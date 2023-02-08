import requests
from csetutils.flask.logging import get_logging

from service.products.product_interface import Product


class DiabloAPI(Product):
    _headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    def __init__(self, settings):
        self._logger = get_logging()
        self.url = settings.DIABLO_URL
        self.auth = (settings.DIABLO_USER, settings.DIABLO_PASS)

    def locate(self, domain: str, guid: str = None, **kwargs: str) -> dict:

        try:
            if guid:
                r = requests.get(self.url + "/" + guid, auth=self.auth, headers=self._headers, verify=False)
                returned_json = r.json()
                return {
                    'guid': guid,
                    'shopper_id': returned_json.get('shopper_id'),
                    'reseller_id': returned_json.get('reseller_id'),
                    'created_date': returned_json.get('created_at'),
                    'ip': returned_json.get('shared_ip_address'),
                    'username': returned_json.get('username'),
                    'os': 'Linux',
                    'product': 'Diablo',
                    'entitlement_id': guid
                }
            payload = {'name': domain}
            r = requests.get(f'{self.url}/find_domain', auth=self.auth, headers=self._headers, params=payload, verify=False)
            returned_json = r.json()

            diablo_account = None
            # We found just a single account, this is easy mode.
            if returned_json.get('id'):
                diablo_account = returned_json
            elif len(returned_json.get('data', [])) > 0:
                all_accounts = [x for x in returned_json.get('data') if x.get('type') == 'account']
                # If there is anything besides one account returned let the analyst sort it out.
                if len(all_accounts) == 1:
                    diablo_account = all_accounts[0]
            else:
                self._logger.info('No data value received from Diablo request')

            if diablo_account:
                return {
                    'guid': diablo_account.get('orion_guid'),
                    'shopper_id': diablo_account.get('shopper_id'),
                    'entitlement_id': diablo_account.get('orion_guid'),
                    'created_date': diablo_account.get('created_at'),
                    'ip': diablo_account.get('shared_ip_address'),
                    'username': diablo_account.get('username'),
                    'os': 'Linux',
                    'product': 'Diablo'
                }

        except Exception as e:
            self._logger.error('Failed Diablo Lookup: {}'.format(e))
        return {}
