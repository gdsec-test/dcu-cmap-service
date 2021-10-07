import requests
from dcustructuredloggingflask.flasklogger import get_logging

from service.products.product_interface import Product


class DiabloAPI(Product):
    _headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    def __init__(self, settings):
        self._logger = get_logging()
        self.url = settings.DIABLO_URL
        self.auth = (settings.DIABLO_USER, settings.DIABLO_PASS)

    def locate(self, domain, guid, **kwargs):
        """
        Given a domain, retrieve the guid, shopperId, create date, IP address, etc. if associated with a Diablo product.
        :param domain:
        :param kwargs:
        :return:
        """
        try:
            self._logger.info("made it here!!!!!!!!!!!!!!!!: " + guid)
            if guid:
                self._logger.info("chose the guid: " + guid)
                r = requests.get(self.url + "/" + guid, auth=self.auth, headers=self._headers, verify=False)
                returned_json = r.json()
                self._logger.info("created at :" + returned_json.get('created_at'))
                return {
                    'guid': returned_json.get('orion_guid'),
                    'shopper_id': returned_json.get('shopper_id'),
                    'created_date': returned_json.get('created_at'),
                    'ip': returned_json.get('shared_ip_address'),
                    'os': 'Linux',
                    'product': 'Diablo'
                }

            self._logger.info("chose the domain: " + domain)
            r = requests.get(self.url + "?addon_domain_eq=" + domain, auth=self.auth, headers=self._headers, verify=False)
            returned_json = r.json()

            if returned_json.get('data'):
                entry = returned_json.get('data', [{}])[0]

                return {
                    'guid': entry.get('orion_guid'),
                    'shopper_id': entry.get('shopper_id'),
                    'created_date': entry.get('created_at'),
                    'ip': entry.get('shared_ip_address'),
                    'os': 'Linux',
                    'product': 'Diablo'
                }
            else:
                self._logger.info('No data value received from Diablo request')

        except Exception as e:
            self._logger.error('Failed Diablo Lookup: {}'.format(e))
        return {}
