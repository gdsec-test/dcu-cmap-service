import logging

import requests

from service.products.product_interface import Product


class MWPOneAPI(Product):
    _headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    def __init__(self, settings):
        self._logger = logging.getLogger(__name__)
        self.url = settings.MWPONE_URL
        self.auth = (settings.MWP_ONE_USER, settings.MWP_ONE_PASS)

    def locate(self, domain, **kwargs):
        """
        This functions sole purpose is to locate all data for a MWP 1.0 account to be placed into the data
        sub document of the incident's mongo document
        :param domain:
        :param kwargs:
        :return:
        """
        response = {}

        try:
            r = requests.get(self.url + domain, auth=self.auth, headers=self._headers, verify=False)
            response = r.json()
        except Exception as e:
            self._logger.error(e)

        for entry in response.get('data', []):
            if entry.get('statusId') != 1:
                continue

            return {
                'guid': entry.get('accountUid'),
                'account_id': entry.get('id'),
                'shopper_id': entry.get('shopperId'),
                'os': 'Linux',
                'data_center': self._dc_helper(entry.get('dataCenter', {}).get('description')),
                'product': 'MWP 1.0',
                'ip': entry.get('ipAddress'),
                'hostname': 'MWP 1.0 does not return hostname',
                'created_date': entry.get('dateCreated')
            }
        else:
            self._logger.info('No active MWP 1.0 account ID found for {}'.format(domain))

    def _dc_helper(self, dc):
        if dc == 'Buckeye':
            dc = 'P3'
        elif dc == 'Ashburn':
            dc = 'A2'
        elif dc == 'Amsterdam':
            dc = 'N1'
        return dc
