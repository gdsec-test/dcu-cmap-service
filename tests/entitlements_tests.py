from unittest import TestCase

import requests
from mock import Mock, patch

from service.connectors.entitlements import EntitlementsAPI
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
        self._subscriptions_api = EntitlementsAPI(DevelopmentAppConfig())

    @patch.object(requests, 'get', return_value=MockResponse({"customerId": "not-a-real-uuid", "subscriptionId": "diablo:591263339", "uri": "/customers/not-a-real-uuid/subscriptions/diablo:591263339", "metadata": {"revision": 1, "modifiedAt": "2022-10-13T14:31:48.000Z", "createdAt": "2022-10-13T09:41:00.000Z"}, "status": "ACTIVE", "statusUpdatedAt": "2022-10-13T14:31:48Z", "paidThroughDate": "2022-11-13T07:00:00Z", "canBeRenewed": True, "offer": {"uri": "/customers/not-a-real-uuid/offers/8b8af56e-1453-4ce3-8cfd-e466f886eb03", "autoRenew": False, "term": {"termType": "MONTH", "numberOfTerms": 1}, "products": [{"key": "0118a064-43ef-4569-998a-68a910b6d2d1", "product": {"productFamily": "hosting", "uri": "/customers/not-a-real-uuid/products/5dc57ceb-3ad1-4b89-b700-4bb6313f084f", "plan": "economy", "resourceType": "product", "productType": "cpanel", "planTier": 2000}}], "plan": "economy"}, "linkedEntitlements": [{"productKey": "0118a064-43ef-4569-998a-68a910b6d2d1", "entitlementUri": "/customers/not-a-real-uuid/entitlements/20538a1d-4adb-11ed-828e-3417ebe724ff", "commonName": "example.com", "i18nKey": "bm90cmVhbGJhc2U2NAo="}], "commonName": "example.com", "i18nKey": "bm90cmVhbGJhc2U2NAo="}, 200, Mock(return_value='')))
    @patch.object(EntitlementsAPI, '_get_jwt')
    def test_entitlementid_cpanel(self, mocked_get_jwt, mocked_post):
        mocked_get_jwt.return_value = 'jwt123'
        self.assertEqual(self._subscriptions_api.find_product_by_entitlement("customer", "entitlement"), [{'product': "Diablo", 'domain': "example.com"}])

    @patch.object(requests, 'get', return_value=MockResponse({"customerId": "not-a-real-uuid", "subscriptionId": "diablo:591263339", "uri": "/customers/not-a-real-uuid/subscriptions/diablo:591263339", "metadata": {"revision": 1, "modifiedAt": "2022-10-13T14:31:48.000Z", "createdAt": "2022-10-13T09:41:00.000Z"}, "status": "ACTIVE", "statusUpdatedAt": "2022-10-13T14:31:48Z", "paidThroughDate": "2022-11-13T07:00:00Z", "canBeRenewed": True, "offer": {"uri": "/customers/not-a-real-uuid/offers/8b8af56e-1453-4ce3-8cfd-e466f886eb03", "autoRenew": False, "term": {"termType": "MONTH", "numberOfTerms": 1}, "products": [{"key": "0118a064-43ef-4569-998a-68a910b6d2d1", "product": {"productFamily": "hosting", "uri": "/customers/not-a-real-uuid/products/5dc57ceb-3ad1-4b89-b700-4bb6313f084f", "plan": "economy", "resourceType": "product", "productType": "managedWordPress", "planTier": 2000}}], "plan": "economy"}, "linkedEntitlements": [{"productKey": "0118a064-43ef-4569-998a-68a910b6d2d1", "entitlementUri": "/customers/not-a-real-uuid/entitlements/20538a1d-4adb-11ed-828e-3417ebe724ff", "commonName": "example.com", "i18nKey": "bm90cmVhbGJhc2U2NAo="}], "commonName": "example.com", "i18nKey": "bm90cmVhbGJhc2U2NAo="}, 200, Mock(return_value='')))
    @patch.object(EntitlementsAPI, '_get_jwt')
    def test_entitlementid_mwp(self, mocked_get_jwt, mocked_post):
        mocked_get_jwt.return_value = 'jwt123'
        self.assertEqual(self._subscriptions_api.find_product_by_entitlement("customer", "entitlement"), [{'product': "MWP 1.0", 'domain': "example.com"}])

    @patch.object(requests, 'get', return_value=MockResponse({"customerId": "not-a-real-uuid", "subscriptionId": "diablo:591263339", "uri": "/customers/not-a-real-uuid/subscriptions/diablo:591263339", "metadata": {"revision": 1, "modifiedAt": "2022-10-13T14:31:48.000Z", "createdAt": "2022-10-13T09:41:00.000Z"}, "status": "ACTIVE", "statusUpdatedAt": "2022-10-13T14:31:48Z", "paidThroughDate": "2022-11-13T07:00:00Z", "canBeRenewed": True, "offer": {"uri": "/customers/not-a-real-uuid/offers/8b8af56e-1453-4ce3-8cfd-e466f886eb03", "autoRenew": False, "term": {"termType": "MONTH", "numberOfTerms": 1}, "products": [{"key": "0118a064-43ef-4569-998a-68a910b6d2d1", "product": {"productFamily": "hosting", "uri": "/customers/not-a-real-uuid/products/5dc57ceb-3ad1-4b89-b700-4bb6313f084f", "plan": "economy", "resourceType": "product", "productType": "websitesAndMarketing", "planTier": 2000}}], "plan": "economy"}, "linkedEntitlements": [{"productKey": "0118a064-43ef-4569-998a-68a910b6d2d1", "entitlementUri": "/customers/not-a-real-uuid/entitlements/20538a1d-4adb-11ed-828e-3417ebe724ff", "commonName": "example.com", "i18nKey": "bm90cmVhbGJhc2U2NAo="}], "commonName": "example.com", "i18nKey": "bm90cmVhbGJhc2U2NAo="}, 200, Mock(return_value='')))
    @patch.object(EntitlementsAPI, '_get_jwt')
    def test_entitlementid_gocentral(self, mocked_get_jwt, mocked_post):
        mocked_get_jwt.return_value = 'jwt123'
        self.assertEqual(self._subscriptions_api.find_product_by_entitlement("customer", "entitlement"), [{'product': "GoCentral", 'domain': "example.com"}])

    @patch.object(requests, 'get', return_value=MockResponse({"customerId": "not-a-real-uuid", "subscriptionId": "diablo:591263339", "uri": "/customers/not-a-real-uuid/subscriptions/diablo:591263339", "metadata": {"revision": 1, "modifiedAt": "2022-10-13T14:31:48.000Z", "createdAt": "2022-10-13T09:41:00.000Z"}, "status": "ACTIVE", "statusUpdatedAt": "2022-10-13T14:31:48Z", "paidThroughDate": "2022-11-13T07:00:00Z", "canBeRenewed": True, "offer": {"uri": "/customers/not-a-real-uuid/offers/8b8af56e-1453-4ce3-8cfd-e466f886eb03", "autoRenew": False, "term": {"termType": "MONTH", "numberOfTerms": 1}, "products": [{"key": "0118a064-43ef-4569-998a-68a910b6d2d1", "product": {"productFamily": "hosting", "uri": "/customers/not-a-real-uuid/products/5dc57ceb-3ad1-4b89-b700-4bb6313f084f", "plan": "economy", "resourceType": "product", "productType": "virtualPrivateServerHostingV4", "planTier": 2000}}], "plan": "economy"}, "linkedEntitlements": [{"productKey": "0118a064-43ef-4569-998a-68a910b6d2d1", "entitlementUri": "/customers/not-a-real-uuid/entitlements/20538a1d-4adb-11ed-828e-3417ebe724ff", "commonName": "example.com", "i18nKey": "bm90cmVhbGJhc2U2NAo="}], "commonName": "example.com", "i18nKey": "bm90cmVhbGJhc2U2NAo="}, 200, Mock(return_value='')))
    @patch.object(EntitlementsAPI, '_get_jwt')
    def test_entitlementid_VPS4(self, mocked_get_jwt, mocked_post):
        mocked_get_jwt.return_value = 'jwt123'
        self.assertEqual(self._subscriptions_api.find_product_by_entitlement("customer", "entitlement"), [{'product': "VPS4", 'domain': "example.com"}])

    @patch.object(requests, 'get', return_value=MockResponse({"customerId": "not-a-real-uuid", "subscriptionId": "diablo:591263339", "uri": "/customers/not-a-real-uuid/subscriptions/diablo:591263339", "metadata": {"revision": 1, "modifiedAt": "2022-10-13T14:31:48.000Z", "createdAt": "2022-10-13T09:41:00.000Z"}, "status": "ACTIVE", "statusUpdatedAt": "2022-10-13T14:31:48Z", "paidThroughDate": "2022-11-13T07:00:00Z", "canBeRenewed": True, "offer": {"uri": "/customers/not-a-real-uuid/offers/8b8af56e-1453-4ce3-8cfd-e466f886eb03", "autoRenew": False, "term": {"termType": "MONTH", "numberOfTerms": 1}, "products": [{"key": "0118a064-43ef-4569-998a-68a910b6d2d1", "product": {"productFamily": "hosting", "uri": "/customers/not-a-real-uuid/products/5dc57ceb-3ad1-4b89-b700-4bb6313f084f", "plan": "economy", "resourceType": "product", "productType": "plesk", "planTier": 2000}}], "plan": "economy"}, "linkedEntitlements": [{"productKey": "0118a064-43ef-4569-998a-68a910b6d2d1", "entitlementUri": "/customers/not-a-real-uuid/entitlements/20538a1d-4adb-11ed-828e-3417ebe724ff", "commonName": "example.com", "i18nKey": "bm90cmVhbGJhc2U2NAo="}], "commonName": "example.com", "i18nKey": "bm90cmVhbGJhc2U2NAo="}, 200, Mock(return_value='')))
    @patch.object(EntitlementsAPI, '_get_jwt')
    def test_entitlementid_plesk(self, mocked_get_jwt, mocked_post):
        mocked_get_jwt.return_value = 'jwt123'
        self.assertEqual(self._subscriptions_api.find_product_by_entitlement("customer", "entitlement"), [{'product': "Plesk", 'domain': "example.com"}])

    @patch.object(requests, 'get', return_value=MockResponse({"customerId": "not-a-real-uuid", "subscriptionId": "diablo:591263339", "uri": "/customers/not-a-real-uuid/subscriptions/diablo:591263339", "metadata": {"revision": 1, "modifiedAt": "2022-10-13T14:31:48.000Z", "createdAt": "2022-10-13T09:41:00.000Z"}, "status": "ACTIVE", "statusUpdatedAt": "2022-10-13T14:31:48Z", "paidThroughDate": "2022-11-13T07:00:00Z", "canBeRenewed": True, "offer": {"uri": "/customers/not-a-real-uuid/offers/8b8af56e-1453-4ce3-8cfd-e466f886eb03", "autoRenew": False, "term": {"termType": "MONTH", "numberOfTerms": 1}, "products": [{"key": "0118a064-43ef-4569-998a-68a910b6d2d1", "product": {"productFamily": "hosting", "uri": "/customers/not-a-real-uuid/products/5dc57ceb-3ad1-4b89-b700-4bb6313f084f", "plan": "enhanceWhmcs", "resourceType": "product", "productType": "cpanel", "planTier": 2000}}], "plan": "enhanceWhmcs"}, "linkedEntitlements": [{"productKey": "0118a064-43ef-4569-998a-68a910b6d2d1", "entitlementUri": "/customers/not-a-real-uuid/entitlements/20538a1d-4adb-11ed-828e-3417ebe724ff", "commonName": "example.com", "i18nKey": "bm90cmVhbGJhc2U2NAo="}], "commonName": "example.com", "i18nKey": "bm90cmVhbGJhc2U2NAo="}, 200, Mock(return_value='')))
    @patch.object(EntitlementsAPI, '_get_jwt')
    def test_entitlementid_whms(self, mocked_get_jwt, mocked_post):
        mocked_get_jwt.return_value = 'jwt123'
        self.assertEqual(self._subscriptions_api.find_product_by_entitlement("customer", "entitlement"), [{'product': "Diablo WHMCS", 'domain': "example.com"}])

    @patch.object(requests, 'get', return_value=MockResponse({"customerId": "not-a-real-uuid", "subscriptionId": "diablo:591263339", "uri": "/customers/not-a-real-uuid/subscriptions/diablo:591263339", "metadata": {"revision": 1, "modifiedAt": "2022-10-13T14:31:48.000Z", "createdAt": "2022-10-13T09:41:00.000Z"}, "status": "ACTIVE", "statusUpdatedAt": "2022-10-13T14:31:48Z", "paidThroughDate": "2022-11-13T07:00:00Z", "canBeRenewed": True, "offer": {"uri": "/customers/not-a-real-uuid/offers/8b8af56e-1453-4ce3-8cfd-e466f886eb03", "autoRenew": False, "term": {"termType": "MONTH", "numberOfTerms": 1}, "products": [{"key": "0118a064-43ef-4569-998a-68a910b6d2d1", "product": {"productFamily": "hosting", "uri": "/customers/not-a-real-uuid/products/5dc57ceb-3ad1-4b89-b700-4bb6313f084f", "plan": "enhanceWhmcs", "resourceType": "product", "productType": "cpanel", "planTier": 2000}}, {"key": "00000000-43ef-4569-998a-68a910b6d2d1", "product": {"productFamily": "hosting", "uri": "/customers/not-a-real-uuid/products/5dc57ceb-3ad1-4b89-b700-4bb6313f084f", "plan": "enhanceWhmcs", "resourceType": "product", "productType": "plesk", "planTier": 2000}}], "plan": "enhanceWhmcs"}, "linkedEntitlements": [{"productKey": "0118a064-43ef-4569-998a-68a910b6d2d1", "entitlementUri": "/customers/not-a-real-uuid/entitlements/20538a1d-4adb-11ed-828e-3417ebe724ff", "commonName": "example.com", "i18nKey": "bm90cmVhbGJhc2U2NAo="}, {"productKey": "00000000-43ef-4569-998a-68a910b6d2d1", "entitlementUri": "/customers/not-a-real-uuid/entitlements/20538a1d-4adb-11ed-828e-3417ebe724ff", "commonName": "newexample.com", "i18nKey": "bm90cmVhbGJhc2U2NAo="}], "commonName": "example.com", "i18nKey": "bm90cmVhbGJhc2U2NAo="}, 200, Mock(return_value='')))
    @patch.object(EntitlementsAPI, '_get_jwt')
    def test_entitlementid_multiple(self, mocked_get_jwt, mocked_post):
        mocked_get_jwt.return_value = 'jwt123'
        self.assertEqual(self._subscriptions_api.find_product_by_entitlement("customer", "entitlement"), [{'product': "Diablo WHMCS", 'domain': "example.com"}, {'product': "Plesk", 'domain': "newexample.com"}])
