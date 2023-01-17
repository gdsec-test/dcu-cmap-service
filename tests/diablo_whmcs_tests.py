from unittest import TestCase

import requests
from mock import MagicMock, patch

from service.products.diablo_whmcs import DiabloAPIWHMCS
from settings import DevelopmentAppConfig


class TestDiabloWHMCSAPI(TestCase):
    CREATED = '2019-11-21T08:14:54.658765Z'
    GUID = 'guid'
    IP = '0.0.0.0'
    NON_DIABLO_IP = '1.1.1.1'
    JUNK_INT = 0
    JUNK_STR = 'junk'
    JUNK_BOOL = False
    RESELLER_ID = 'reseller_id'
    OS = 'Linux'
    SHOPPER_ID = '123'
    WHMCS = 'Diablo WHMCS'
    NON_WHMCS = 'Diablo'
    USERNAME = 'username'
    C2NOTFOUND = 'NotFound'
    C2USERNAME1 = 'c2user1'
    C2USERNAME2 = 'c2user2'
    DOMAIN = C2DOMAIN1 = 'domain.tld'
    C2DOMAIN2 = 'c2domain2.tld'
    PATH1 = '/folder/file.ext'
    PATH2 = '/~c2user2/file.ext'

    expected_whmcs_requests_get_return = {
        'c1_account': {
            'orion_guid': GUID,
            'shopper_id': SHOPPER_ID,
            'created_at': CREATED,
            'shared_ip_address': IP,
            'os': OS,
            'product': WHMCS,
            'reseller_id': RESELLER_ID
        },
        'c2_accounts': [
            {
                'user': C2USERNAME1,
                'domain': C2DOMAIN1,
                'suspended': 0,
                'suspendreason': 'not suspended',
                'owner': 'c1user',
                'ip': IP
            },
            {
                'user': C2USERNAME2,
                'domain': C2DOMAIN2,
                'suspended': 0,
                'suspendreason': 'not suspended',
                'owner': 'c1user',
                'ip': IP
            }
        ],
        'type': 'hash'
    }

    expected_non_whmcs_requests_get_return = {
        'c1_account': {
            'orion_guid': GUID,
            'shopper_id': SHOPPER_ID,
            'created_at': CREATED,
            'shared_ip_address': NON_DIABLO_IP,
            'os': OS,
            'product': NON_WHMCS,
            'reseller_id': RESELLER_ID,
            'username': USERNAME
        },
        'c2_accounts': [
            {}
        ],
        'type': 'hash'
    }

    expected_whmcs_locate_return = {
        'guid': GUID,
        'shopper_id': SHOPPER_ID,
        'created_date': CREATED,
        'ip': IP,
        'os': OS,
        'product': WHMCS,
        'reseller_id': RESELLER_ID,
        'username': C2USERNAME1
    }

    expected_whmcs_locate_return_ip_url = {
        'guid': GUID,
        'shopper_id': SHOPPER_ID,
        'created_date': CREATED,
        'ip': IP,
        'os': OS,
        'product': WHMCS,
        'reseller_id': RESELLER_ID,
        'username': C2USERNAME2
    }

    expected_whmcs_locate_return_ip_url_invalid = {
        'guid': GUID,
        'shopper_id': SHOPPER_ID,
        'created_date': CREATED,
        'ip': IP,
        'os': OS,
        'product': WHMCS,
        'reseller_id': RESELLER_ID,
        'username': C2NOTFOUND
    }

    expected_400_requests_get_return = {
        "message": "Failed to get whmcs accounts info",
        "type": "error"
    }

    expected_400_locate_return = {}

    # When the ip matches a Diablo WHMCS product
    @patch.object(requests, 'get')
    def test_locate_whmcs_ip_success(self, mocked_get):
        diablo_api_whmcs = DiabloAPIWHMCS(DevelopmentAppConfig())
        mocked_get.return_value = MagicMock(status_code=200)
        mocked_get.return_value.json.return_value = self.expected_whmcs_requests_get_return
        self.assertDictEqual(self.expected_whmcs_locate_return, diablo_api_whmcs.locate(self.IP, self.DOMAIN, self.PATH1))
        mocked_get.assert_called()

    # When the ip matches a Diablo WHMCS product on an IP-based URL with a valid username in the path
    @patch.object(requests, 'get')
    def test_locate_whmcs_ip_success_ip_url_with_user(self, mocked_get):
        self.DOMAIN = self.IP
        diablo_api_whmcs = DiabloAPIWHMCS(DevelopmentAppConfig())
        mocked_get.return_value = MagicMock(status_code=200)
        mocked_get.return_value.json.return_value = self.expected_whmcs_requests_get_return
        self.assertDictEqual(self.expected_whmcs_locate_return_ip_url,
                             diablo_api_whmcs.locate(self.IP, self.DOMAIN, self.PATH2))
        mocked_get.assert_called()

    # When the ip matches a Diablo WHMCS product on an IP-based URL with an invalid or no username in the path
    @patch.object(requests, 'get')
    def test_locate_whmcs_ip_success_ip_url_without_user(self, mocked_get):
        self.DOMAIN = self.IP
        diablo_api_whmcs = DiabloAPIWHMCS(DevelopmentAppConfig())
        mocked_get.return_value = MagicMock(status_code=200)
        mocked_get.return_value.json.return_value = self.expected_whmcs_requests_get_return
        self.assertDictEqual(self.expected_whmcs_locate_return_ip_url_invalid,
                             diablo_api_whmcs.locate(self.IP, self.DOMAIN, self.PATH1))
        mocked_get.assert_called()

    # When the ip matches a Diablo non-WHMCS product
    @patch.object(requests, 'get')
    def test_locate_non_whmcs(self, mocked_get):
        diablo_api_whmcs = DiabloAPIWHMCS(DevelopmentAppConfig())
        mocked_get.return_value = MagicMock(status_code=400)
        mocked_get.return_value.json.return_value = self.expected_non_whmcs_requests_get_return
        self.assertDictEqual(self.expected_400_locate_return,
                             diablo_api_whmcs.locate(self.NON_DIABLO_IP, self.DOMAIN, self.PATH1))
        mocked_get.assert_called()

    # When the ip doesn't match a Diablo product
    @patch.object(requests, 'get')
    def test_locate_ip_fail(self, mocked_get):
        diablo_api_whmcs = DiabloAPIWHMCS(DevelopmentAppConfig())
        mocked_get.return_value = MagicMock(status_code=400)
        mocked_get.return_value.json.return_value = self.expected_400_requests_get_return
        self.assertDictEqual(self.expected_400_locate_return,
                             diablo_api_whmcs.locate(self.NON_DIABLO_IP, self.DOMAIN, self.PATH1))
        mocked_get.assert_called()
