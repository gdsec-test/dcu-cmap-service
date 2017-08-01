import datetime
import json
import logging
import re
import threading
from datetime import datetime, timedelta
from urllib import urlopen
from dns import resolver, reversename
from ipwhois import IPWhois
from netaddr.ip import all_matching_cidrs
from whois import NICClient, whois
from whois.parser import PywhoisError, WhoisEntry
from functions import return_expected_dict_due_to_exception


class ASNPrefixes(object):
    """
    Utility class for determining if a given ip address is part of an ASN's
    announced prefixes. This class maintains an internal list of prefixes
    for the given ASN that will be updated every update_hrs hours
    """

    def __init__(self, asn=26496, update_hrs=24):
        self._logger = logging.getLogger(__name__)
        self._asn = asn
        self._last_query = datetime(1970, 1, 1)
        self._url_base = 'https://stat.ripe.net/data/announced-prefixes/data.json?resource=AS'
        self._update_hrs = update_hrs
        self._prefixes = []
        self._update_lock = threading.RLock()
        threading.Thread(target=self._ripe_get_prefixes_per_asn).start()

    def get_network_for_ip(self, ipaddr):
        """
        Returns a list of networks that ipaddr exists in based on
        the announced prefixes for the given ASN
        NOTE: Based on update_hrs, this call may block while an up
        to date list is being retrieved
        """
        with self._update_lock:
            try:
                if self._last_query < datetime.utcnow() - timedelta(
                        hours=self._update_hrs):
                    self._logger.info("Updating prefix list for ASN{}".format(self._asn))
                    self._ripe_get_prefixes_per_asn()
                return all_matching_cidrs(ipaddr, self._prefixes)
            except Exception as e:
                self._logger.error('Exception in _update_lock(): {}'.format(e.message))
                return []

    def _ripe_get_prefixes_per_asn(self):
        """
        Uses RIPE's API (https://stat.ripe.net/data/announced-prefixes/data.?)
        to list the prefixes associated to a given Autonomous System Number (ASN)

        e.g., e.g. https://stat.ripe.net/data/announced-prefixes/data.json?resource=AS3333&starttime=2011-12-12T12:00

        This API is documented on https://stat.ripe.net/docs/data_api
        """
        with self._update_lock:
            try:
                query_time = datetime.utcnow()
                rep = urlopen(self._url_base + str(self._asn) + '&starttime=' +
                              query_time.isoformat().split('.')[0])
                data = str(rep.read().decode(encoding='UTF-8'))
                rep.close()
                js_data = json.loads(data)
                pref_list = []

                for record in js_data['data']['prefixes']:
                    pref_list.append(record['prefix'])
                # If prefix list is empty, don't overwrite _prefixes nor update _last_query time
                if len(pref_list) == 0:
                    raise ValueError('Currently obtained Prefix List is empty.')
                self._prefixes = pref_list
                self._last_query = query_time
            except Exception as e:
                self._logger.error(
                    "Unable to update the prefix list. Last update at {}:{}".format(
                        self._last_query, e))


