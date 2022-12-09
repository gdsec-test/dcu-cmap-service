import json

import requests
from csetutils.flask.logging import get_logging

from service.products.product_interface import Product


class MWPOneAPI(Product):

    _headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    def __init__(self, settings):
        self._logger = get_logging()
        self.url = settings.MWPONE_URL
        self.cert = (settings.CMAP_SERVICE_CLIENT_CERT, settings.CMAP_SERVICE_CLIENT_KEY)
        self._sso_endpoint = settings.SSO_URL + '/v1/secure/api/token'

    def _get_jwt(self, cert):
        """
        Attempt to retrieve the JWT associated with the cert/key pair from SSO
        :param cert:
        :return:
        """
        try:
            response = requests.post(self._sso_endpoint, data={'realm': 'cert'}, cert=cert)
            response.raise_for_status()

            body = json.loads(response.text)
            # Expected return body.get {'type': 'signed-jwt', 'id': 'XXX', 'code': 1, 'message': 'Success', 'data': JWT}
            return body.get('data')
        except Exception as e:
            self._logger.error(e)
        return None

    def locate(self, domain, guid=None, **kwargs):
        """
        This functions sole purpose is to locate all data for a MWP 1.0 account to be placed into the data
        sub document of the incident's mongo document
        :param domain:
        :param kwargs:
        :return:
        """
        response = {}
        query_param = {}
        if guid:
            query_param['accountUid'] = guid
        else:
            query_param['domain'] = domain
        try:
            self._headers['Authorization'] = f'sso-jwt {self._get_jwt(self.cert)}'
            r = requests.get(self.url, cert=self.cert, headers=self._headers, params=query_param, verify=False)
            response = r.json()
        except Exception as e:
            self._logger.error(e)

        for entry in response.get('data', []):
            if entry.get('statusId') != 1:
                continue

            return {
                'guid': entry.get('accountUid'),
                'account_id': entry.get('id'),
                'shopper_id': entry.get('shopperId'),
                'reseller_id': entry.get('resellerId'),
                'os': 'Linux',
                'data_center': self._dc_helper(entry.get('dataCenter', {}).get('description')),
                'product': 'MWP 1.0',
                'ip': entry.get('ipAddress'),
                'hostname': 'MWP 1.0 does not return hostname',
                'created_date': entry.get('dateCreated'),
                'primary_domain': entry.get('domain'),
                'product_uid': entry.get('productUid', '')
            }
        else:
            self._logger.info('No active MWP 1.0 account ID found for {}'.format(domain))

    def _dc_helper(self, dc):
        if dc == 'Buckeye':
            dc = 'P3'
        elif dc == 'Ashburn':
            dc = 'A2'
        elif dc == 'Amsterdam':
            dc = 'N1'
        return dc
