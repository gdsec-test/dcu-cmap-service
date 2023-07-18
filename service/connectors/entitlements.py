from typing import Optional

import requests
from csetutils.flask.logging import get_logging


class EntitlementsAPI(object):
    def __init__(self, config):
        self._logger = get_logging()
        self._url = config.ENTITLEMENTS_URL
        self._sso_url = config.SSO_URL
        self._cert = (config.CMAP_SERVICE_CLIENT_CERT, config.CMAP_SERVICE_CLIENT_KEY)
        self._jwt = None

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

    def get_entitlement(self, customerId: str, entitlementId: str) -> Optional[dict]:
        headers = {'content-type': 'application/json', 'Authorization': f'sso-jwt {self._get_jwt()}'}
        response = requests.get(f'{self._url}/v2/customers/{customerId}/entitlements/{entitlementId}', headers=headers)
        if response.status_code == 403 or response.status_code == 401:
            headers = {'content-type': 'application/json', 'Authorization': f'sso-jwt {self._get_jwt(True)}'}
            response = requests.get(f'{self._url}/v2/customers/{customerId}/entitlements/{entitlementId}', headers=headers)
        response.raise_for_status()
        return response.json()