class WhoisQuery(object):

    REDIS_DATA_KEY = 'result'

    def __init__(self, config, redis_obj):
        self._redis = redis_obj
        self.date_format = config.DATE_FORMAT
        self._asn = ASNPrefixes()
        self._logger = logging.getLogger(__name__)

    def is_ip(self, source_domain_or_ip):
        """
        Returns whether the given sourceDomainOrIp is an ip address
        :param source_domain_or_ip:
        :return:
        """
        pattern = re.compile(r"((([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])[ (\[]?(\.|dot)[ )\]]?){3}[0-9]{1,3})")
        return pattern.match(source_domain_or_ip) is not None

    def get_ip_from_domain(self, domain_name):
        dnsresolver = resolver.Resolver()
        dnsresolver.timeout = 1
        dnsresolver.lifetime = 1
        try:
            return dnsresolver.query(domain_name, 'A')[0].address
        except Exception as e:
            logging.error("Unable to get ip for %s : %s", domain_name, e.message)

    def get_domain_from_ip(self, ip):
        dnsresolver = resolver.Resolver()
        addr = reversename.from_address(ip)
        dnsresolver.timeout = 1
        dnsresolver.lifetime = 1
        try:
            return dnsresolver.query(addr, 'PTR')[0].to_text().rstrip('.').encode('idna')
        except Exception as e:
            logging.error("Unable to get domain for %s : %s", ip, e.message)

    def get_hosting_info(self, domain_name):
        """
        Return hosting network and email
        :param domain_name:
        :return:
        """
        email_list = []
        query_value = {}
        try:
            if domain_name is None or domain_name == '':
                raise ValueError('Blank domain name was provided')
            redis_record_key = u'{}-ip_whois_info'.format(domain_name)
            query_value = self._redis.get_value(redis_record_key)
            if query_value is None:
                if domain_name is not str:
                    domain_name = domain_name.encode('idna')
                if self.is_ip(domain_name):
                    ip = domain_name
                else:
                    ip = self.get_ip_from_domain(domain_name)
                query_value = dict(ip=ip)
                if self._check_hosted_here(ip):
                    query_value['name'] = 'GoDaddy.com LLC'
                    query_value['email'] = ['abuse@goaddy.com']
                    self._redis.set_value(redis_record_key, json.dumps({self.REDIS_DATA_KEY: query_value}))
                    return query_value
                self._logger.info("Resorting to IPWhois lookup for {}".format(ip))
                info = IPWhois(ip).lookup_rdap()
                query_value['name'] = info.get('network').get('name')
                for k, v in info['objects'].iteritems():
                    email_address = v['contact']['email']
                    if email_address:
                        for i in email_address:
                            email_list.append(i['value'])
                query_value['email'] = email_list
                self._redis.set_value(redis_record_key, json.dumps({self.REDIS_DATA_KEY: query_value}))
            else:
                query_value = json.loads(query_value).get(self.REDIS_DATA_KEY)
        except Exception as e:
            self._logger.error("Error in getting the hosting whois info for %s : %s", domain_name, e.message)
            # If exception occurred before query_value had completed assignment, set keys to None
            query_value = return_expected_dict_due_to_exception(query_value, ['name', 'email', 'ip'])
        return query_value

    def _check_hosted_here(self, ip):
        """
        Check the ip address against the asn announced prefixes then check
        the reverse dns for secureserver.net
        """
        if self._asn.get_network_for_ip(ip):
            self._logger.info("{} hosted info found in advertised prefixes".format(ip))
            return True
        else:
            # Not sure if this will ever return true if the above is False
            reverse_dns = self.get_domain_from_ip(ip)
            if reverse_dns is not None and 'secureserver.net' in reverse_dns:
                self._logger.info("{} hosted info found in reverse dns".format(ip))
                return True
            return False

    def get_registrar_info(self, domain_name):
        """
        Return registrar network, domain create date and email
        :param domain_name:
        :return:
        """
        query_value = {}
        try:
            if domain_name is None or domain_name == '':
                raise ValueError('Blank domain name was provided')
            redis_record_key = u'{}-registrar_whois_info'.format(domain_name)
            query_value = self._redis.get_value(redis_record_key)
            if query_value is None:
                # Try godaddy first
                try:
                    query = WhoisEntry.load(domain_name, NICClient().whois(domain_name, 'whois.godaddy.com', True))
                    if query.registrar:
                        query.registrar = 'GoDaddy.com, LLC'
                        query.emails = ['abuse@godaddy.com']
                    else:
                        # If query.registrar is None, go for the alternate whois query
                        raise PywhoisError
                except PywhoisError:
                    query = whois(domain_name)
                    if isinstance(query.emails, basestring):
                        query.emails = [query.emails]
                query_value = dict(name=query.registrar, email=query.emails)
                create_date = query.creation_date[0] if isinstance(query.creation_date, list) else query.creation_date
                create_date = create_date.strftime(self.date_format) if create_date and  \
                    isinstance(create_date, datetime) else None
                query_value['create_date'] = create_date
                self._redis.set_value(redis_record_key, json.dumps({self.REDIS_DATA_KEY: query_value}))
            else:
                query_value = json.loads(query_value).get(self.REDIS_DATA_KEY)
        except Exception as e:
            logging.error("Error in getting the registrar whois info for %s : %s", domain_name, e.message)
            # If exception occurred before query_value had completed assignment, set keys to None
            query_value = return_expected_dict_due_to_exception(query_value, ['name', 'email', 'create_date'])
        return query_value
