from csetutils.flask.logging import get_logging
from requests import Session
from requests_ntlm import HttpNtlmAuth
from zeep.client import Client
from zeep.transports import Transport


class Ipam(object):
    """
    This class provides access into the IPAM Soap Service to retrieve and modify data about IP Addresses
    """

    def __init__(self, url, user, password):
        self._logger = get_logging()

        self.session = Session()
        self.session.verify = False
        self.session.auth = HttpNtlmAuth(user, password)
        self.url = url
        self.client = None

    def connect(self):
        transport = Transport(timeout=10, session=self.session)
        self.client = Client(self.url, transport=transport)

    @staticmethod
    def __get_ips(obj):
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

    def __soap_call(self, method, params):
        """
        Perform a SOAP call, and parse the results.
        :param method:
        :param params:
        :return:
        """

        # We need the params to be a tuple, so if it's a single element, cast as a tuple.
        if not isinstance(params, tuple):
            params = (params,)

        try:
            # Dynamically make SOAP call.
            return getattr(self.client.service, method)(*params)
        except Exception as e:
            self._logger.error('Unable to make SOAP call: {}'.format(e))

    @staticmethod
    def __validate_params(params):
        """
        Make sure that all method parameters were supplied.
        :param params:
        :return:
        """
        for key, val in params.items():
            if not val:
                raise Exception('Missing parameter {}'.format(key))

    def get_ips_by_hostname(self, hostname):
        """
        Get IP's assigned to a specific hostname. Returns a list.
        :param hostname:
        :return:
        """
        self.connect()
        Ipam.__validate_params(locals())
        return Ipam.__get_ips(self.__soap_call('GetIPsByHostname', hostname))

    def get_properties_for_ip(self, ip):
        """
        Get details for a specific IP address. Returns a dictionary.
        :param ip:
        :return:
        """
        self.connect()
        Ipam.__validate_params(locals())
        return self.__soap_call('GetPropertiesForIP', ip)
