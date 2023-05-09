from unittest import TestCase
from unittest.mock import MagicMock, patch

from service.connectors.netbox import Netbox


class TestNetboxLookup(TestCase):

    def setUp(self):
        self.netbox = Netbox('http://localhost', 'token')

    @patch('service.connectors.netbox.requests.get')
    def test_lookup_hostname(self, requests_get):
        requests_get.return_value = MagicMock(
            raise_for_status=MagicMock(return_value=None),
            json=MagicMock(return_value={'results': [{'custom_fields': {'IPPlan_HostName': 'localhost.local'}}]})
        )
        resp = self.netbox.lookup_hostname('127.0.0.1')
        self.assertEqual(resp, 'localhost.local')
        requests_get.assert_called_with('http://localhost/api/ipam/ip-addresses/', params={'address': '127.0.0.1'}, headers={'Authorization': 'Token token', 'Accept': 'application/json'})

    @patch('service.connectors.netbox.requests.get')
    def test_lookup_desc(self, requests_get):
        requests_get.return_value = MagicMock(
            raise_for_status=MagicMock(return_value=None),
            json=MagicMock(return_value={'results': [{'description': 'a description'}]})
        )
        resp = self.netbox.lookup_hostname('127.0.0.1')
        self.assertEqual(resp, 'a description')
        requests_get.assert_called_with('http://localhost/api/ipam/ip-addresses/', params={'address': '127.0.0.1'}, headers={'Authorization': 'Token token', 'Accept': 'application/json'})
