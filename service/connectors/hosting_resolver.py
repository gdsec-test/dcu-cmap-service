import logging
import socket

from service.connectors.smdb import Ipam
from service.connectors.subscriptions import SubscriptionsAPI
from service.connectors.toolzilla import ToolzillaAPI
from service.products.angelo import AngeloAPI
from service.products.diablo import DiabloAPI
from service.products.go_central import GoCentralAPI
from service.products.mwp_one import MWPOneAPI
from service.products.mwp_two import MWPTwoAPI
from service.products.vertigo import VertigoAPI
from service.utils.hostname_parser import parse_hostname


class HostingProductResolver(object):
    '''
    HostingProductResolver is responsible for determining any hosting products that might be associated
    with the provided domain name. It utilizes a variety of methods, subscriptions API, Toolzilla, etc. to achieve this.
    '''

    def __init__(self, config):
        self._logger = logging.getLogger(__name__)
        self.ipam = Ipam(config.SMDB_URL, config.SMDB_USER, config.SMDB_PASS)
        self.vertigo_api = VertigoAPI(config)
        self.diablo_api = DiabloAPI(config)
        self.angelo_api = AngeloAPI(config)
        self.toolzilla_api = ToolzillaAPI(config)
        self.mwp1_api = MWPOneAPI(config)
        self.mwp2_api = MWPTwoAPI()
        self.gocentral_api = GoCentralAPI(config)
        self.subscriptions_api = SubscriptionsAPI(config)

    def get_properties_for_domain(self, domain, shopper_id):
        '''
        Given a domain name and a shopperID, attempt to determine all related hosted information, or none if the
        domain is not hosted with GoDaddy.
        :param domain:
        :param shopper_id:
        :return:
        '''
        try:
            ip = socket.gethostbyname(domain)
            ipam = self.ipam.get_properties_for_ip(ip)

        except Exception as e:
            self._logger.error(e)
            return None

        if hasattr(ipam, 'HostName'):
            ipam_hostname = getattr(ipam, 'HostName')
            # First check if the host details can be retrieved using the subscriptions API
            # If not, fall back on the existing way to retrieve host details.
            subscription = self.subscriptions_api.get_hosting_subscriptions(shopper_id, domain)
            if subscription:
                self._logger.info('Successfully retrieved subscriptions info for domain: {}'.format(domain))
                product_dict = self._guid_locater(subscription.get('product', {}).get('namespace'), domain)
                if product_dict:
                    return {'hostname': ipam_hostname, 'data_center': None, 'os': product_dict.get('os'),
                            'product': subscription.get('product', {}).get('product_name'),
                            'ip': ip, 'guid': product_dict.get('guid'),
                            'shopper_id': product_dict.get('shopper_id'),
                            'created_date': product_dict.get('created_date'),
                            'friendly_name': product_dict.get('friendly_name'),
                            'private_label_id': product_dict.get('private_label_id')}

            if ipam_hostname is None:
                data = self.toolzilla_api.search_by_domain(domain)
                # if data comes back as None, set it to a dict so get() can be run on it
                if data is None:
                    data = {}
                if data.get('product') == 'wpaas':
                    return self.mwp1_api.locate(domain)
                else:
                    return {'dc': data.get('dc'), 'os': data.get('os'),
                            'product': data.get('product'),
                            'ip': ip, 'guid': data.get('guid'), 'shopper_id': data.get('shopper_id'),
                            'hostname': data.get('hostname'), 'created_date': data.get('created_date'),
                            'friendly_name': data.get('friendly_name')}

            else:
                data = parse_hostname(ipam_hostname)
                if len(data) < 3 or data[2] != 'Not Hosting':
                    d = self._guid_locater(data[2], domain)
                    gc_dict = self.gocentral_api.locate(domain)
                    if d:
                        return {'hostname': ipam_hostname, 'data_center': data[0], 'os': d.get('os'),
                                'product': data[2], 'ip': ip, 'guid': d.get('guid'),
                                'shopper_id': d.get('shopper_id'), 'created_date': d.get('created_date'),
                                'friendly_name': d.get('friendly_name'),
                                'private_label_id': d.get('private_label_id')}

                    # Check if domain is hosted on MWP2.0 and if so sending back return with MWP2.0 as product
                    elif self.mwp2_api.locate(domain):
                        host_product = 'MWP 2.0'

                    # Check if domain is hosted on GoCentral and if so sending back return with GoCentral as product
                    elif gc_dict:
                        gc_dict.update({'hostname': ipam_hostname, 'data_center': data[0], 'os': data[1],
                                        'ip': ip, 'friendly_name': None})
                        return gc_dict

                    else:
                        self._logger.error('_guid_locater failed on: {}'.format(domain))
                        host_product = data[2]

                    return {'hostname': ipam_hostname, 'data_center': data[0], 'os': data[1], 'product': host_product,
                            'ip': ip, 'guid': None, 'shopper_id': None, 'created_date': None, 'friendly_name': None}

                else:
                    return 'No hosting product found'

    def _guid_locater(self, product, domain):
        '''
        Based on a particular product, further query product specific domains to narrow down and enhance the
        information that can be returned.
        :param product:
        :param domain:
        :return:
        '''
        if product == 'Vertigo':
            return self.vertigo_api.locate(domain)
        elif product == 'Diablo':
            result = self.diablo_api.locate(domain)
            if result is not None:
                return result
        elif product == 'Angelo':
            result = self.angelo_api.locate(domain)
            if result is not None:
                return result
        return self.toolzilla_api.search_by_domain(domain)
