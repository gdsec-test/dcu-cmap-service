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
        failure_msg = 'Failed CNDNS Lookup.'
        try:
            cnds_domains_url = self._url + 'domains/{}/account'.format(domain)
            r = requests.get(cnds_domains_url, headers=self._headers)
            # To avoid running json() on a 404 response
            if r.status_code == 200:
                response = r.json()
                for record in response.get('records'):
                    if record.get('orionGuid'):
                        return {
                            'guid': record.get('orionGuid'),
                            'shopper_id': record.get('shopperId'),
                            'product': 'WSBD'
                        }
                self._logger.error('{} orionGuid not found'.format(failure_msg))
            else:
                self._logger.error('{} Call to API returned status code {}'.format(failure_msg, r.status_code))

        except Exception as e:
            self._logger.error('{} Details: {}'.format(failure_msg, e))
