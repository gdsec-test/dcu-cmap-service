import logging
import socket

from suds.client import Client
from suds.transport.https import WindowsHttpAuthenticated

from angelo_api import AngeloApi
from diablo_api import DiabloApi
from enrichment import nutrition_label
from gocentral import GoCentral
from mwpone_api import MwpOneApi
from mwptwo import MwpTwo
from tz_api import ToolzillaApi
from vertigo_api import VertigoApi


class Ipam(object):
    # This method is called automatically when this class is instantiated.
    def __init__(self, config):
        self._logger = logging.getLogger(__name__)
        self.vertigo_api = VertigoApi(config)
        self.diablo_api = DiabloApi(config)
        self.angelo_api = AngeloApi(config)
        self.toolzilla_api = ToolzillaApi(config)
        self.mwp1_api = MwpOneApi(config)
        self.mwp2_api = MwpTwo(config)
        self.gocentral_api = GoCentral(config)

        # Create the NTLM authentication object.
        self.ntlm = WindowsHttpAuthenticated(username=config.SMDB_USER, password=config.SMDB_PASS)
        self.client = Client(config.SMDB_URL, transport=self.ntlm)  # Create the SUDS SOAP client.

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

            return soapResult
        except Exception as e:
            self._logger.error(e.message)
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

        try:
            ipam = self.client.service.GetPropertiesForIP(ip, transport=self.ntlm)

        except Exception as e:
            self._logger.error(e.message)
            return None

        if hasattr(ipam, 'HostName'):
            ipam_hostname = getattr(ipam, 'HostName')
            if ipam_hostname is None:
                data = self.toolzilla_api.guid_query(domain)
                # if data comes back as None, set it to a dict so get() can be run on it
                if data is None:
                    data = {}
                if data.get('product') == 'wpaas':
                    return self.mwp1_api.mwpone_locate(domain)
                else:
                    return {'dc': data.get('dc', None), 'os': data.get('os', None),
                            'product': data.get('product', None),
                            'ip': ip, 'guid': data.get('guid', None), 'shopper': data.get('shopper', None),
                            'hostname': data.get('hostname', None), 'created_date': data.get('created_date', None),
                            'friendly_name': data.get('friendly_name', None)}

            else:
                data = nutrition_label(ipam_hostname)
                if len(data) < 3 or data[2] != 'Not Hosting':
                    d = self._guid_locater(data[2], domain)
                    gc_dict = self.gocentral_api.is_gocentral(domain)
                    if d:
                        return {'hostname': ipam_hostname, 'data_center': data[0], 'os': d.get('os', None),
                                'product': data[2], 'ip': ip, 'guid': d.get('guid', None),
                                'shopper_id': d.get('shopper_id', None), 'created_date': d.get('created_date', None),
                                'friendly_name': d.get('friendly_name', None)}

                    # Check if domain is hosted on MWP2.0 and if so sending back return with MWP2.0 as product
                    elif self.mwp2_api.is_mwp2(domain):
                        host_product = 'MWP 2.0'

                    # Check if domain is hosted on GoCentral and if so sending back return with GoCentral as product
                    elif gc_dict:
                        gc_dict.update({'hostname': ipam_hostname, 'data_center': data[0], 'os': data[1],
                                        'ip': ip, 'friendly_name': None})
                        return gc_dict

                    else:
                        self._logger.error('_guid_locater failed on: %s' % domain)
                        host_product = data[2]

                    return {'hostname': ipam_hostname, 'data_center': data[0], 'os': data[1], 'product': host_product,
                            'ip': ip, 'guid': None, 'shopper_id': None, 'created_date': None, 'friendly_name': None}

                else:
                    return 'No hosting product found'
        else:
            return None

    def _guid_locater(self, product, domain):
        if product == 'Vertigo':
            return self.vertigo_api.guid_query(domain)
        elif product == 'Diablo':
            result = self.diablo_api.guid_query(domain)
            if result is not None:
                return result
        elif product == 'Angelo':
            result = self.angelo_api.guid_query(domain)
            if result is not None:
                return result
        return self.toolzilla_api.guid_query(domain)
