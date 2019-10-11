import logging

import requests

from service.products.product_interface import Product


class CNDNSAPI(Product):
    _headers = {'accept': 'application/json'}

    def __init__(self, settings):
        self._logger = logging.getLogger(__name__)
        self._url = settings.CNDNS_URL

    def locate(self, domain, **kwargs):
        """
        Given a domain, retrieve Orion related information in case of CNDNS domains.
        :param domain:
        :return:
        """

        try:
            cnds_domains_url = self._url + 'domains/{}/account'.format(domain)
            r = requests.get(cnds_domains_url, headers=self._headers)
            response = r.json()
            for record in response.get('records'):
                if record.get('orionGuid'):
                    return {
                        'guid': record.get('orionGuid'),
                        'shopper_id': record.get('shopperId'),
                        'product': 'WSBD'
                    }

        except Exception as e:
            self._logger.error('Failed CNDNS Lookup. Details: {}'.format(e))
