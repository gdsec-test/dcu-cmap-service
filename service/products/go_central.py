import json
import logging

import requests


class GoCentralAPI(object):
    _headers = {'Accept': 'application/json', 'Authorization': ''}

    def __init__(self, settings):
        self._logger = logging.getLogger(__name__)
        self._url = settings.GOCENTRAL_URL
        self._sso_endpoint = settings.SSO_URL + '/v1/secure/api/token'

        cert = (settings.CMAP_SERVICE_CERT, settings.CMAP_SERVICE_KEY)
        self._headers['Authorization'] = 'sso-jwt ' + self._get_jwt(cert)

    def locate(self, domain):
        """
        This functions sole purpose use the available domains api to determine if a domain name is hosted with a
        gocentral hosting product.
        :param: domain:
        :return: Dict with hosting info if hosted GoCentral, Or empty dict
        """
        '''
        Sample of partial GoCentral API Return.  More data is returned that could possibly be used in the future.
        Api Spec at https://websites.api.dev-godaddy.com/v2/docs/#/ for GET /v2/domains/{domain}/website

        {'id': '9edafb08-0d94-45a6-a33b-e27c54993fe6',
        'domainName': 'lorzio45.godaddysites.com',
        'accountId': '32f811b3-af51-11e8-814e-3417ebe72595', # This is the GUID
        'accountSource': 'orion',
        'shopperId': '123456789',
        'resellerId': 1,
        'type': 'gocentral',
        'homepageId': '28e6dc92-3bec-438c-8d0d-75c251def48c',
        'createDate': '2018-09-03T08:13:14.124Z',
        'updateDate': '2018-09-03T08:33:04.020Z',
        'status': 'active',
        ... ...

        '''
        try:
            r = requests.get(self._url.format(domain=domain), headers=self._headers)
            res = json.loads(r.text)
            if res.get('type', '').lower() == 'gocentral':
                return dict(product='GoCentral', guid=res.get('accountId'), shopper_id=res.get('shopperId'),
                            created_date=res.get('createDate'))

            else:
                self._logger.debug('GoCentral API determined that {} is not a GoCentral domain'.format(domain))

        except Exception as e:
            self._logger.error('GoCentral API Exception for {}: msg:{}.'.format(domain, e))

        return {}

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
