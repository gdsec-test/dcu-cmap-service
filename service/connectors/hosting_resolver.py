import socket
from asyncio import create_task
from collections import OrderedDict
from typing import Optional

from csetutils.flask.logging import get_logging
from dns import resolver

from service.connectors.smdb import Ipam
from service.connectors.subscriptions import SubscriptionsAPI
from service.products.angelo import AngeloAPI
from service.products.cndns import CNDNSAPI
from service.products.diablo import DiabloAPI
from service.products.diablo_whmcs import DiabloAPIWHMCS
from service.products.go_central import GoCentralAPI
from service.products.mwp_one import MWPOneAPI
from service.products.mwp_two import MWPTwoAPI
from service.products.vertigo import VertigoAPI
from service.products.vps4 import VPS4API
from service.utils.functions import ip_is_parked
from service.utils.hostname_parser import parse_hostname
from settings import AppConfig


class HostingProductResolver(object):
    """
    HostingProductResolver is responsible for determining any hosting products that might be associated
    with the provided domain name. It utilizes a variety of methods, subscriptions API, etc. to achieve this.
    """
    product_mappers = {
        'diablo': 'Diablo',
        'angelo': 'Plesk',
        'wpaas': 'MWP 1.0',
        'mwp2': 'MWP 2.0',
        'wsb': 'GoCentral',
        'wst': 'Website Tonight',
        'plesk': 'Plesk',
        'sharedhosting': '4GH'
    }

    def __init__(self, config: AppConfig):
        self._logger = get_logging()
        self.ipam = Ipam(config.SMDB_URL, config.SMDB_USER, config.SMDB_PASS)
        self.subscriptions_api = SubscriptionsAPI(config)
        self.config = config

        """
        IPAM can not search for MWP 2.0 and GoCentral Products.
        Hence, giving preference to MWP 2.0 and GoCentral in case we have to loop through the product locators.
        """
        self.product_locators = OrderedDict([
            ('CNDNS', CNDNSAPI(config)),
            ('MWP 2.0', MWPTwoAPI()),
            ('GoCentral', GoCentralAPI(config)),
            ('Vertigo', VertigoAPI(config)),
            ('Diablo', DiabloAPI(config)),
            ('Diablo WHMCS', DiabloAPIWHMCS(config)),
            ('Plesk', AngeloAPI(config)),
            ('MWP 1.0', MWPOneAPI(config)),
            ('VPS4', VPS4API(config))
        ])

    async def __get_subscription_properties(self, shopper_id: str, domain: str) -> Optional[tuple]:
        subscription = self.subscriptions_api.get_hosting_subscriptions(shopper_id, domain)
        if subscription:
            namespace = subscription.get('product', {}).get('namespace', '')
            product = self.product_mappers.get(namespace.lower() if namespace else '')
            guid = subscription.get('externalId')
            created_date = subscription.get('createdAt')
            return product, guid, created_date
        return None

    async def __get_ipam_properties(self, ip: str) -> Optional[tuple]:
        # check for parking IP first
        if ip_is_parked(ip):
            return None, None, 'Parked'

        # fallback to ipam if not parked
        ipam = self._query_ipam(ip)
        hostname = getattr(ipam, 'HostName') if getattr(ipam, 'HostName', None) else getattr(ipam, 'Description', None)
        # IPAM description Useful for parked pages: "PHX3 - ParkWeb PodA - Server Loopbacks"
        if hostname:
            dc, os, product = parse_hostname(hostname)
            return dc, os, product
        return None

    def locate_product(self, domain: str, guid: str, ip: str, product: str = None, path: str = None) -> dict:
        if product and product in self.product_locators:
            pl_data = self.product_locators.get(product).locate(domain=domain, guid=guid, ip=ip, path=path)
            if pl_data:
                pl_data['second_pass_enrichment'] = product
                return pl_data
        else:
            for product_locator in self.product_locators.values():
                pl_data = product_locator.locate(domain=domain, guid=guid, ip=ip, path=path)
                if pl_data:
                    pl_data['second_pass_enrichment'] = pl_data['product']
                    return pl_data
        return {}

    async def get_properties_for_domain(self, domain, shopper_id, path):
        """
        Given a domain name and a shopperID, attempt to determine all related hosted information, or none if the
        domain is not hosted with GoDaddy.
        :param domain:
        :param shopper_id:
        :return:
        """
        created_date = dc = guid = hostname = host_shopper = os = product = None
        first_pass_enrichment = ''
        ip = self._retrieve_ip(domain)

        # We support two sources: Subscriptions API and IPAM
        # Run async tasks to grab the info we need in parallel.
        sub_task = create_task(self.__get_subscription_properties(shopper_id, domain))
        ipam_task = create_task(self.__get_ipam_properties(ip))
        sub_params = await sub_task
        ipam_params = await ipam_task
        dc = os = product = None
        if sub_params:
            product = sub_params[0]
            guid = sub_params[1]
            created_date = sub_params[2]
            host_shopper = shopper_id
            first_pass_enrichment = 'subscriptionapi'
        elif ipam_params:
            dc, os, product = ipam_params
            first_pass_enrichment = 'ipam'
        data = self.locate_product(domain=domain, guid=guid, ip=ip, product=product, path=path)

        return {
            'hostname': hostname,
            'ip': ip,
            'data_center': data.get('data_center', dc),
            'os': data.get('os', os),
            'product': data.get('product', product),
            'guid': data.get('guid', guid),
            'container_id': data.get('container_id'),
            'shopper_id': data.get('shopper_id', host_shopper),
            'reseller_id': data.get('reseller_id'),
            'friendly_name': data.get('friendly_name'),
            'created_date': data.get('created_date', created_date),
            'private_label_id': data.get('private_label_id'),
            'account_id': data.get('account_id'),
            'username': data.get('username'),
            'managed_level': data.get('managed_level'),
            'first_pass_enrichment': first_pass_enrichment,
            'second_pass_enrichment': data.get('second_pass_enrichment', '')
        }

    def _retrieve_ip(self, domain):
        """
        Retrieve ip from domain
        :param domain:
        :return:
        """
        try:
            if self.config.CUSTOM_NS:
                try:
                    dnsresolver = resolver.Resolver()
                    dnsresolver.nameservers = [self.config.CUSTOM_NS]
                    return dnsresolver.query(domain, 'A')[0].address
                except:  # noqa: E722
                    pass
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
