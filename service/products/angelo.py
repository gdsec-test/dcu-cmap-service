import ast
import socket

import requests
from dcustructuredloggingflask.flasklogger import get_logging

from service.products.product_interface import Product


class AngeloAPI(Product):
    _headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    def __init__(self, settings):
        self._logger = get_logging()
        self.url = settings.ANGELO_URL
        self.auth = (settings.ANGELO_USER, settings.ANGELO_PASS)

    def locate(self, domain, **kwargs):
        """
        Given a domain, retrieve the guid, shopperId, and private label if associated with an Angelo product.
        :param domain:
        :param kwargs:
        :return:
        """

        try:
            ip = socket.gethostbyname(domain)
            r = requests.post(self.url + 'addonDomain=' + domain + '&serverIp=' + ip,
                              auth=self.auth, headers=self._headers, verify=False)

            if r.status_code == 200:
                returned_json = r.json()
                guid = str(returned_json.get('orion_id'))
                shopper_id = str(returned_json.get('shopper_id'))
                private_label_id = str(returned_json.get('reseller_id'))

                return {'guid': guid, 'shopper_id': shopper_id, 'os': 'Windows', 'private_label_id': private_label_id, 'product': 'Plesk'}

            elif r.status_code == 400:
                t = ast.literal_eval(r.text)
                self._logger.info(t)

            self._logger.info('Failed Angelo Lookup')
        except Exception as e:
            self._logger.error('Failed Angelo Lookup: {}'.format(e))
