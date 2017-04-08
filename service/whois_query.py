import json
import socket
import logging
import datetime
import re
from whois import whois, NICClient
from whois.parser import WhoisEntry, PywhoisError
from dns import resolver, reversename
from ipwhois import IPWhois
from functions import return_expected_dict_due_to_exception


class WhoisQuery(object):

    REDIS_DATA_KEY = 'result'

    def __init__(self, config, redis_obj):
        self._redis = redis_obj
        self.date_format = config.DATE_FORMAT

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
            logging.error("Error in getting the hosting whois info for %s : %s", domain_name, e.message)
            # If exception occurred before query_value had completed assignment, set keys to None
            query_value = return_expected_dict_due_to_exception(query_value, ['name', 'email', 'ip'])
        return query_value

    def _check_hosted_here(self, ip):
        reverse_dns = self.get_domain_from_ip(ip)
        return reverse_dns is not None and 'secureserver.net' in reverse_dns

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
                    else:
                        # If query.registrar is None, go for the alternate whois query
                        raise PywhoisError
                except PywhoisError:
                    query = whois(domain_name)
                query_value = dict(name=query.registrar, email=query.emails)
                create_date = query.creation_date[0] if isinstance(query.creation_date, list) else query.creation_date
                create_date = create_date.strftime(self.date_format) if create_date and  \
                    isinstance(create_date, datetime.datetime) else None
                query_value['create_date'] = create_date
                self._redis.set_value(redis_record_key, json.dumps({self.REDIS_DATA_KEY: query_value}))
            else:
                query_value = json.loads(query_value).get(self.REDIS_DATA_KEY)
        except Exception as e:
            logging.error("Error in getting the registrar whois info for %s : %s", domain_name, e.message)
            # If exception occurred before query_value had completed assignment, set keys to None
            query_value = return_expected_dict_due_to_exception(query_value, ['name', 'email', 'create_date'])
        return query_value
