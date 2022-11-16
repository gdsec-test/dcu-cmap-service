import json
from urllib.parse import urlencode

import requests
from csetutils.flask.logging import get_logging


class SubscriptionsAPI(object):
    valid_subscription_statuses = {'ACTIVE', 'TRIAL PERIOD', 'FREE'}

    def __init__(self, config):
        self._logger = get_logging()
        self._url = config.SUBSCRIPTIONS_URL
        self._sso_url = config.SSO_URL
        self._cert = (config.CMAP_SERVICE_CLIENT_CERT, config.CMAP_SERVICE_CLIENT_KEY)
        self._blacklist = config.SUBSCRIPTIONS_BLACKLIST
        self._jwt = None

    def get_hosting_subscriptions(self, shopper_id, domain):
        """
        Uses the Subscriptions API to determine if a shopper has any hosting subscriptions associated with the
        provided domain name.

        At this time, the Subscriptions API _cannot_ be used to determine information about older Dedicated ,
        Virtual Dedicated, or Virtual Private Hosting.
        :param: shopper_id:
        :param: domain:
        :return: Dict with subscription info if a subscription is associated with the domain name
        """
        domain = domain.lower() if domain else None
        product_group_keys = ['hosting', 'websiteBuilder', 'wordpress']
        handled_hosting_products = {'diablo',       # hosting
                                    'angelo',       # hosting
                                    'wpaas',        # wordpress
                                    'mwp2',         # wordpress
                                    'wsb',          # websiteBuilder
                                    'wst'           # websiteBuilder
                                    }

        subscriptions = self._get_subscriptions(shopper_id, product_group_keys, domain)

        for subscription in subscriptions:
            label = subscription.get('label').lower() if subscription.get('label') else ""
            namespace = subscription.get('product', {}).get('namespace')

            if subscription.get('status') in self.valid_subscription_statuses and self._check_label(label, domain,
                                                                                                    namespace):
                if namespace in handled_hosting_products:
                    return subscription
        return {}

    def get_sucuri_subscriptions(self, shopper_id, domain):
        """
        Uses the Subscriptions API to determine if the a shopper has any Sucuri Subscriptions associated with a
        domain name that is registered within the same shopper and return the product labels.
        :param: shopper_id:
        :param: domain:
        :return: List with sucuri subscription info if there are any sucuri product(s) associated with the domain name
        """
        product_group_keys = ['websiteSecurity']
        subscriptions = self._get_subscriptions(shopper_id, product_group_keys, domain)
        security_subscription = []
        for subscription in subscriptions:
            if subscription.get('status') in self.valid_subscription_statuses and subscription.get('product', {}).get(
                    'productGroupKey') == 'websiteSecurity':
                security_subscription.append(subscription.get('product', {}).get('label'))
        return security_subscription

    def get_ssl_subscriptions(self, shopper_id, domain):
        """
        Uses the Subscriptions API to determine if the a shopper has any SSL Subscriptions associated with a
        domain name that is registered within the same shopper and return the product labels, created & expire dates.
        :param: shopper_id:
        :param: domain:
        :return: List of dicts(s) with ssl subscription info if there are any ssl product(s) associated with the domain
        """
        product_group_keys = ['sslCerts']
        ssl_subscriptions = []
        '''
        Check to ensure that the call to retrieve ssl certs from the Subscriptions API is
        bypassed in case of blacklisted shoppers.
        '''
        if shopper_id in self._blacklist:
            self._logger.info(
                'Bypassing Subscriptions API call to retrieve ssl certs for blacklisted shopper: {}'.format(shopper_id))
            return ssl_subscriptions

        subscriptions = self._get_subscriptions(shopper_id, product_group_keys, domain)
        for subscription in subscriptions:
            if subscription.get('status') in self.valid_subscription_statuses and subscription.get('product', {}).get(
                    'productGroupKey') == 'sslCerts':
                ssl_subscription = {
                    'cert_common_name': subscription.get('label'),
                    'cert_type': subscription.get('product').get('label'),
                    'created_at': subscription.get('createdAt'),
                    'expires_at': subscription.get('expiresAt')
                }
                ssl_subscriptions.append(ssl_subscription)
        return ssl_subscriptions

    def _get_jwt(self, force_refresh: bool = False) -> str:
        if self._jwt is None or force_refresh:
            try:
                response = requests.post(f'{self._sso_url}/v1/secure/api/token',
                                         data={'realm': 'cert'}, cert=self._cert)
                response.raise_for_status()
                sso_response = response.json()
                self._jwt = sso_response.get('data')
            except Exception:
                self._logger.exception('Error calling sso')
                return ""
        return self._jwt

    def _get_subscriptions(self, shopper_id, product_group_keys, domain):
        """
        Uses the Subscriptions API to retrieve the subscriptions associated with a particular shopper
        and product groups.
        :param: shopper_id:
        :param: product_group_keys:
        :param: domain:
        :return: List with all the subscriptions that belong to the shopper.
        """
        '''
        Sample of partial Subscriptions API Return.  More data is returned that could possibly be used in the future.
        Api Spec at https://developer.godaddy.com/doc/endpoint/subscriptions

        {
        "pagination": {
            "total": 2,
            "next": "https://subscription.api.int.godaddy.com/v1/subscriptions?productGroupKeys=%5B'hosting'%2C%20'websiteSecurity'",
            "last": "https://subscription.api.int.godaddy.com/v1/subscriptions?productGroupKeys=%5B'hosting'%2C%20'websiteSecurity'",
            "first": "https://subscription.api.int.godaddy.com/v1/subscriptions?productGroupKeys=%5B'hosting'%2C%20'websiteSecurity'"
            },
        "subscriptions": [
            {
            "status": "ACTIVE",
            "product": {
                "pfid": abc,
                "renewalPeriod": 1,
                "namespace": "domain",
                "renewalPfid": abcd,
                "label": ".COM Domain Registration",
                "productGroupKey": "domains",
                "renewalPeriodUnit": "ANNUAL"
            },
            "billing": {
                "status": "CURRENT",
                "commitment": "PAID",
                "renewAt": "2028-07-04T18:18:31.000Z"
            },
            "upgradeable": true,
            "paymentProfileId": abcd,
            "priceLocked": false,
            "label": "domain.COM",
            "expiresAt": "2028-07-03T18:18:31.000Z",
            "externalId": "abcd",
            "createdAt": "2017-07-03T16:18:25.870Z",
            "subscriptionId": "abcd",
            "renewAuto": true,
            "renewable": true
            },
        ......

        '''
        subscriptions = []
        if not shopper_id:
            return subscriptions

        # Page size represents the number of subscriptions that are to be retrieved in one call.
        page_size = 2000
        headers = {'content-type': 'application/json', 'X-Shopper-Id': shopper_id, 'Authorization': f'sso-jwt {self._get_jwt()}'}
        query_params = {'productGroupKeys': product_group_keys, 'label': domain, 'offset': 0, 'limit': page_size}

        '''
        The doseq parameter in urlencode, when True, converts each sequence element in a sequence (list)
        into a separate parameter. For instance productGroupKeys = ['hosting', 'domains']
        gets converted into productGroupKeys=hosting&productGroupKeys=domains in the url.
        '''
        query_url = '{}?{}'.format(self._url, urlencode(query_params, doseq=True))

        try:
            while True:
                r = requests.get(query_url, headers=headers)
                if r.status_code == 401 or r.status_code == 403:
                    headers['Authorization'] = f'sso-jwt {self._get_jwt(force_refresh=True)}'
                    r = requests.get(query_url, headers=headers)
                r.raise_for_status()
                res = json.loads(r.text)
                subscriptions += res.get('subscriptions', [])
                next_page = res.get('pagination', {}).get('next')
                if not next_page:
                    break
                query_url = next_page
        except Exception as e:
            self._logger.error('Unable to retrieve subscriptions for {}: {}'.format(shopper_id, e))
        return subscriptions

    def _check_label(self, label, domain, namespace):
        """
        Check whether or not the label stored in the Subscriptions information matches the domain we are looking for.

        In some cases, it may be necessary to have specific logic for specific namespaces/products. One of these cases
        is MWP 2.0. In this case, the label is a comma-separated list of all sites associated with a MWP 2.0 plan.
        :param label:
        :param domain:
        :param namespace:
        :return:
        """
        if namespace == 'mwp2':
            return domain in label.split(',')
        return domain == label
