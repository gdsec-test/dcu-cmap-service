import json
import socket
import logging
import datetime
from whois import whois, NICClient 
from whois.parser import WhoisEntry, PywhoisError

from ipwhois import IPWhois
from functions import return_expected_dict_due_to_exception


class WhoisQuery(object):

    REDIS_DATA_KEY = 'result'

    def __init__(self, config, redis_obj):
        self._redis = redis_obj
        self.date_format = config.DATE_FORMAT

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
            redis_record_key = '{}-ip_whois_info'.format(domain_name)
            query_value = self._redis.get_value(redis_record_key)
            if query_value is None:
                try:
                    ip = socket.gethostbyname(domain_name)
                except Exception as e:
                    domain_name = 'www.' + domain_name if domain_name[:4] != 'www.' else domain_name[4:]
                    ip = socket.gethostbyname(domain_name)
                query_value = dict(ip=ip)
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
            redis_record_key = '{}-registrar_whois_info'.format(domain_name)
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
