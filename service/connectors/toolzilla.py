import logging

from suds.client import Client

from service.soap.request_transport import RequestsTransport


class ToolzillaAPI(object):
    _location = 'https://toolzilla.cmap.proxy.int.godaddy.com/webservice.php/AccountSearchService'
    _wsdl = _location + '/WSDL'

    def __init__(self, settings, ipam_obj):
        self._logger = logging.getLogger(__name__)
        self._ipam = ipam_obj

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
        :param a_record: A record of the domain being searched for, socket.gethostbyname(domain), from hosting_resolver
        :return:
        """
        ips = None
        no_loc = 'Unable to locate'
        payload = dict()
        try:
            # Verify we were provided required arguments
            if not domain:
                raise TypeError('Type for "domain" is None but should be String')
            if not a_record:
                raise TypeError('Type for "a_record" is None but should be String')
            # If a client was not instantiated successfully, don't try running a query
            if not hasattr(self, 'client'):
                raise ValueError('ToolzillaAPI object has no attribute: client')

            data = self.client.service.searchByDomain(domain)

            # checks to make sure the returned data is not an error
            if str(type(data)) != "<class 'suds.sax.text.Text'>":
                entry = data[0][0]

                payload['guid'] = str(entry['AccountUid'][0])
                payload['shopper_id'] = str(entry['ShopperId'][0])
                payload['product'] = str(entry['ProductType'][0])
                if payload.get('guid'):
                    payload['hostname'] = self._get_hostname_by_guid(payload['guid'])
                    if payload.get('hostname'):
                        """
                        Wrapping call to get_ips_by_hostname() because an exception will cause this method to return
                        'None' even though it may have already determined guid, shopper_id, product and hostname
                        """
                        try:
                            ips = self._ipam.get_ips_by_hostname(payload['hostname'])
                        except Exception as e:
                            self._logger.error(
                                'Unable to determine IPs for hostname {}: {}'.format(payload['hostname'], e))
                else:
                    # If no guid was determined, then there is no useful information to return, so bail
                    return None

                # If we're unable to determine any IPs for a host, then we will still return any values obtained, but
                #  if the IPs are determined, the provided a_record must be contained within it, or return None
                if ips and a_record not in ips:
                    return None
                elif payload.get('product') == 'wpaas':
                    payload.update({'os': 'Linux', 'hostname': no_loc, 'data_center': no_loc})
                elif payload.get('product') == 'dhs':
                    payload.update({'os': no_loc, 'hostname': no_loc, 'data_center': no_loc})
                return payload

        except Exception as e:
            self._logger.error('Failed Toolzilla Lookup: {}'.format(e))
            if hasattr(self, 'client'):
                self._logger.error(self.client.last_received())
