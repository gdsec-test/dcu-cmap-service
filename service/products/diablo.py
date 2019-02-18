import logging

import requests


class DiabloAPI(object):
    _headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    def __init__(self, settings):
        self._logger = logging.getLogger(__name__)
        self.url = settings.DIABLO_URL
        self.auth = (settings.DIABLO_USER, settings.DIABLO_PASS)

    def locate(self, domain):
        """
        Given a domain, retrieve the guid, shopperId, create date, IP address, etc. if associated with a Diablo product.
        :param domain:
        :return:
        """
        try:
            r = requests.get(self.url + domain, auth=self.auth, headers=self._headers, verify=False)
            returned_json = r.json()

            if returned_json.get('data', []):
                entry = returned_json.get('data', [{}])[0]

                return {
                    'guid': entry.get('orion_guid'),
                    'shopper_id': entry.get('shopper_id'),
                    'created_date': entry.get('created_at'),
                    'ip': entry.get('shared_ip_address'),
                    'os': 'Linux'
                }
            else:
                self._logger.error('Failed Diablo Lookup')

        except Exception as e:
            self._logger.error('Failed Diablo Lookup: {}'.format(e))
        return {}
