import requests
from dcustructuredloggingflask.flasklogger import get_logging

from service.products.product_interface import Product


class CNDNSAPI(Product):
    _headers = {'accept': 'application/json'}

    """
    duda: Arabic Website Builder Product
    wopop: Website Builder Product for chinese markets including Taiwan, Hong Kong and Singapore
    """
    _partner_product_map = {'duda': 'WSBA', 'wopop': 'WSBD'}

    def __init__(self, settings):
        self._logger = get_logging()
        self._url = settings.CNDNS_URL
        self._cert = (settings.CMAP_SERVICE_CERT, settings.CMAP_SERVICE_KEY)

    def locate(self, domain, **kwargs):
        """
        Given a domain, retrieve Orion related information in case of CNDNS domains.
        :param domain:
        :return dictionary with product related information:

        Sample of the json object returned from the Abuse Partners API:
        API Spec: https://abuse.partners.int.godaddy.com/v1/docs/
        {
            "siteId": "29c99f84736e457e964ba395abaca62a",
            "records": [
                {
                    "partner": "duda",
                    "orionGuid": "177411d8-b65f-11ea-811a-0050569a4acb",
                    "shopperId": "1111333"
                }
          ]
        }
        """
        failure_msg = 'Failed CNDNS Lookup.'
        try:
            cnds_domains_url = self._url + 'domains/{}/account'.format(domain)
            r = requests.get(cnds_domains_url, headers=self._headers, cert=self._cert)
            # To avoid running json() on a 404 response
            if r.status_code == 200:
                response = r.json()
                for record in response.get('records', []):
                    partner = record.get('partner', '')
                    if record.get('orionGuid') and partner in self._partner_product_map.keys():
                        return {
                            'guid': record.get('orionGuid'),
                            'shopper_id': record.get('shopperId'),
                            'product': self._partner_product_map.get(partner)
                        }
                self._logger.info('{} orionGuid not found'.format(failure_msg))
            else:
                self._logger.info('{} Call to API returned status code {}'.format(failure_msg, r.status_code))

        except Exception as e:
            self._logger.error('{} Details: {}'.format(failure_msg, e))

        return {}
