import json
import logging
from urllib.parse import urlencode

import requests

from service.products.product_interface import Product


class VPS4API(Product):
    _headers = {'Accept': 'application/json', 'Authorization': ''}

    def __init__(self, settings):
        self._logger = logging.getLogger(__name__)
        self._vps4_urls = settings.VPS4_URLS
        self._vps4_user = settings.VPS4_USER
        self._vps4_pass = settings.VPS4_PASS
        self._sso_endpoint = settings.SSO_URL + '/v1/api/token'

        self._headers['Authorization'] = 'sso-jwt {}'.format(self._get_jwt())

    def _build_query_dict(self, ip=None, guid=None):
        query_dict = {'type': 'ACTIVE'}

        if ip:
            query_dict['ipAddress'] = ip
        if guid:
            query_dict['orionGuid'] = guid

        return query_dict

    def locate(self, ip, guid, **kwargs):
        """
        This function's sole purpose is to use the method's accepted parameters to determine if an IP, GUID, ServerID or
        shopperID is hosted on a VPS4 product. IP or guid pulled from kwargs
        :param ip:
        :param guid:
        :param kwargs:
        :return: List of Dict(s) with hosting info if hosted on VPS4, Or empty list
        """
        '''
        Sample of abbreviated VPS4 API Return, more data is returned (such as details related to server specs and
        server images) than what we will use.

        [
          {
            "vmId": "efbd1eec-23f4-5af6-a78b-901a2b300e5e",
            "hfsVmId": 12345,
            "orionGuid": "1f234ed5-6b78-99e0-1122-3445ebe60eb6",
            "projectId": 1234,
            "spec": {
                "serverType": {
                    "serverTypeId": 1,
                    "serverType": "VIRTUAL",
                    "platform": "OPENSTACK"
                    },
                    "virtualMachine": true
            },
            "name": "Sample",
            "image": {
                "controlPanel": "PLESK",
                "operatingSystem": "WINDOWS",
                "serverType": {
                    "serverTypeId": 1,
                    "serverType": "VIRTUAL",
                    "platform": "OPENSTACK"
                    }
            },
            "primaryIpAddress": {
                "ipAddressId": 12345,
                "vmId": "efbd1eec-23f4-5af0-a67b-890a1b200e3e",
                "ipAddress": "123.45.678.90",
                "ipAddressType": "PRIMARY",
                "pingCheckId": null,
                "validOn": "2019-04-30T13:21:06.688121Z",
                "validUntil": "+292278994-08-16T23:00:00Z"
            },
            "validOn": "2019-04-30T13:20:25.262804Z",
            "canceled": "+292278994-08-16T23:00:00Z",
            "validUntil": "+292278994-08-16T23:00:00Z",
            "hostname": "s123-45-678-90.secureserver.net",
            "managedLevel": 0,
            "backupJobId": "0f1d34c4-ff5c-67d-b89a-0d1234250d67",
            "fullyManaged": false
            }
        ]
        '''

        query_dict = self._build_query_dict(ip, guid)
        if query_dict.get('ipAddress') or query_dict.get('orionGuid'):
            for dc, dc_url in self._vps4_urls.items():
                try:
                    dc_url = '{}?{}'.format(dc_url, urlencode(query_dict))
                    dc_r = requests.get(dc_url, headers=self._headers)
                    if dc_r.status_code == 403 and dc_r.json().get('id') == 'MISSING_AUTHENTICATION':
                        fresh_jwt = self._get_jwt()

                        self._headers['Authorization'] = "sso-jwt " + fresh_jwt
                        dc_r = requests.get(dc_url, headers=self._headers)

                    dc_res = dc_r.json()

                    if not dc_res:
                        self._logger.error('The details provided could not be found at {}'.format(dc_url))

                    for vps_data in dc_res:
                        if (query_dict.get('ipAddress') == vps_data.get('primaryIpAddress', {}).get('ipAddress')) or \
                                (query_dict.get('orionGuid') == vps_data.get('orionGuid')):
                            return {
                                'product': 'VPS4',
                                'data_center': dc,
                                'guid': vps_data.get('orionGuid'),
                                'created_date': vps_data.get('validOn'),
                                'friendly_name': vps_data.get('name'),
                                'os': vps_data.get('image').get('operatingSystem'),
                                'ip': vps_data.get('primaryIpAddress').get('ipAddress')
                            }

                except Exception as e:
                    self._logger.error('Failed VPS4 Lookup: {}'.format(e))
        else:
            self._logger.error('Please provide a VPS4 IP Address or Guid')

    def _get_jwt(self):
        """
        Attempt to retrieve the JWT associated with the dcu service account user/pass from SSO
        :return:
        """
        try:
            response = requests.post(self._sso_endpoint, data={'username': self._vps4_user, 'password': self._vps4_pass, 'realm': 'jomax'})
            response.raise_for_status()

            body = json.loads(response.text)
            # Expected return body.get {'type': 'signed-jwt', 'id': 'XXX', 'code': 1, 'message': 'Success', 'data': JWT}
            return body.get('data')
        except Exception as e:
            self._logger.error(e)
        return
