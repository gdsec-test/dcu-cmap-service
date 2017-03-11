import json
import socket
import logging
import datetime
from whois import whois

from ipwhois import IPWhois


class WhoisQuery(object):

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
        query_value = None
        try:
            redis_key = '{}-ip_whois_info'.format(domain_name)
            query_value = self._redis.get_value(redis_key)
            if query_value is None:
                domain_name = 'www.' + domain_name if domain_name[:4] != 'www.' else domain_name[4:]
                ip = socket.gethostbyname(domain_name)
                info = IPWhois(ip).lookup_rdap()
                for k, v in info['objects'].iteritems():
                    email_address = v['contact']['email']
                    if email_address:
                        for i in email_address:
                            email_list.append(i['value'])
                query_value = dict(name=info.get('network').get('name'), email=email_list)
                self._redis.set_value(redis_key, json.dumps({'result': query_value}))
            else:
                query_value = json.loads(query_value).get('result')
        except Exception as e:
            logging.warning("Error in getting the hosting whois info for %s : %s", domain_name, e.message)
        return query_value

    def get_registrar_info(self, domain_name):
        """
        Return registrar network, domain create date and email
        :param domain_name:
        :return:
        """
        query_value = None
        try:
            redis_key = '{}-registrar_whois_info'.format(domain_name)
            query_value = self._redis.get_value(redis_key)
            if query_value is None:
                query = whois(domain_name)
                if type(query.creation_date[0]) == datetime.datetime:
                    create_date = query.creation_date[0].strftime(self.date_format)
                else:
                    create_date = 'A datetime object was not returned for creation_date'
                query_value = dict(name=query.registrar, create_date=create_date, email=query.emails)
                self._redis.set_value(redis_key, json.dumps({'result': query_value}))
            else:
                query_value = json.loads(query_value).get('result')
        except Exception as e:
            logging.warning("Error in getting the registrar whois info for %s : %s", domain_name, e.message)
        return query_value
