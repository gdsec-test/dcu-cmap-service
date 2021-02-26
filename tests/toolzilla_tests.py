from mock import patch
from nose.tools import assert_equal, assert_is_none

from service.connectors.toolzilla import ToolzillaAPI
from settings import DevelopmentAppConfig

A_RECORD = '0.0.0.0'
DOMAIN = 'domain'
GUID = 'guid'
HOSTNAME = 'hostname'
SHOPPER = 'shopper'
# Products used
DHS = 'dhs'
DIABLO = 'diablo'
WPAAS = 'wpaas'


class MockIpam:
    # Returning the "a record" in the list of ips so search_by_domain() will return one of three dicts
    def get_ips_by_hostname(self, hostname):
        return [A_RECORD, '0.0.0.1']


class MockService:
    # For ease of testing "products", a "product" should be passed in as the domain_name
    def searchByDomain(self, domain_name):
        return [[{'AccountUid': [GUID],
                  'ShopperId': [SHOPPER],
                  'ProductType': [domain_name]}
                 ]]


class MockClient:
    service = MockService()

    def last_received(self):
        return 'LAST RECEIVED'


class TestToolzillaAPI:
    no_loc = 'Unable to locate'
    expected_value_not_wpaas_nor_dhs = {
        'guid': GUID,
        'shopper_id': SHOPPER,
        'product': DIABLO,
        'hostname': HOSTNAME
    }
    expected_value_wpaas = {
        'guid': GUID,
        'shopper_id': SHOPPER,
        'product': WPAAS,
        'os': 'Linux',
        'hostname': no_loc,
        'data_center': no_loc
    }
    expected_value_dhs = {
        'guid': GUID,
        'shopper_id': SHOPPER,
        'product': DHS,
        'os': no_loc,
        'hostname': no_loc,
        'data_center': no_loc
    }

    mock_client_obj = MockClient()
    mock_ipam_obj = MockIpam()

    TZ_CLIENT = 'service.connectors.toolzilla.Client'
    GET_HOSTNAME_METHOD = '_get_hostname_by_guid'

    # Successful search on a product that is neither wpaas nor dhs
    @patch.object(ToolzillaAPI, GET_HOSTNAME_METHOD)
    @patch(TZ_CLIENT)
    def test_search_by_domain_product_not_wpaas_nor_dhs(self, mock_client, mock_get_host):
        mock_client.return_value = self.mock_client_obj
        mock_get_host.return_value = HOSTNAME
        tz_api = ToolzillaAPI(DevelopmentAppConfig(), self.mock_ipam_obj)
        assert_equal(self.expected_value_not_wpaas_nor_dhs, tz_api.search_by_domain(DIABLO, A_RECORD))

    # Successful search on a wpaas product
    @patch.object(ToolzillaAPI, GET_HOSTNAME_METHOD)
    @patch(TZ_CLIENT)
    def test_search_by_domain_product_wpaas(self, mock_client, mock_get_host):
        mock_client.return_value = self.mock_client_obj
        mock_get_host.return_value = HOSTNAME
        tz_api = ToolzillaAPI(DevelopmentAppConfig(), self.mock_ipam_obj)
        assert_equal(self.expected_value_wpaas, tz_api.search_by_domain(WPAAS, A_RECORD))

    # Successful search on a dhs product
    @patch.object(ToolzillaAPI, GET_HOSTNAME_METHOD)
    @patch(TZ_CLIENT)
    def test_search_by_domain_product_dhs(self, mock_client, mock_get_host):
        mock_client.return_value = self.mock_client_obj
        mock_get_host.return_value = HOSTNAME
        tz_api = ToolzillaAPI(DevelopmentAppConfig(), self.mock_ipam_obj)
        assert_equal(self.expected_value_dhs, tz_api.search_by_domain(DHS, A_RECORD))

    # When a domain isn't provided, should raise TypeError exception as it is required
    @patch(TZ_CLIENT)
    def test_search_by_domain_no_domain(self, mock_client):
        mock_client.return_value = self.mock_client_obj
        tz_api = ToolzillaAPI(DevelopmentAppConfig(), self.mock_ipam_obj)
        assert_is_none(tz_api.search_by_domain(None, A_RECORD))

    # When an a_record isn't provided, should raise TypeError exception as it is required
    @patch(TZ_CLIENT)
    def test_search_by_domain_no_arecord(self, mock_client):
        mock_client.return_value = self.mock_client_obj
        tz_api = ToolzillaAPI(DevelopmentAppConfig(), self.mock_ipam_obj)
        assert_is_none(tz_api.search_by_domain(DIABLO, None))

    # Failure when soap client can't be instantiated
    def test_search_by_domain_client_not_instantiated(self):
        tz_api = ToolzillaAPI(DevelopmentAppConfig(), self.mock_ipam_obj)
        assert_is_none(tz_api.search_by_domain(DIABLO, A_RECORD))
