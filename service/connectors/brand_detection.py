import json
import os

import requests
from csetutils.flask.logging import get_logging

from settings import config_by_name

config = config_by_name[os.getenv('sysenv', 'dev')]()


class BrandDetectionHelper(object):
    '''
    Provides a simple interface for interacting with the Brand Detection Service which aids in determining
    the brand associated with a given domain. It also returns limited information such as abuse contact emails, etc.
    '''

    def __init__(self, url):
        self._logger = get_logging()

        self._hosting_endpoint = '{}/hosting?domain={{}}'.format(url)
        self._registrar_endpoint = '{}/registrar?domain={{}}'.format(url)

        self._sso_endpoint = config.SSO_URL + '/v1/secure/api/token'
        self._cert = (config.CMAP_SERVICE_CERT, config.CMAP_SERVICE_KEY)
        self._headers = {'Content-Type': 'application/json', 'Authorization': f'sso-jwt {self._get_jwt(self._cert)}'}

    def get_hosting_info(self, domain):
        """
        Attempt to retrieve the hosting information from the Brand Detection service
        :param domain:
        :return:
        """
        self._logger.info('Fetching hosting information for {}'.format(domain))

        try:
            r = requests.get(self._hosting_endpoint.format(domain), headers=self._headers)
            if r.status_code in [401, 403]:
                self._headers['Authorization'] = f'sso-jwt {self._get_jwt(self._cert)}'
                r = requests.get(self._hosting_endpoint.format(domain), headers=self._headers)
            return r.json()
        except Exception as e:
            self._logger.error('Unable to query Brand Detection service for {} : {}'.format(domain, e))
            return {'brand': None, 'hosting_company_name': None, 'hosting_abuse_email': None, 'ip': None}

    def get_registrar_info(self, domain):
        """
        Attempt to retrieve the registrar information from the Brand Detection service
        :param domain:
        :return:
        """
        self._logger.info('Fetching registrar information for {}'.format(domain))

        try:
            r = requests.get(self._registrar_endpoint.format(domain), headers=self._headers)
            if r.status_code in [401, 403]:
                self._headers['Authorization'] = f'sso-jwt {self._get_jwt(self._cert)}'
                r = requests.get(self._registrar_endpoint.format(domain), headers=self._headers)
            return r.json()
        except Exception as e:
            self._logger.error('Unable to query Brand Detection service for {} : {}'.format(domain, e))
            return {'brand': None, 'registrar_name': None, 'registrar_abuse_email': None, 'domain_create_date': None,
                    'domain_id': None}

    def _get_jwt(self, cert):
        """
        Attempt to retrieve the JWT associated with the cert/key pair from SSO
        :param cert:
        :return: jwt
        """
        try:
            response = requests.post(self._sso_endpoint, data={'realm': 'cert'}, cert=cert)
            response.raise_for_status()

            body = json.loads(response.text)
            return body.get('data')  # {'type': 'signed-jwt', 'id': 'XXX', 'code': 1, 'message': 'Success', 'data': JWT}
        except Exception as e:
            self._logger.error(e.message)
        return
