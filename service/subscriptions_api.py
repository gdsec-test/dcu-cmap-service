import json
import logging
from urllib import urlencode

import requests


class SubscriptionsAPI(object):
    VALID_SUBSCRIPTION_STATUSES = {'ACTIVE', 'TRIAL PERIOD', 'FREE'}

    def __init__(self, settings):
        self._logger = logging.getLogger(__name__)
        self._url = settings.SUBSCRIPTIONS_URL
        self._cert = (settings.SUBSCRIPTIONS_CERT, settings.SUBSCRIPTIONS_KEY)

    def has_hosting_subscription(self, shopper_id, domain):
        """
        This function's sole purpose is to use the available subscriptions api to determine if a shopper has
        any hosting subscriptions associated with a domain name.
        :param: shopper_id:
        :param: domain:
        :return: Dict with subscription info if a subscription is associated with the domain name
        """
        domain = domain.lower() if domain else None
        product_group_keys = ['hosting', 'websiteBuilder', 'servers', 'wordpress']
        handled_hosting_products = {'diablo': 'Diablo', 'wpaas': 'MWP 1.0', 'angelo': 'Angelo'}

        subscriptions = self._get_subscriptions(shopper_id, product_group_keys)

        for subscription in subscriptions:
            label = subscription.get('label').lower() if subscription.get('label') else None
            if subscription.get('status') in self.VALID_SUBSCRIPTION_STATUSES and label == domain:
                namespace = subscription.get('product', {}).get('namespace')
                if namespace in handled_hosting_products:
                    subscription.get('product', {}).update(product_name=handled_hosting_products[namespace])
                    return subscription
        return {}

    def _get_subscriptions(self, shopper_id, product_group_keys):
        """
        This function's sole purpose is to use the available subscriptions api to determine
        the subscriptions associated with a particular shopper and product groups.
        :param: shopper_id:
        :param: product_group_keys:
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
        # Page size represents the number of subscriptions that are to be retrieved in one call.
        page_size = 1000
        headers = {'content-type': 'application/json', 'X-Shopper-Id': shopper_id}
        query_params = {'productGroupKeys': product_group_keys, 'offset': 0, 'limit': page_size}

        '''
        The doseq parameter in urlencode, when True, converts each sequence element in a sequence (list)
        into a separate parameter. For instance productGroupKeys = ['hosting', 'domains']
        gets converted into productGroupKeys=hosting&productGroupKeys=domains in the url.
        '''
        query_url = '{}?{}'.format(self._url, urlencode(query_params, doseq=True))

        subscriptions = []
        try:
            while True:
                r = requests.get(query_url, headers=headers, cert=self._cert)
                res = json.loads(r.text)
                subscriptions += res.get('subscriptions', [])
                next_page = res.get('pagination', {}).get('next')
                if not next_page:
                    break
                query_url = next_page
        except Exception as e:
            self._logger.error("Exception thrown for {}: msg:{}.".format(shopper_id, e.message))
        return subscriptions
