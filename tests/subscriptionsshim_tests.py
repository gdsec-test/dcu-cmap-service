from unittest import TestCase

import requests
from mock import Mock, patch

from service.connectors.subscriptionsshim import SubscriptionsShimAPI
from settings import DevelopmentAppConfig


class MockResponse:
    def __init__(self, json_data, status_code, raise_for_status):
        self.json_data = json_data
        self.status_code = status_code
        self.raise_for_status = raise_for_status

    def json(self):
        return self.json_data


class TestEntitlementsAPI(TestCase):
    def setUp(self):
        self._subscriptions_api = SubscriptionsShimAPI(DevelopmentAppConfig())

    @patch.object(requests, 'get', return_value=MockResponse({"customerId": "fe3a1f3f-a078-4e62-90b5-be72c9a3675e", "subscriptionId": "diablo:15294056", "uri": "/customers/fe3a1f3f-a078-4e62-90b5-be72c9a3675e/subscriptions/diablo:15294056", "metadata": {"createdAt": "2023-01-30T17:28:09.000Z", "revision": 1, "modifiedAt": "2023-01-30T17:43:45.000Z"}, "status": "ACTIVE", "statusUpdatedAt": "2023-01-30T17:43:45Z", "paymentInstrumentUri": "/v1/fe3a1f3f-a078-4e62-90b5-be72c9a3675e/payment-instruments/960b12b0-5159-4c8e-bfc6-ac8e7bb67111", "paidThroughDate": "2026-01-30T07:00:00Z", "canBeRenewed": True, "offer": {"uri": "/customers/31430a42-6f4f-4646-9595-305f614957be/offers/05730877-89bd-49c0-8fff-c9880b743bf0", "autoRenew": True, "term": {"termType": "YEAR", "numberOfTerms": 3}, "products": [{"key": "799b2e70-6771-4260-a92e-244c6e1e3550", "product": {"productFamily": "hosting", "uri": "/customers/31430a42-6f4f-4646-9595-305f614957be/products/5dc57ceb-3ad1-4b89-b700-4bb6313f084f", "plan": "ultimate", "resourceType": "product", "productType": "cpanel", "planTier": 4001}}], "plan": "ultimate"}, "linkedEntitlements": [{"productKey": "799b2e70-6771-4260-a92e-244c6e1e3550", "entitlementUri": "/customers/fe3a1f3f-a078-4e62-90b5-be72c9a3675e/entitlements/748e4869-a0c3-11ed-81af-0050569a00bd", "commonName": "heyhalinatest.com", "i18nKey": "MTMzODk5Ng=="}], "commonName": "heyhalinatest.com", "i18nKey": "MTMzODk5Ng=="}, 200, Mock(return_value='')))
    @patch.object(SubscriptionsShimAPI, '_get_jwt')
    def test_entitlementid_cpanel(self, mocked_get_jwt, mocked_post):
        mocked_get_jwt.return_value = 'jwt123'
        self.assertEqual(self._subscriptions_api.find_product_by_entitlement("customer", "entitlement"), [{'product': "Diablo", 'domain': "heyhalinatest.com"}])

    @patch.object(requests, 'get', return_value=MockResponse({"customerId": "not-a-real-uuid", "subscriptionId": "diablo:591263339", "uri": "/customers/not-a-real-uuid/subscriptions/diablo:591263339", "metadata": {"revision": 1, "modifiedAt": "2022-10-13T14:31:48.000Z", "createdAt": "2022-10-13T09:41:00.000Z"}, "status": "ACTIVE", "statusUpdatedAt": "2022-10-13T14:31:48Z", "paidThroughDate": "2022-11-13T07:00:00Z", "canBeRenewed": True, "offer": {"uri": "/customers/not-a-real-uuid/offers/8b8af56e-1453-4ce3-8cfd-e466f886eb03", "autoRenew": False, "term": {"termType": "MONTH", "numberOfTerms": 1}, "products": [{"key": "0118a064-43ef-4569-998a-68a910b6d2d1", "product": {"productFamily": "hosting", "uri": "/customers/not-a-real-uuid/products/5dc57ceb-3ad1-4b89-b700-4bb6313f084f", "plan": "economy", "resourceType": "product", "productType": "managedWordPress", "planTier": 2000}}], "plan": "economy"}, "linkedEntitlements": [{"productKey": "0118a064-43ef-4569-998a-68a910b6d2d1", "entitlementUri": "/customers/not-a-real-uuid/entitlements/20538a1d-4adb-11ed-828e-3417ebe724ff", "commonName": "example.com", "i18nKey": "bm90cmVhbGJhc2U2NAo="}], "commonName": "example.com", "i18nKey": "bm90cmVhbGJhc2U2NAo="}, 200, Mock(return_value='')))
    @patch.object(SubscriptionsShimAPI, '_get_jwt')
    def test_entitlementid_mwp(self, mocked_get_jwt, mocked_post):
        mocked_get_jwt.return_value = 'jwt123'
        self.assertEqual(self._subscriptions_api.find_product_by_entitlement("customer", "entitlement"), [{'product': "MWP 1.0", 'domain': "example.com"}])

    @patch.object(requests, 'get', return_value=MockResponse({"customerId": "not-a-real-uuid", "subscriptionId": "diablo:591263339", "uri": "/customers/not-a-real-uuid/subscriptions/diablo:591263339", "metadata": {"revision": 1, "modifiedAt": "2022-10-13T14:31:48.000Z", "createdAt": "2022-10-13T09:41:00.000Z"}, "status": "ACTIVE", "statusUpdatedAt": "2022-10-13T14:31:48Z", "paidThroughDate": "2022-11-13T07:00:00Z", "canBeRenewed": True, "offer": {"uri": "/customers/not-a-real-uuid/offers/8b8af56e-1453-4ce3-8cfd-e466f886eb03", "autoRenew": False, "term": {"termType": "MONTH", "numberOfTerms": 1}, "products": [{"key": "0118a064-43ef-4569-998a-68a910b6d2d1", "product": {"productFamily": "hosting", "uri": "/customers/not-a-real-uuid/products/5dc57ceb-3ad1-4b89-b700-4bb6313f084f", "plan": "economy", "resourceType": "product", "productType": "websitesAndMarketing", "planTier": 2000}}], "plan": "economy"}, "linkedEntitlements": [{"productKey": "0118a064-43ef-4569-998a-68a910b6d2d1", "entitlementUri": "/customers/not-a-real-uuid/entitlements/20538a1d-4adb-11ed-828e-3417ebe724ff", "commonName": "example.com", "i18nKey": "bm90cmVhbGJhc2U2NAo="}], "commonName": "example.com", "i18nKey": "bm90cmVhbGJhc2U2NAo="}, 200, Mock(return_value='')))
    @patch.object(SubscriptionsShimAPI, '_get_jwt')
    def test_entitlementid_gocentral(self, mocked_get_jwt, mocked_post):
        mocked_get_jwt.return_value = 'jwt123'
        self.assertEqual(self._subscriptions_api.find_product_by_entitlement("customer", "entitlement"), [{'product': "GoCentral", 'domain': "example.com"}])

    @patch.object(requests, 'get', return_value=MockResponse({"customerId": "not-a-real-uuid", "subscriptionId": "diablo:591263339", "uri": "/customers/not-a-real-uuid/subscriptions/diablo:591263339", "metadata": {"revision": 1, "modifiedAt": "2022-10-13T14:31:48.000Z", "createdAt": "2022-10-13T09:41:00.000Z"}, "status": "ACTIVE", "statusUpdatedAt": "2022-10-13T14:31:48Z", "paidThroughDate": "2022-11-13T07:00:00Z", "canBeRenewed": True, "offer": {"uri": "/customers/not-a-real-uuid/offers/8b8af56e-1453-4ce3-8cfd-e466f886eb03", "autoRenew": False, "term": {"termType": "MONTH", "numberOfTerms": 1}, "products": [{"key": "0118a064-43ef-4569-998a-68a910b6d2d1", "product": {"productFamily": "hosting", "uri": "/customers/not-a-real-uuid/products/5dc57ceb-3ad1-4b89-b700-4bb6313f084f", "plan": "economy", "resourceType": "product", "productType": "virtualPrivateServerHostingV4", "planTier": 2000}}], "plan": "economy"}, "linkedEntitlements": [{"productKey": "0118a064-43ef-4569-998a-68a910b6d2d1", "entitlementUri": "/customers/not-a-real-uuid/entitlements/20538a1d-4adb-11ed-828e-3417ebe724ff", "commonName": "example.com", "i18nKey": "bm90cmVhbGJhc2U2NAo="}], "commonName": "example.com", "i18nKey": "bm90cmVhbGJhc2U2NAo="}, 200, Mock(return_value='')))
    @patch.object(SubscriptionsShimAPI, '_get_jwt')
    def test_entitlementid_VPS4(self, mocked_get_jwt, mocked_post):
        mocked_get_jwt.return_value = 'jwt123'
        self.assertEqual(self._subscriptions_api.find_product_by_entitlement("customer", "entitlement"), [{'product': "VPS4", 'domain': "example.com"}])

    @patch.object(requests, 'get', return_value=MockResponse({"customerId": "fe3a1f3f-a078-4e62-90b5-be72c9a3675e", "subscriptionId": "angelo:15294160", "uri": "/customers/fe3a1f3f-a078-4e62-90b5-be72c9a3675e/subscriptions/angelo:15294160", "metadata": {"createdAt": "2023-01-30T20:11:50.000Z", "revision": 1, "modifiedAt": "2023-01-30T23:14:02.000Z"}, "status": "ACTIVE", "statusUpdatedAt": "2023-01-30T23:14:02Z", "paymentInstrumentUri": "/v1/fe3a1f3f-a078-4e62-90b5-be72c9a3675e/payment-instruments/960b12b0-5159-4c8e-bfc6-ac8e7bb67111", "paidThroughDate": "2023-04-30T07:00:00Z", "canBeRenewed": True, "offer": {"uri": "/customers/31430a42-6f4f-4646-9595-305f614957be/offers/e8523785-b9d8-4f25-bb99-cfc37bd2e9a7", "autoRenew": True, "term": {"termType": "QUARTER", "numberOfTerms": 1}, "products": [{"key": "ac56176-9ac0-422f-bd9d-62ada0ff26aa", "product": {"productFamily": "hosting", "uri": "/customers/31430a42-6f4f-4646-9595-305f614957be/products/d2c2d9dd-2778-403f-adf5-fbe0519ffefc", "plan": "economy", "resourceType": "product", "productType": "plesk", "planTier": 10}}], "plan": "economy"}, "linkedEntitlements": [{"productKey": "ac56176-9ac0-422f-bd9d-62ada0ff26aa", "entitlementUri": "/customers/fe3a1f3f-a078-4e62-90b5-be72c9a3675e/entitlements/5251f248-a0da-11ed-81af-0050569a00bd", "commonName": "iloveplesk.info", "i18nKey": "MzI0MDc="}], "commonName": "iloveplesk.info", "i18nKey": "MzI0MDc="}, 200, Mock(return_value='')))
    @patch.object(SubscriptionsShimAPI, '_get_jwt')
    def test_entitlementid_plesk(self, mocked_get_jwt, mocked_post):
        mocked_get_jwt.return_value = 'jwt123'
        self.assertEqual(self._subscriptions_api.find_product_by_entitlement("customer", "entitlement"), [{'product': "Plesk", 'domain': "iloveplesk.info"}])

    @patch.object(requests, 'get', return_value=MockResponse({"customerId": "not-a-real-uuid", "subscriptionId": "diablo:591263339", "uri": "/customers/not-a-real-uuid/subscriptions/diablo:591263339", "metadata": {"revision": 1, "modifiedAt": "2022-10-13T14:31:48.000Z", "createdAt": "2022-10-13T09:41:00.000Z"}, "status": "ACTIVE", "statusUpdatedAt": "2022-10-13T14:31:48Z", "paidThroughDate": "2022-11-13T07:00:00Z", "canBeRenewed": True, "offer": {"uri": "/customers/not-a-real-uuid/offers/8b8af56e-1453-4ce3-8cfd-e466f886eb03", "autoRenew": False, "term": {"termType": "MONTH", "numberOfTerms": 1}, "products": [{"key": "0118a064-43ef-4569-998a-68a910b6d2d1", "product": {"productFamily": "hosting", "uri": "/customers/not-a-real-uuid/products/5dc57ceb-3ad1-4b89-b700-4bb6313f084f", "plan": "enhanceWhmcs", "resourceType": "product", "productType": "cpanel", "planTier": 2000}}], "plan": "enhanceWhmcs"}, "linkedEntitlements": [{"productKey": "0118a064-43ef-4569-998a-68a910b6d2d1", "entitlementUri": "/customers/not-a-real-uuid/entitlements/20538a1d-4adb-11ed-828e-3417ebe724ff", "commonName": "example.com", "i18nKey": "bm90cmVhbGJhc2U2NAo="}], "commonName": "example.com", "i18nKey": "bm90cmVhbGJhc2U2NAo="}, 200, Mock(return_value='')))
    @patch.object(SubscriptionsShimAPI, '_get_jwt')
    def test_entitlementid_whms(self, mocked_get_jwt, mocked_post):
        mocked_get_jwt.return_value = 'jwt123'
        self.assertEqual(self._subscriptions_api.find_product_by_entitlement("customer", "entitlement"), [{'product': "Diablo WHMCS", 'domain': "example.com"}])

    @patch.object(requests, 'get', return_value=MockResponse({"customerId": "not-a-real-uuid", "subscriptionId": "diablo:591263339", "uri": "/customers/not-a-real-uuid/subscriptions/diablo:591263339", "metadata": {"revision": 1, "modifiedAt": "2022-10-13T14:31:48.000Z", "createdAt": "2022-10-13T09:41:00.000Z"}, "status": "ACTIVE", "statusUpdatedAt": "2022-10-13T14:31:48Z", "paidThroughDate": "2022-11-13T07:00:00Z", "canBeRenewed": True, "offer": {"uri": "/customers/not-a-real-uuid/offers/8b8af56e-1453-4ce3-8cfd-e466f886eb03", "autoRenew": False, "term": {"termType": "MONTH", "numberOfTerms": 1}, "products": [{"key": "0118a064-43ef-4569-998a-68a910b6d2d1", "product": {"productFamily": "hosting", "uri": "/customers/not-a-real-uuid/products/5dc57ceb-3ad1-4b89-b700-4bb6313f084f", "plan": "enhanceWhmcs", "resourceType": "product", "productType": "cpanel", "planTier": 2000}}, {"key": "00000000-43ef-4569-998a-68a910b6d2d1", "product": {"productFamily": "hosting", "uri": "/customers/not-a-real-uuid/products/5dc57ceb-3ad1-4b89-b700-4bb6313f084f", "plan": "enhanceWhmcs", "resourceType": "product", "productType": "plesk", "planTier": 2000}}], "plan": "enhanceWhmcs"}, "linkedEntitlements": [{"productKey": "0118a064-43ef-4569-998a-68a910b6d2d1", "entitlementUri": "/customers/not-a-real-uuid/entitlements/20538a1d-4adb-11ed-828e-3417ebe724ff", "commonName": "example.com", "i18nKey": "bm90cmVhbGJhc2U2NAo="}, {"productKey": "00000000-43ef-4569-998a-68a910b6d2d1", "entitlementUri": "/customers/not-a-real-uuid/entitlements/20538a1d-4adb-11ed-828e-3417ebe724ff", "commonName": "newexample.com", "i18nKey": "bm90cmVhbGJhc2U2NAo="}], "commonName": "example.com", "i18nKey": "bm90cmVhbGJhc2U2NAo="}, 200, Mock(return_value='')))
    @patch.object(SubscriptionsShimAPI, '_get_jwt')
    def test_entitlementid_multiple(self, mocked_get_jwt, mocked_post):
        mocked_get_jwt.return_value = 'jwt123'
        self.assertEqual(self._subscriptions_api.find_product_by_entitlement("customer", "entitlement"), [{'product': "Diablo WHMCS", 'domain': "example.com"}, {'product': "Plesk", 'domain': "newexample.com"}])
