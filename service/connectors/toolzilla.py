import logging

from suds.client import Client

from service.soap.request_transport import RequestsTransport
from service.connectors.smdb import Ipam


class ToolzillaAPI(object):
    _location = 'https://toolzilla.cmap.proxy.int.godaddy.com/webservice.php/AccountSearchService'
    _wsdl = _location + '/WSDL'

    def __init__(self, settings):
        self._logger = logging.getLogger(__name__)
        self._ipam = Ipam

        try:
            self.client = Client(self._wsdl, location=self._location,
                                 headers=RequestsTransport.get_soap_headers(),
                                 transport=RequestsTransport(username=settings.CMAP_PROXY_USER,
                                                             password=settings.CMAP_PROXY_PASS,
                                                             cert=settings.CMAP_PROXY_CERT,
                                                             key=settings.CMAP_PROXY_KEY))
        except Exception as e:
            self._logger.error('Unable to initialize WSDL to Toolzilla API: {}'.format(e))

    def _get_hostname_by_guid(self, guid):
        """
        Queries the Toolzilla API for a GUID for a domain name.
        :param guid:
        :return: hostname or None
        """
        hostname = None

        try:
            self._logger.info('Searching for hostname for guid {}'.format(guid))
            data = self.client.service.getHostNameByGuid(guid)
            if data:
                hostname = data.split('.')[0]
        except Exception as e:
            self._logger.error('Unable to lookup hostname for {} : {}'.format(guid, e))
            self._logger.error(self.client.last_received())
        finally:
            return hostname

    def search_by_domain(self, domain, a_record):
        """
        For a given domain name, query Toolzilla to retrieve corresponding hosting guids, shopperIDs, and product.
        :param domain: Domain being searched for, coolexample.com
        :param a_record: A record of the domain being searched for, socket.gethostbyname(domain) completed in hosting_resolver
        :return:
        """

        try:
            # If a client was not instantiated successfully, don't try running a query
            if not hasattr(self, 'client'):
                raise ValueError('ToolzillaAPI object has no attribute: client')

            data = self.client.service.searchByDomain(domain)

            # checks to make sure the returned data is not an error
            if str(type(data)) != "<class 'suds.sax.text.Text'>":
                entry = data[0][0]

                guid = str(entry['AccountUid'][0])
                shopper_id = str(entry['ShopperId'][0])
                product = str(entry['ProductType'][0])
                hostname = self._get_hostname_by_guid(guid)
                ips = self._ipam.get_ips_by_hostname(hostname)

                if a_record not in ips:
                    return None
                elif product == 'wpaas':
                    return {'guid': guid, 'shopper_id': shopper_id, 'product': product, 'os': 'Linux',
                            'hostname': 'Unable to locate', 'data_center': 'Unable to locate'}
                elif product == 'dhs':
                    return {'guid': guid, 'shopper_id': shopper_id, 'product': product, 'os': 'Unable to locate',
                            'hostname': 'Unable to locate', 'data_center': 'Unable to locate'}
                return {'guid': guid, 'shopper_id': shopper_id, 'product': product}

        except Exception as e:
            self._logger.error('Failed Toolzilla Lookup: {}'.format(e))
            if hasattr(self, 'client'):
                self._logger.error(self.client.last_received())
