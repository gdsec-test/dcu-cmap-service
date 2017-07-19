from pathos.multiprocessing import ProcessingPool as Pool
from itertools import product
from diablo_api import DiabloApi
from vertigo_api import VertigoApi
from angelo_api import AngeloApi
from tz_api import ToolzillaApi
from suds.client import Client
from suds.sax.element import Element
from suds import WebFault
import ssl
from enrichment import nutrition_label
import logging
from suds.transport.https import WindowsHttpAuthenticated
from urllib2 import URLError
import socket



class SearchAll(object):

    def __init__(self, config):
        self.tz_pass = config.TOOLZILLAPASS
        self.vrun = VertigoApi(config)
        self.drun = DiabloApi(config)
        self.arun = AngeloApi(config)
        self.trun = ToolzillaApi(config)

    def run_guid(self, data):
        env = data[0]
        domain = data[1]
        if env == 'vertigo':
            return self.vrun.guid_query(domain)
        elif env == 'diablo':
            return self.drun.guid_query(domain)
        elif env == 'angelo':
            return self.arun.guid_query(domain)
        elif env == 'tz':
            return self.guid_query(domain)

    def get_hostname_tz(self, guid):
        url = 'https://toolzilla.int.godaddy.com/webservice.php/AccountSearchService/WSDL'
        user = 'svc_dcu'
        pwd = self.tz_pass

        if pwd is not None:

            auth_head = Element('acc:Authentication User="' + user + '" Password="' + pwd + '"')
            ssl._create_default_https_context = ssl._create_unverified_context

            client = Client(url)
            client.set_options(soapheaders=auth_head)

        else:
            print 'no tz password passed'

        try:

            hostname = client.service.getHostNameByGuid(guid)
            hostname = hostname.split('.')[0]
            hostname = hostname.lower()

            enrichment = nutrition_label(hostname)
            dc = enrichment[0]
            os = enrichment[1]
            product = enrichment[2]

            data = [dc, os, product]

            return data

        except Exception as e:
            print str(e)
            print client.last_received()

    def guid_query(self, domain):
        """
        Queries the Toolzilla API for a GUID for a domain name.
        :param domain:
        :return: GUID or None
        """
        url = 'https://toolzilla.int.godaddy.com/webservice.php/AccountSearchService/WSDL'
        user = 'svc_dcu'
        pwd = self.tz_pass

        if pwd is not None:

            auth_head = Element('acc:Authentication User="' + user + '" Password="' + pwd + '"')
            ssl._create_default_https_context = ssl._create_unverified_context

            client = Client(url)
            client.set_options(soapheaders=auth_head)

        else:
            print 'no tz password passed'

        try:
            data = client.service.searchByDomain(domain)
            # checks to make sure the returned data is not an error
            if str(type(data)) != "<class 'suds.sax.text.Text'>":
                logging.info('Domain searched for: %s', domain)
                hosting_guid = str(data[0][0][2][0])
                return hosting_guid

            return None

        except Exception as e:
            logging.error(e.message)
            logging.error(client.last_received())
            return None

    def setrun(self, domain):
        pool = Pool()
        data = []
        try:
            result = pool.map(self.run_guid, [x for x in product(*[['angelo', 'vertigo', 'diablo', 'tz'], [domain]])])
            env = [self.get_hostname_tz(x) for x in result if x]
            result = filter(lambda x: x is not None, result)
            for x in env[0]:
                data.append(x)

            data.append(result[0])

        except Exception as e:
            print str(e)

        finally:
            pool.close()
            pool.join()
            return data


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
        except (WebFault, URLError) as e:
            try:
                raise Exception("IPAM SOAP Fault: %s" % e.fault.faultstring)
            except AttributeError as e2:
                raise Exception("IPAM SOAP Attribute Fault: %s" % str(e2))

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
        if ipam['HostName']:
            data = nutrition_label(ipam['HostName'])
            if data[2] != 'Not Hosting':
                d = self._guid_locater(data[2], domain)
                return {'hostname': ipam['HostName'], 'dc': data[0], 'os': d['os'], 'product': data[2], 'ip': ip,
                            'guid': d['guid'], 'shopper': d['shopper']}
            else:
                return 'No hosting product found'
        elif ipam['HostName'] is None:
            data = self.trun.guid_query(domain)
            return {'dc': data['dc'], 'os': data['os'], 'product': data['product'], 'ip': ip, 'guid': data['guid'],
                    'shopper': data['shopper'], 'hostname': data['hostname']}
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
