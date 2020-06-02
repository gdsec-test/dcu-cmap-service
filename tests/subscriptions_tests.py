import requests
from mock import patch
from nose.tools import assert_equal, assert_false, assert_true

from service.connectors.subscriptions import SubscriptionsAPI
from settings import DevelopmentAppConfig


class MockResponse:
    text = '{"subscriptions": "1"}'


class TestSubscriptionsAPI:

    @classmethod
    def setup(cls):
        cls._subscriptions_api = SubscriptionsAPI(DevelopmentAppConfig())
        common = dict(subscriptionId='1', status='ACTIVE', label='test1.com', createdAt='2019-04-15T20:48:58.340Z',
                      expiresAt='2021-04-15T07:00:00.000Z')
        commontwo = dict(subscriptionId='1', status='ACTIVE', label='test2.com', createdAt='2019-04-15T20:48:58.340Z',
                         expiresAt='2021-04-15T07:00:00.000Z')
        cls._mock_ssl_sub_response = [dict(product={'productGroupKey': 'sslCerts'}, **common)]
        cls._mock_hosting_sub_response = [dict(product={'namespace': 'diablo'}, **common)]
        cls._mock_hosting_sub_response_mwptwo = [dict(product={'namespace': 'mwp2'}, **commontwo)]
        cls._mock_sucuri_sub_response = [dict(product={'productGroupKey': 'websiteSecurity', 'label': 'test'},
                                              **common)]

    """
    get_hosting_subscriptions tests
    """

    @patch.object(SubscriptionsAPI, '_get_subscriptions')
    def test_get_hosting_subscriptions_match(self, mocked_subs_api):
        mocked_subs_api.return_value = self._mock_hosting_sub_response
        assert_equal(self._subscriptions_api.get_hosting_subscriptions('102704532', 'test1.com'),
                     mocked_subs_api.return_value[0])

    # testing of _check_label
    @patch.object(SubscriptionsAPI, '_get_subscriptions')
    def test_get_hosting_subscriptions_match_mwptwo(self, mocked_subs_api):
        mocked_subs_api.return_value = self._mock_hosting_sub_response_mwptwo
        assert_equal(self._subscriptions_api.get_hosting_subscriptions('102704532', 'test2.com'),
                     mocked_subs_api.return_value[0])

    @patch.object(SubscriptionsAPI, '_get_subscriptions')
    def test_get_hosting_subscriptions_no_match(self, mocked_subs_api):
        mocked_subs_api.return_value = self._mock_hosting_sub_response
        assert_equal(self._subscriptions_api.get_hosting_subscriptions('102704532', 'abc.com'), {})

    """
    get_sucuri_subscriptions tests
    """

    @patch.object(SubscriptionsAPI, '_get_subscriptions')
    def test_get_sucuri_subscriptions(self, mocked_subs_api):
        mocked_subs_api.return_value = self._mock_sucuri_sub_response
        assert_equal(self._subscriptions_api.get_sucuri_subscriptions('102704532', 'test1.com')[0], 'test')

    """
    get_ssl_subscriptions tests
    """

    def test_get_ssl_subscriptions_blacklist_shopper(self):
        assert_false(self._subscriptions_api.get_ssl_subscriptions('102704532', 'abc.com'))

    @patch.object(SubscriptionsAPI, '_get_subscriptions')
    def test_get_ssl_subscriptions_success(self, mocked_subs_api):
        mocked_subs_api.return_value = self._mock_ssl_sub_response
        assert_true(self._subscriptions_api.get_ssl_subscriptions('100', 'test1.com'))

    @patch.object(SubscriptionsAPI, '_get_subscriptions')
    def test_get_ssl_subscriptions_failure(self, mocked_subs_api):
        mocked_subs_api.return_value = []
        assert_false(self._subscriptions_api.get_ssl_subscriptions('100', 'test3.com'))

    """
    _get_subscriptions tests
    """

    @patch.object(requests, 'get', return_value=MockResponse)
    def test_get_subscriptions(self, mocked_get):
        assert_equal(self._subscriptions_api._get_subscriptions('102704532', ['websiteSecurity'], 'test1.com'), ['1'])

    def test_get_subscriptions_no_id(self):
        assert_equal(self._subscriptions_api._get_subscriptions(None, ['websiteSecurity'], 'test1.com'), [])
