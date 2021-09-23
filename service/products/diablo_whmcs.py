import requests
from dcustructuredloggingflask.flasklogger import get_logging

from service.products.product_interface import Product


class DiabloAPIWHMCS(Product):
    _headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    def __init__(self, settings):
        self._logger = get_logging()
        self.url = settings.DIABLO_WHMCS_URL
        self.auth = (settings.DIABLO_USER, settings.DIABLO_PASS)

    def locate(self, ip: str) -> dict:
        """
        Given an IP, retrieve account details when associated with a Diablo WHMCS product.
        NOTE: Although this endpoint is meant to be specific to the WHMCS product, it *sometimes* returns info
        for non-WHMCS Diablo plans, so we need to account for and differentiate those depending on the response.
        """
        result = {}
        try:
            r = requests.get(f'{self.url}{ip}/list_whmcs_accounts_info', auth=self.auth, headers=self._headers)
            returned_json = r.json()

            if isinstance(returned_json, dict):
                entry = returned_json.get('c1_account')

                # NOTE: not grabbing username as C1 home dir is not typically the location of reported content
                result = {
                    'guid': entry.get('orion_guid'),
                    'shopper_id': entry.get('shopper_id'),
                    'created_date': entry.get('created_at'),
                    'ip': entry.get('shared_ip_address'),
                    'os': 'Linux',
                    'product': 'Diablo WHMCS',
                    'reseller_id': entry.get('reseller_id')
                }

                # If no C2 info, treat as a non-WHMCS Diablo plan
                if returned_json.get('c2_accounts') == [{}]:
                    result.update({
                        'product': 'Diablo',
                        'username': entry.get('username')
                    })
            else:
                self._logger.info(f'No dictionary value received from Diablo WHMCS for {ip}')

        except Exception as e:
            self._logger.error(f'Failed Diablo WHMCS Lookup: {e}')

        return result
