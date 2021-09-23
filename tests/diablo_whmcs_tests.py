import requests
from mock import MagicMock, patch
from nose.tools import assert_dict_equal

from service.products.diablo_whmcs import DiabloAPIWHMCS
from settings import DevelopmentAppConfig


class TestDiabloWHMCSAPI:
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
                'something': 'foo'
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
        'reseller_id': RESELLER_ID
    }

    expected_non_whmcs_locate_return = {
        'guid': GUID,
        'shopper_id': SHOPPER_ID,
        'created_date': CREATED,
        'ip': NON_DIABLO_IP,
        'os': OS,
        'product': NON_WHMCS,
        'reseller_id': RESELLER_ID,
        'username': USERNAME
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
        assert_dict_equal(self.expected_whmcs_locate_return, diablo_api_whmcs.locate(self.WHMCS))
        mocked_get.assert_called()

    # When the ip matches a Diablo non-WHMCS product
    @patch.object(requests, 'get')
    def test_locate_non_whmcs_ip_success(self, mocked_get):
        diablo_api_whmcs = DiabloAPIWHMCS(DevelopmentAppConfig())
        mocked_get.return_value = MagicMock(status_code=200)
        mocked_get.return_value.json.return_value = self.expected_non_whmcs_requests_get_return
        assert_dict_equal(self.expected_non_whmcs_locate_return, diablo_api_whmcs.locate(self.NON_WHMCS))
        mocked_get.assert_called()

    # When the ip doesn't match a Diablo product
    @patch.object(requests, 'get')
    def test_locate_ip_fail(self, mocked_get):
        diablo_api_whmcs = DiabloAPIWHMCS(DevelopmentAppConfig())
        mocked_get.return_value = MagicMock(status_code=400)
        mocked_get.return_value.json.return_value = self.expected_400_requests_get_return
        assert_dict_equal(self.expected_400_locate_return, diablo_api_whmcs.locate(self.NON_WHMCS))
        mocked_get.assert_called()
