import logging

from suds.client import Client

from enrichment import nutrition_label
from request_transport import RequestsTransport


class ToolzillaApi(object):
    """
    Uses the AbsGUID interface. Class is used to look up a GUID in the Toolzilla API given a domain name.
    """
    _LOCATION = 'https://toolzilla.cmap.proxy.int.godaddy.com/webservice.php/AccountSearchService'
    _WSDL = _LOCATION + '/WSDL'

    def __init__(self, settings):
        self._logger = logging.getLogger(__name__)
        try:
            self.client = Client(self._WSDL, location=self._LOCATION,
                                 headers=RequestsTransport.get_soap_headers(),
                                 transport=RequestsTransport(username=settings.CMAP_PROXY_USER,
                                                             password=settings.CMAP_PROXY_PASS,
                                                             cert=settings.CMAP_PROXY_CERT,
                                                             key=settings.CMAP_PROXY_KEY))
        except Exception as e:
            self._logger.error("Failed Toolzilla Client Init: %s", e.message)

    def _hostname_query(self, guid):
        """
        Queries the Toolzilla API for a GUID for a domain name.
        :param guid:
        :return: hostname or None
        """
        try:
            data = self.client.service.getHostNameByGuid(guid)
            # checks to make sure the returned data is not an error
            if data:
                self._logger.info('guid searched for: %s', guid)
                hostname = data.split('.')[0]
                return hostname

        except Exception as e:
            self._logger.error("Failed Toolzilla Lookup: %s", e.message)
            self._logger.error(self.client.last_received())
        return None

    def guid_query(self, domain):
        """
        Queries the Toolzilla API for a GUID for a domain name.
        :param domain:
        :return: GUID or None
        """
        try:
            # If a client wasnt instantiated successfully, dont try running a query
            if not hasattr(self, 'client'):
                raise ValueError('ToolzillaApi object has no attribute: client')
            data = self.client.service.searchByDomain(domain)
            # checks to make sure the returned data is not an error
            if str(type(data)) != "<class 'suds.sax.text.Text'>":

                self._logger.info('Domain searched for: %s', domain)
                shopper_id = str(data[0][0]['ShopperId'][0])
                hosting_guid = str(data[0][0]['AccountUid'][0])
                product = str(data[0][0]['ProductType'][0])
                if product == 'wpaas':
                    return {'guid': hosting_guid, 'shopper_id': shopper_id, 'product': product, 'os': 'Linux',
                            'hostname': 'Unable to locate', 'data_center': 'Unable to locate'}
                elif product == 'dhs':
                    return {'guid': hosting_guid, 'shopper_id': shopper_id, 'product': product, 'os': 'Unable to locate',
                            'hostname': 'Unable to locate', 'data_center': 'Unable to locate'}
                else:
                    hostname = self._hostname_query(hosting_guid)
                    extra = nutrition_label(hostname)
                    os = extra[1]
                    dc = extra[0]
                    product = extra[2]
                    return {'guid': hosting_guid, 'shopper_id': shopper_id, 'product': product, 'os': os,
                            'hostname': hostname, 'data_center': dc}

        except Exception as e:
            self._logger.error("Failed Toolzilla Lookup: %s", e.message)
            if hasattr(self, 'client'):
                self._logger.error(self.client.last_received())

        return None
