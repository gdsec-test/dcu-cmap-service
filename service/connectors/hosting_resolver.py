import socket
from asyncio import create_task
from collections import OrderedDict
from typing import Union

from dcustructuredloggingflask.flasklogger import get_logging
from prometheus_client import Counter

from service.connectors.smdb import Ipam
from service.connectors.subscriptions import SubscriptionsAPI
from service.connectors.toolzilla import ToolzillaAPI
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

toolzilla_successes = Counter('toolzilla_successes', 'Number of successful calls to toolzilla')
toolzilla_failure = Counter('toolzilla_failure', 'Number of failed calls to toolzilla')
subscription_successes = Counter('subscription_successes', 'Number of successful calls to subscription API')
subscription_failure = Counter('subscription_failure', 'Number of failed calls to subscription API')
mismatched_guid = Counter('mismatched_guid', 'Number of mismatched calls between the subscription API and toolzilla')


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
        'plesk': 'Plesk',
        'sharedhosting': '4GH'
    }

    def __init__(self, config):
        self._logger = get_logging()
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
            ('Diablo WHMCS', DiabloAPIWHMCS(config)),
            ('Plesk', AngeloAPI(config)),
            ('MWP 1.0', MWPOneAPI(config)),
            ('VPS4', VPS4API(config))
        ])

    async def __get_toolzilla_properties(self, domain: str, ip: str) -> tuple:
        tz_data = self.toolzilla_api.search_by_domain(domain, ip)
        if tz_data:
            product = tz_data.get('product', '')
            product = self.product_mappers.get(product.lower() if product else '')
            dc = tz_data.get('data_center')
            os = tz_data.get('os')
            guid = tz_data.get('guid')
            hostname = tz_data.get('hostname')
            host_shopper = tz_data.get('shopper_id')
            if guid and host_shopper and product:
                toolzilla_successes.inc()
            return product, dc, os, guid, hostname, host_shopper
        toolzilla_failure.inc()
        return None

    async def __get_subscription_properties(self, shopper_id: str, domain: str) -> tuple:
        subscription = self.subscriptions_api.get_hosting_subscriptions(shopper_id, domain)
        if subscription:
            namespace = subscription.get('product', {}).get('namespace', '')
            product = self.product_mappers.get(namespace.lower() if namespace else '')
            guid = subscription.get('externalId')
            if guid:
                subscription_successes.inc()
            created_date = subscription.get('createdAt')
            return product, guid, created_date
        subscription_failure.inc()
        return None

    async def __get_ipam_properties(self, ip: str) -> Union[tuple, None]:
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

    def locate_product(self, domain: str, guid: str, ip: str, product: str = None) -> dict:
        if product and product in self.product_locators:
            pl_data = self.product_locators.get(product).locate(domain=domain, guid=guid, ip=ip)
            if pl_data:
                return pl_data
        else:
            for product_locator in self.product_locators.values():
                pl_data = product_locator.locate(domain=domain, guid=guid, ip=ip)
                if pl_data:
                    return pl_data
        return {}

    async def get_properties_for_domain(self, domain, shopper_id):
        """
        Given a domain name and a shopperID, attempt to determine all related hosted information, or none if the
        domain is not hosted with GoDaddy.
        :param domain:
        :param shopper_id:
        :return:
        """
        created_date = dc = guid = hostname = host_shopper = os = product = tz_guid = sub_guid = None
        ip = self._retrieve_ip(domain)

        # We support three sources: Toolzilla, Subscriptions API, and IPAM
        # Run async tasks to grab the info we need in parallel.
        tool_task = create_task(self.__get_toolzilla_properties(domain, ip))
        sub_task = create_task(self.__get_subscription_properties(shopper_id, domain))
        ipam_task = create_task(self.__get_ipam_properties(ip))
        tz_params = await tool_task
        sub_params = await sub_task
        ipam_params = await ipam_task
        dc = os = product = None
        if tz_params:
            product = tz_params[0]
            dc = tz_params[1]
            os = tz_params[2]
            guid = tz_params[3]
            tz_guid = guid
            hostname = tz_params[4]
            host_shopper = tz_params[5]
        elif sub_params:
            product = sub_params[0]
            guid = sub_guid = sub_params[1]
            created_date = sub_params[2]
            host_shopper = shopper_id
        elif ipam_params:
            dc, os, product = ipam_params
        data = self.locate_product(domain=domain, guid=guid, ip=ip, product=product)

        if tz_params:
            tz_guid = tz_params[2]
        if sub_params:
            sub_guid = sub_params[1]
        if sub_guid != tz_guid:
            mismatched_guid.inc()
        self._logger.info("username: ", data.get('username'))
        return {
            'hostname': hostname,
            'ip': ip,
            'data_center': data.get('data_center', dc),
            'os': data.get('os', os),
            'product': data.get('product', product),
            'guid': data.get('guid', guid),
            'container_id': data.get('container_id'),
            'shopper_id': data.get('shopper_id', host_shopper),
            'friendly_name': data.get('friendly_name'),
            'created_date': data.get('created_date', created_date),
            'private_label_id': data.get('private_label_id'),
            'account_id': data.get('account_id'),
            'username': data.get('username')
        }

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
