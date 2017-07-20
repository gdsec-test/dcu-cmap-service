from diablo_api import DiabloApi
from vertigo_api import VertigoApi
from angelo_api import AngeloApi
from tz_api import ToolzillaApi
from suds.client import Client
from suds import WebFault
from enrichment import nutrition_label
import logging
from suds.transport.https import WindowsHttpAuthenticated
from urllib2 import URLError
import socket


class Ipam(object):

    # This method is called automatically when this class is instantiated.
    def __init__(self, config):

        self.smdbUsername = config.TOOLZILLAUSER
        self.smdbPassword = config.TOOLZILLAPASS
        self.tz_pass = config.TOOLZILLAPASS
        self.vrun = VertigoApi(config)
        self.drun = DiabloApi(config)
        self.arun = AngeloApi(config)
        self.trun = ToolzillaApi(config)

        self.url = config.SMDB_URL

        # Create the NTLM authentication object.
        self.ntlm = WindowsHttpAuthenticated(username=self.smdbUsername, password=self.smdbPassword)

        # Set the logging for SUDS to only critical. We don't care about anything less.
        logging.disable(logging.CRITICAL)

        # Create the SUDS SOAP client.
        self.client = Client(self.url, transport=self.ntlm)

        # Create lookup object dictionary
        # self.ctx = {vertigo}

    # Convert the string "true" and "false" to boolean.
    def __get_boolean(self, obj):
        # Make sure the object is a string.
        if isinstance(obj, basestring):
            if obj.lower() == 'false':
                return False
            elif obj.lower() == 'true':
                return True

        raise Exception('Could not determine boolean value: %s' % obj)

    # Get a list of IP addresses from an object. This is specific to the IPAM IP SOAP response.
    def __get_ips(self, obj):
        # Default to empty list.
        ips = []

        # Make sure the object is a list, and contains a 'IPAddress' key.
        if obj is not None and hasattr(obj, '__iter__') and 'IPAddress' in obj:
            # If the object is a list already, just return it.
            if isinstance(obj['IPAddress'], list):
                ips = obj['IPAddress']
            # If the object is a dictionary, cast as a list.
            elif isinstance(obj['IPAddress'], dict):
                ips.append(obj['IPAddress'])

        return ips

    # Perform a SOAP call, and parse the results.
    def __soap_call(self, method, params, responseKey):
        # We need the params to be a tuple for Suds. So if it's a single element, cast as a tuple.
        if not isinstance(params, tuple):
            params = (params,)

        # Try and make the SOAP call, and return the results. Or throw an exception on any SOAP faults.
        try:
            # Dynamically make SOAP call.
            soapResult = getattr(self.client.service, method)(*params)

            # Manually parse the SOAP XML response.
            return soapResult
        except Exception as e:
            logging.error(e.message)
            return None

    # Make sure all method parameters were supplied. The only exception is 'vlan', which is optional.
    def __validate_params(self, params):
        for key, val in params.iteritems():
            if val is None and key != 'vlan':
                raise Exception('Missing parameter %s' % key)

    # Get IP's assigned to a specific hostname. Returns a list.
    def get_ips_by_hostname(self, hostname):
        self.__validate_params(locals())
        return self.__get_ips(self.__soap_call('GetIPsByHostname', hostname, 'GetIPsByHostnameResult'))

    # Get details for a specific IP address. Returns a dictionary.
    def get_properties_for_ip(self, domain):

        ip = socket.gethostbyname(domain)
        self.__validate_params(locals())
        ipam = self.client.service.GetPropertiesForIP(ip, transport=self.ntlm)
        if ipam.get('HostName'):
            data = nutrition_label(ipam['HostName'])
            if data[2] != 'Not Hosting':
                d = self._guid_locater(data[2], domain)
                if d:
                    return {'hostname': ipam.get('HostName'), 'dc': data[0], 'os': d.get('os'), 'product': data[2], 'ip': ip,
                            'guid': d.get('guid'), 'shopper': d.get('shopper')}
                else:
                    logging.error('_guid_locater failed on: %s' % domain)
            else:
                return 'No hosting product found'
        elif ipam['HostName'] is None:
            data = self.trun.guid_query(domain)
            return {'dc': data.get('dc'), 'os': data.get('os'), 'product': data.get('product'), 'ip': ip,
                    'guid': data.get('guid'), 'shopper': data.get('shopper'), 'hostname': data.get('hostname')}
        else:
            return None

    def _guid_locater(self, product, domain):

        if product == 'Vertigo':
            return self.vrun.guid_query(domain)
        elif product == 'Diablo':
            return self.drun.guid_query(domain)
        elif product == 'Angelo':
            return self.arun.guid_query(domain)
        else:
            return self.trun.guid_query(domain)
