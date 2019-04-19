import logging

from requests import Session

from requests_ntlm import HttpNtlmAuth
from zeep.client import Client
from zeep.transports import Transport


class Ipam(object):
    '''
    This class provides access into the IPAM Soap Service to retrieve and modify data about IP Addresses
    '''

    def __init__(self, url, user, password):
        self._logger = logging.getLogger(__name__)

        session = Session()
        session.verify = False
        session.auth = HttpNtlmAuth(user, password)
        transport = Transport(timeout=10, session=session)

        self.client = Client(url, transport=transport)

    def __get_ips(self, obj):
        """
        Get a list of IP Addresses from an object
        :param obj:
        :return:
        """
        ips = []

        if obj and isinstance(obj, list):
            for response in obj:
                ips.append(response['Address'])

        return ips

    def __soap_call(self, method, params, response_key):
        '''
        Perform a SOAP call, and parse the results.
        :param method:
        :param params:
        :param response_key:
        :return:
        '''

        # We need the params to be a tuple, so if it's a single element, cast as a tuple.
        if not isinstance(params, tuple):
            params = (params,)

        try:
            # Dynamically make SOAP call.
            return getattr(self.client.service, method)(*params)
        except Exception as e:
            self._logger.error('Unable to make SOAP call: {}'.format(e))

    def __validate_params(self, params):
        '''
        Make sure that all method parameters were supplied.
        :param params:
        :return:
        '''
        for key, val in params.items():
            if not val:
                raise Exception('Missing parameter {}'.format(key))

    def get_ips_by_hostname(self, hostname):
        '''
        Get IP's assigned to a specific hostname. Returns a list.
        :param hostname:
        :return:
        '''
        self.__validate_params(locals())
        s = self.__soap_call('GetIPsByHostname', hostname, 'GetIPsByHostnameResult')
        return self.__get_ips(self.__soap_call('GetIPsByHostname', hostname, 'GetIPsByHostnameResult'))

    def get_properties_for_ip(self, ip):
        '''
        Get details for a specific IP address. Returns a dictionary.
        :param ip:
        :return:
        '''
        self.__validate_params(locals())
        return self.__soap_call('GetPropertiesForIP', ip, 'GetPropertiesForIPResult')
