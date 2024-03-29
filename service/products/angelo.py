import requests
from csetutils.flask.logging import get_logging

from service.products.product_interface import Product


class AngeloAPI(Product):
    _headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    def __init__(self, settings):
        self._logger = get_logging()
        self.url = settings.ANGELO_URL
        self.auth = (settings.ANGELO_USER, settings.ANGELO_PASS)

    def locate(self, domain, ip, **kwargs):
        """
        Given a domain, retrieve the guid, shopperId, and private label if associated with an Angelo product.
        :param domain:
        :param kwargs:
        :return:
        """

        try:
            r = requests.post(self.url + 'addonDomain=' + domain + '&serverIp=' + ip,
                              auth=self.auth, headers=self._headers)

            if r.status_code == 200:
                returned_json = r.json()
                guid = str(returned_json.get('orion_id'))
                shopper_id = str(returned_json.get('shopper_id'))
                reseller_id = str(returned_json.get('reseller_id'))

                return {'guid': guid, 'shopper_id': shopper_id, 'os': 'Windows', 'reseller_id': reseller_id,
                        'product': 'Plesk', 'entitlement_id': guid}

            elif r.status_code == 400:
                self._logger.info(r.text)

            self._logger.info('Failed Angelo Lookup')
        except Exception as e:
            self._logger.error('Failed Angelo Lookup: {}'.format(e))
