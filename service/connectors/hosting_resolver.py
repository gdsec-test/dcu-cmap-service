import logging
import socket
from collections import OrderedDict

from service.connectors.smdb import Ipam
from service.connectors.subscriptions import SubscriptionsAPI
from service.connectors.toolzilla import ToolzillaAPI
from service.products.angelo import AngeloAPI
from service.products.cndns import CNDNSAPI
from service.products.diablo import DiabloAPI
from service.products.go_central import GoCentralAPI
from service.products.mwp_one import MWPOneAPI
from service.products.mwp_two import MWPTwoAPI
from service.products.vertigo import VertigoAPI
from service.products.vps4 import VPS4API
from service.utils.hostname_parser import parse_hostname


class HostingProductResolver(object):
    """
    HostingProductResolver is responsible for determining any hosting products that might be associated
    with the provided domain name. It utilizes a variety of methods, subscriptions API, Toolzilla, etc. to achieve this.
    """
    product_mappers = {
        'diablo': 'Diablo',
        'angelo': 'Plesk',
        'wpaas': 'MWP 1.0',
        'mwp2': 'MWP 2.0',
        'wsb': 'GoCentral',
        'wst': 'Website Tonight',
        'plesk': 'Plesk'
    }

    def __init__(self, config):
        self._logger = logging.getLogger(__name__)
        self.ipam = Ipam(config.SMDB_URL, config.SMDB_USER, config.SMDB_PASS)
        self.toolzilla_api = ToolzillaAPI(config, self.ipam)
        self.subscriptions_api = SubscriptionsAPI(config)

        """
        Neither ToolZilla nor IPAM can search MWP 2.0 and GoCentral Products.
        Hence, giving preference to MWP 2.0 and GoCentral in case we have to loop through the product locators.
        """
        self.product_locators = OrderedDict([
            ('CNDNS', CNDNSAPI(config)),
            ('MWP 2.0', MWPTwoAPI()),
            ('GoCentral', GoCentralAPI(config)),
            ('Vertigo', VertigoAPI(config)),
            ('Diablo', DiabloAPI(config)),
            ('Plesk', AngeloAPI(config)),
            ('MWP 1.0', MWPOneAPI(config)),
            ('VPS4', VPS4API(config))
        ])

    def get_properties_for_domain(self, domain, shopper_id):
        """
        Given a domain name and a shopperID, attempt to determine all related hosted information, or none if the
        domain is not hosted with GoDaddy.
        :param domain:
        :param shopper_id:
        :return:
        """
        dc = os = guid = hostname = created_date = data = host_shopper = None
        ip = self._retrieve_ip(domain)
        container_id = ''

        # Extract the product information from Toolzilla, Subscriptions API, or IPAM
        tz_data = self.toolzilla_api.search_by_domain(domain, ip)
        if tz_data:
            product = tz_data.get('product', '')
            product = self.product_mappers.get(product.lower() if product else '')
            dc = tz_data.get('data_center')
            os = tz_data.get('os')
            guid = tz_data.get('guid')
            hostname = tz_data.get('hostname')
            host_shopper = tz_data.get('shopper_id')
        else:
            subscription = self.subscriptions_api.get_hosting_subscriptions(shopper_id, domain)
            if subscription:
                namespace = subscription.get('product', {}).get('namespace', '')
                product = self.product_mappers.get(namespace.lower() if namespace else '')
                guid = subscription.get('externalId')
                created_date = subscription.get('createdAt')
                host_shopper = shopper_id
            else:
                ipam = self._query_ipam(ip)
                hostname = getattr(ipam, 'HostName', None)
                dc, os, product = parse_hostname(hostname)

        if product in self.product_locators:
            data = self.product_locators.get(product).locate(domain=domain, guid=guid, ip=ip)

        if not data:
            for product_locator in self.product_locators.values():
                data = product_locator.locate(domain=domain, guid=guid, ip=ip)
                if data:
                    break

        response_dict = {'hostname': hostname, 'data_center': dc, 'os': os, 'product': product, 'ip': ip, 'guid': guid,
                         'container_id': container_id, 'created_date': created_date, 'shopper_id': host_shopper}

        if data:
            response_dict.update({
                'data_center': data.get('data_center') or dc,
                'os': data.get('os') or os,
                'product': data.get('product') or product,
                'guid': data.get('guid') or guid,
                'container_id': data.get('container_id') or container_id,
                'shopper_id': data.get('shopper_id') or host_shopper,
                'friendly_name': data.get('friendly_name'),
                'created_date': data.get('created_date') or created_date,
                'private_label_id': data.get('private_label_id'),
                'account_id': data.get('account_id')
            })

        return response_dict

    def _retrieve_ip(self, domain):
        """
        Retrieve ip from domain
        :param domain:
        :return:
        """
        try:
            return socket.gethostbyname(domain)
        except Exception as e:
            self._logger.error(e)

    def _query_ipam(self, ip):
        """
        Query IPAM soap web service and retrive ip related information.
        :param ip:
        :return:
        """
        try:
            return self.ipam.get_properties_for_ip(ip)
        except Exception as e:
            self._logger.error(e)
