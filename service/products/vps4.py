import json
from urllib.parse import urlencode

import requests
from dcustructuredloggingflask.flasklogger import get_logging

from service.products.product_interface import Product


class VPS4API(Product):
    _headers = {'Accept': 'application/json', 'Authorization': ''}
    IP_STR = 'ipAddress'
    GUID_STR = 'orionGuid'

    def __init__(self, settings):
        self._logger = get_logging()
        self._vps4_urls = settings.VPS4_URLS
        self._vps4_user = settings.VPS4_USER
        self._vps4_pass = settings.VPS4_PASS
        self._sso_endpoint = settings.SSO_URL + '/v1/api/token'
        self._headers['Authorization'] = f'sso-jwt {self._get_jwt()}'

    def _build_query_dict(self, ip=None, guid=None):
        query_dict = {'type': 'ACTIVE'}

        if ip:
            query_dict[self.IP_STR] = ip
        if guid:
            query_dict[self.GUID_STR] = guid

        return query_dict

    def locate(self, ip, guid, **kwargs):
        """
        This function's sole purpose is to use the method's accepted parameters to determine if an IP or GUID is
        hosted on a VPS4 product. No values are pulled from kwargs
        :param ip:
        :param guid:
        :param kwargs:
        :return: Empty Dict or Dict containing VPS4 account info
        """
        hosting_info = {}

        if ip or guid:
            hosting_info = self._get_vms(ip, guid)

            if hosting_info:
                shopper = self._get_shopper_from_credits(hosting_info.get('guid'))

                if shopper:
                    hosting_info.update(shopper_id=shopper)

        else:
            self._logger.info('A required VPS4 IP Address or Guid was NOT provided')

        return hosting_info

    def _get_jwt(self):
        """
        Attempt to retrieve the JWT associated with the dcu service account user/pass from SSO
        :return:
        """
        try:
            response = requests.post(self._sso_endpoint, data={'username': self._vps4_user,
                                                               'password': self._vps4_pass, 'realm': 'jomax'})
            response.raise_for_status()

            body = json.loads(response.text)
            # Expected return body.get {'type': 'signed-jwt', 'id': 'XXX', 'code': 1, 'message': 'Success', 'data': JWT}
            return body.get('data')
        except Exception as e:
            self._logger.error(e)

    def _get_shopper_from_credits(self, guid):
        """
        Queries VPS4 API /credits/ with Orion GUID for shopperId as /vms does not provide shopperId.
        :param guid: Orion GUID
        :return: shopper ID string
        """
        if guid:
            for url in self._vps4_urls.values():
                try:
                    url = '{}credits/{}'.format(url, guid)
                    r = self._query(url)

                    if not r:
                        self._logger.info('The details for the GUID could not be found at {}'.format(url))
                        continue

                    return r.json().get('shopperId')

                except Exception as e:
                    self._logger.error('Failed VPS4 credit Lookup: {}'.format(e))

            self._logger.info('Can not get VPS4 credits details for: {}'.format(guid))
        else:
            self._logger.info('A required Orion GUID was not provided')

    def _get_vms(self, ip, guid):
        """
        Queries VPS4 API using IP or GUID for account details.
        :param ip:
        :param guid:
        :return: Dict with hosting info if hosted on VPS4
        """
        '''
        Sample of abbreviated VPS4 API Return for /vms, more data is returned (such as details related to server specs
        and server images) than what we will use.

        [
          {
            "vmId": "a0a0a0a0-a0a0-a0a0-a0a0-a0a0a0a0a0a0",
            "hfsVmId": 12345,
            "orionGuid": "a0a0a0a0-a0a0-a0a0-a0a0-a0a0a0a0a0a0",
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
                "vmId": "a0a0a0a0-a0a0-a0a0-a0a0-a0a0a0a0a0a0",
                "ipAddress": "0.0.0.0",
                "ipAddressType": "PRIMARY",
                "pingCheckId": null,
                "validOn": "2019-04-30T13:21:06.688121Z",
                "validUntil": "+292278994-08-16T23:00:00Z"
            },
            "validOn": "2019-04-30T13:20:25.262804Z",
            "canceled": "+292278994-08-16T23:00:00Z",
            "validUntil": "+292278994-08-16T23:00:00Z",
            "hostname": "a0a0-00-000-00.secureserver.net",
            "managedLevel": 0,
            "backupJobId": "a0a0a0a0-a0a0-a0a0-a0a0-a0a0a0a0a0a0",
            "fullyManaged": false
            }
        ]
        '''

        query_dict = self._build_query_dict(ip, guid)

        for dc, dc_url in self._vps4_urls.items():
            try:
                dc_url = '{}vms?{}'.format(dc_url, urlencode(query_dict))
                dc_r = self._query(dc_url)

                dc_res = dc_r.json()
                # dc_res will be {'id': 'INTERNAL_ERROR', 'message': 'An internal error occurred'} if
                #  you're not in a production env, as JWT's created on DEV/OTE wont work with a prod VPS endpoint.
                # In order to test VPS4 in dev or ote, you'll need to return a hardcoded prod JWT from _get_jwt

                if not dc_res:
                    self._logger.info('The details provided could not be found at {}'.format(dc_url))

                for vps_data in dc_res:
                    # If vps_data isn't a dictionary, it causes the error: 'str' object has no attribute 'get'
                    if not isinstance(vps_data, dict):
                        continue
                    if (query_dict.get(self.IP_STR) == vps_data.get('primaryIpAddress', {}).get(self.IP_STR)) or \
                            (query_dict.get(self.GUID_STR) == vps_data.get(self.GUID_STR)):
                        return {
                            'product': 'VPS4',
                            'data_center': dc,
                            'guid': vps_data.get(self.GUID_STR),
                            'created_date': vps_data.get('validOn'),
                            'friendly_name': vps_data.get('name'),
                            'os': vps_data.get('image').get('operatingSystem'),
                            'ip': vps_data.get('primaryIpAddress').get(self.IP_STR)
                        }
            except Exception as e:
                self._logger.error('Failed VPS4 Lookup: {}'.format(e))
                return dict()

        self._logger.info('Not determined to be a VPS4 product')
        return dict()

    def _query(self, url):
        r = requests.get(url, headers=self._headers)
        if r.status_code in [401, 403]:
            self._headers['Authorization'] = f'sso-jwt {self._get_jwt()}'
            r = requests.get(url, headers=self._headers)
        return r
