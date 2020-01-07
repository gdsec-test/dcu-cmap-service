import requests
from mock import MagicMock, patch
from nose.tools import assert_equal, assert_is_none

from service.products.cndns import CNDNSAPI
from settings import DevelopmentAppConfig


class TestCNDNSAPI:
    _cndns = CNDNSAPI(DevelopmentAppConfig())

    @patch.object(requests, 'get')
    def test_locate_success(self, mocked_method):
        mocked_method.return_value = MagicMock(status_code=200)
        mocked_method.return_value.json.return_value = {'partner': 'cndns',
                                                        'siteId': 'gdtest-000000',
                                                        'records': [
                                                            {
                                                                'orionGuid': '000aa0a0-b000-00s0-0000-0000sss000s0',
                                                                'shopperId': '1234'
                                                            }
                                                        ]}
        actual = self._cndns.locate('test-domain')
        assert_equal(actual.get('guid'), '000aa0a0-b000-00s0-0000-0000sss000s0')
        assert_equal(actual.get('shopper_id'), '1234')
        assert_equal(actual.get('product'), 'WSBD')

    @patch.object(requests, 'get')
    def test_locate_domain_not_found(self, mocked_method):
        mocked_method.return_value = MagicMock(status_code=404)
        assert_is_none(self._cndns.locate('test-domain'))

    @patch.object(requests, 'get')
    def test_locate_failure(self, mocked_method):
        mocked_method.return_value = MagicMock(status_code=500)
        assert_is_none(self._cndns.locate('test-domain'))
