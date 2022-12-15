import requests
from mock import patch
from nose.tools import assert_equal

from service.products.mwp_one import MWPOneAPI
from settings import LocalAppConfig


class TestMWPAPI:

    @patch.object(requests, 'get')
    def test_mwp_api(self, mocked_get):
        mwp_one_api = MWPOneAPI(LocalAppConfig())
        mocked_get.return_value.json.return_value = {'data': [{'id': '28988', 'accountType': {'id': 1, 'description': 'primary'}, 'accountTypeId': 1, 'accountUid': 'e7a39f62-1a2f-4c94-9158-bf740b3a977a', 'aliasDomains': [], 'applicationDatabaseId': 14446, 'applicationId': 1, 'clusterId': 1, 'cName': 'dpq.c96.fac.test.domaincontrol-com.ide', 'countryCode': 'us', 'dataCenterId': 3, 'dateCreated': '2020-03-06T20:10:52Z', 'dateCreatedTS': 1583525452000, 'databaseServerId': '3', 'domain': 'test.com', 'ipAddress': '10.38.134.16', 'language': 'en-US', 'maxStagingAccounts': 1, 'productUid': '3465f7f2-5a7f-11ea-810e-0050569a00bd', 'resellerId': 1, 'shopperId': '1296956', 'sshStatus': {'id': 2, 'description': 'Inactive'}, 'sslHtaccessStatusId': 2, 'status': {'id': 1, 'description': 'Deleted'}, 'statusId': 1, 'userId': 2900, 'version': '5.4', 'wordPressBlogTitle': 'Blog Title', 'xid': 42767515, 'filerId': 64, 'dataCenter': {'id': '3', 'description': 'Buckeye'}}]}
        assert_equal(mwp_one_api.locate("test.com"), {'guid': 'e7a39f62-1a2f-4c94-9158-bf740b3a977a', 'account_id': '28988', 'shopper_id': '1296956', 'reseller_id': 1, 'os': 'Linux', 'data_center': 'P3', 'product': 'MWP 1.0', 'ip': '10.38.134.16', 'hostname': 'MWP 1.0 does not return hostname', 'created_date': '2020-03-06T20:10:52Z', 'primary_domain': 'test.com', 'product_uid': '3465f7f2-5a7f-11ea-810e-0050569a00bd', 'staging_url': 'dpq.c96.fac.test.domaincontrol-com.ide'})

    @patch.object(requests, 'get')
    def test_not_hosted_mwp_api(self, mocked_get):
        mwp_one_api = MWPOneAPI(LocalAppConfig())
        mocked_get.return_value.json.return_value = {"data": []}
        assert_equal(mwp_one_api.locate("test.com"), None)
