from unittest import TestCase

import requests
from mock import MagicMock, patch

from service.products.vps4 import VPS4API
from settings import DevelopmentAppConfig


class TestVPS4API(TestCase):

    """
    Because the VPS4API constructor makes a call to _get_jwt() which make a post request to the SSO endpoint,
    I decided to patch the constructor to mock the return from _get_jwt()
    Solution found at: https://medium.com/@george.shuklin/mocking-complicated-init-in-python-6ef9850dd202
    """

    CREATED = '2019-11-21T08:14:54.658765Z'
    FRIENDLY = 'friendly-name'
    GUID = 'guid'
    IP = '0.0.0.0'
    JUNK_INT = 0
    JUNK_STR = 'junk'
    JUNK_BOOL = False
    JWT = 'JWT_STRING'
    OS = 'LINUX'
    SHOPPER_ID = '123'
    RESELLER_ID = '1'

    # Actual format of VPS API call
    vps4_api_vms_return = [
        {
            "vmId": JUNK_STR,
            "hfsVmId": JUNK_INT,
            "orionGuid": GUID,
            "projectId": JUNK_INT,
            "spec": {
                "specId": JUNK_INT,
                "name": JUNK_STR,
                "specName": JUNK_STR,
                "tier": JUNK_INT,
                "cpuCoreCount": JUNK_INT,
                "memoryMib": JUNK_INT,
                "diskGib": JUNK_INT,
                "validOn": JUNK_STR,
                "validUntil": JUNK_STR,
                "serverType": {
                    "serverTypeId": JUNK_INT,
                    "serverType": JUNK_STR,
                    "platform": JUNK_STR
                },
                "virtualMachine": True
            },
            "name": FRIENDLY,
            "image": {
                "imageId": JUNK_INT,
                "imageName": JUNK_STR,
                "hfsName": JUNK_STR,
                "controlPanel": JUNK_STR,
                "operatingSystem": OS,
                "serverType": {
                    "serverTypeId": JUNK_INT,
                    "serverType": JUNK_STR,
                    "platform": JUNK_STR
                },
                "imageControlPanel": JUNK_STR
            },
            "primaryIpAddress": {
                "ipAddressId": JUNK_INT,
                "vmId": JUNK_STR,
                "ipAddress": IP,
                "ipAddressType": JUNK_STR,
                "pingCheckId": JUNK_INT,
                "validOn": JUNK_STR,
                "validUntil": JUNK_STR
            },
            "validOn": CREATED,
            "canceled": JUNK_STR,
            "validUntil": JUNK_STR,
            "hostname": JUNK_STR,
            "managedLevel": JUNK_INT,
            "backupJobId": JUNK_STR
        }
    ]

    # Actual format of VPS4 API return of credits
    vps4_api_credits_return = {'orionGuid': JUNK_STR,
                               'tier': JUNK_INT,
                               'managedLevel': JUNK_INT,
                               'operatingSystem': JUNK_STR,
                               'controlPanel': JUNK_STR,
                               'provisionDate': JUNK_STR,
                               'shopperId': SHOPPER_ID,
                               'monitoring': JUNK_INT,
                               'accountStatus': JUNK_STR,
                               'dataCenter': {
                                   'dataCenterId': JUNK_INT,
                                   'dataCenterName': JUNK_STR
                               },
                               'productId': JUNK_STR,
                               'fullyManagedEmailSent': JUNK_BOOL,
                               'resellerId': '1',
                               'planChangePending': JUNK_BOOL,
                               'pfid': JUNK_INT,
                               'managed': JUNK_BOOL,
                               'billingSuspendedFlagSet': JUNK_BOOL,
                               'abuseSuspendedFlagSet': JUNK_BOOL,
                               'ded4': JUNK_BOOL,
                               'hasMonitoring': JUNK_BOOL
                               }

    expected_value = {
        'product': 'VPS4',
        'data_center': 'IAD2',
        'guid': GUID,
        'created_date': CREATED,
        'friendly_name': FRIENDLY,
        'os': OS,
        'ip': IP,
        'shopper_id': SHOPPER_ID,
        'reseller_id': RESELLER_ID,
        "managed_level": 'SelfManaged',
        'entitlement_id': GUID
    }

    # When a valid get request is made without a SSO token
    @patch.object(requests, 'get')
    def test_locate_missing_authentication(self, mocked_get):
        with patch.object(VPS4API, "_get_jwt", lambda x: self.JWT):
            vps_api = VPS4API(DevelopmentAppConfig())
            mocked_get.return_value = MagicMock(status_code=403)
            mocked_get.return_value.json.return_value = {'id': 'MISSING_AUTHENTICATION'}
            self.assertEqual(vps_api.locate(self.IP, self.GUID), dict())

    # When no guid is provided and the ip doesnt match any VPS4 products
    @patch.object(requests, 'get')
    def test_locate_ip_not_found(self, mocked_get):
        with patch.object(VPS4API, "_get_jwt", lambda x: self.JWT):
            vps_api = VPS4API(DevelopmentAppConfig())
            mocked_get.return_value = MagicMock(status_code=200)
            mocked_get.return_value.json.return_value = []
            self.assertEqual(vps_api.locate(self.IP, None), dict())

    # When no ip is provided and the guid doesnt match any VPS4 products
    @patch.object(requests, 'get')
    def test_locate_guid_not_found(self, mocked_get):
        with patch.object(VPS4API, "_get_jwt", lambda x: self.JWT):
            vps_api = VPS4API(DevelopmentAppConfig())
            mocked_get.return_value = MagicMock(status_code=200)
            mocked_get.return_value.json.return_value = []
            self.assertEqual(vps_api.locate(None, self.GUID), dict())

    # When the ip OR guid match a VPS4 product
    @patch.object(VPS4API, '_get_shopper_from_credits')
    @patch.object(requests, 'get')
    def test_locate_guid_and_ip_success(self, mocked_get, mocked_credits):
        with patch.object(VPS4API, "_get_jwt", lambda x: self.JWT):
            vps_api = VPS4API(DevelopmentAppConfig())
            mocked_get.return_value = MagicMock(status_code=200)
            mocked_get.return_value.json.return_value = self.vps4_api_vms_return
            mocked_credits.return_value = self.SHOPPER_ID, self.RESELLER_ID
            self.assertEqual(self.expected_value, vps_api.locate(self.IP, self.GUID))

    # When neither an ip nor guid is provided, should raise TypeError exception as either is required
    def test_locate_ip_guid_not_provided(self):
        with patch.object(VPS4API, "_get_jwt", lambda x: self.JWT):
            vps_api = VPS4API(DevelopmentAppConfig())
            self.assertRaises(TypeError, vps_api.locate(None, None))

    # When valid ORION GUID provides credits details
    @patch.object(requests, 'get')
    def test_get_shopper_from_credits(self, mocked_get):
        with patch.object(VPS4API, "_get_jwt", lambda x: self.JWT):
            vps_api = VPS4API(DevelopmentAppConfig())
            mocked_get.return_value = MagicMock(status_code=200)
            mocked_get.return_value.json.return_value = self.vps4_api_credits_return
            self.assertEqual((self.SHOPPER_ID, self.RESELLER_ID), vps_api._get_shopper_from_credits(self.GUID))
