from typing import Optional

import requests
from csetutils.flask.logging import get_logging


class SubscriptionsShimAPI(object):
    def __init__(self, config):
        self._logger = get_logging()
        self._url = config.SUBSCRIPTIONS_SHIM_URL
        self._sso_url = config.SSO_URL
        self._cert = (config.CMAP_SERVICE_CLIENT_CERT, config.CMAP_SERVICE_CLIENT_KEY)
        self._jwt = None
        self._prod_dict = {'cpanel': 'Diablo', 'managedWordPress': 'MWP 1.0', 'websitesAndMarketing': 'GoCentral', 'virtualPrivateServerHostingV4': 'VPS4', 'plesk': 'Plesk'}

    def _get_jwt(self, force_refresh: bool = False) -> str:
        if self._jwt is None or force_refresh:
            try:
                response = requests.post(f'{self._sso_url}/v1/secure/api/token',
                                         data={'realm': 'cert'}, cert=self._cert)
                response.raise_for_status()
                sso_response = response.json()
                self._jwt = sso_response.get('data')
            except Exception:
                self._logger.exception('Error calling sso')
                return ''
        return self._jwt

    def get_entitlement_plan(self, customerId: str, entitlementId: str) -> Optional[str]:
        headers = {'content-type': 'application/json', 'Authorization': f'sso-jwt {self._get_jwt()}'}
        response = requests.get(f'{self._url}/v2/customers/{customerId}/subscriptionByEntitlementId?entitlementId={entitlementId}', headers=headers)
        if response.status_code == 403 or response.status_code == 401:
            headers = {'content-type': 'application/json', 'Authorization': f'sso-jwt {self._get_jwt(True)}'}
            response = requests.get(f'{self._url}/v2/customers/{customerId}/subscriptionByEntitlementId?entitlementId={entitlementId}', headers=headers)
        response.raise_for_status()
        resp = response.json()
        return resp.get('offer', {}).get('plan', None)

    def find_product_by_entitlement(self, customerId: str, entitlementId: str) -> dict:
        headers = {'content-type': 'application/json', 'Authorization': f'sso-jwt {self._get_jwt()}'}
        response = requests.get(f'{self._url}/v2/customers/{customerId}/subscriptionByEntitlementId?entitlementId={entitlementId}', headers=headers)
        if response.status_code == 403 or response.status_code == 401:
            headers = {'content-type': 'application/json', 'Authorization': f'sso-jwt {self._get_jwt(True)}'}
            response = requests.get(f'{self._url}/v2/customers/{customerId}/subscriptionByEntitlementId?entitlementId={entitlementId}', headers=headers)
        response.raise_for_status()
        resp = response.json()
        products = resp.get('offer').get('products')
        entitlements = resp.get('linkedEntitlements')
        products_lists = []
        for entitlement in entitlements:
            key = entitlement.get('productKey')
            for product in products:
                if key == product.get('key'):
                    prod_type = (product.get('product').get('productType'))
                    prod_type_conversion = self._prod_dict.get(prod_type)
                    if prod_type == 'cpanel' and product.get('product').get('plan') == 'enhanceWhmcs':
                        prod_type_conversion = 'Diablo WHMCS'
                    domain = entitlement.get('commonName')
                    products_lists.append({'product': prod_type_conversion, 'domain': domain})
        return products_lists
