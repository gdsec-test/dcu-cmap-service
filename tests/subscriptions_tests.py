from mock import patch
from nose.tools import assert_false, assert_true

from service.connectors.subscriptions import SubscriptionsAPI
from settings import DevelopmentAppConfig


class TestSubscriptionsAPI:

    @classmethod
    def setup(cls):
        cls._subscriptions_api = SubscriptionsAPI(DevelopmentAppConfig())
        cls._mock_ssl_sub_response = [
            {
                'subscriptionId': '1',
                'status': 'ACTIVE',
                'label': 'test1.com',
                'createdAt': '2019-04-15T20:48:58.340Z',
                'expiresAt': '2021-04-15T07:00:00.000Z',
                'product': {
                    'productGroupKey': 'sslCerts'
                }
            }
        ]

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
