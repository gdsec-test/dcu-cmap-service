import requests
from dcustructuredloggingflask.flasklogger import get_logging

from service.products.product_interface import Product


class VertigoAPI(Product):
    _headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    def __init__(self, settings):
        self._logger = get_logging()
        self.url = settings.VERT_URL
        self.auth = (settings.CMAP_PROXY_USER, settings.CMAP_PROXY_PASS)
        self.cert = (settings.CMAP_PROXY_CERT, settings.CMAP_PROXY_KEY)

    def locate(self, domain, ip, **kwargs):

        try:
            response = requests.get(self.url + ip, cert=self.cert, auth=self.auth, headers=self._headers, verify=False)
            returned_json = response.json()

            if returned_json.get('data'):
                data = returned_json.get('data', [{}])[0]
                managed_string = data.get('managedLevelString', '')
                self._logger.info(f'managedLevelString: {managed_string}')

                return {
                    'guid': data.get('accountUid'),
                    'container_id': data.get('id'),
                    'created_data': data.get('created'),
                    'friendly_name': data.get('friendlyName'),
                    'shopper_id': data.get('shopperId'),
                    'os': data.get('template_name'),
                    'managed_level': managed_string.replace(' ', ''),
                    'product': 'Vertigo'
                }
        except Exception as e:
            self._logger.error('Failed Vertigo Lookup: {}'.format(e))
        return None
