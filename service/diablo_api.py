import ast
import logging

from requests import sessions, packages


class DiabloApi(object):

    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    def __init__(self, settings):
        self._logger = logging.getLogger(__name__)
        self.url = settings.DIABLO_URL
        self.auth = (settings.DIABLO_USER, settings.DIABLO_PASS)

    def guid_query(self, domain):

        packages.urllib3.disable_warnings()

        try:

            with sessions.Session() as session:
                r = session.get(self.url + domain, auth=self.auth, headers=self.headers, verify=False)
            returned_json = r.json()

            if returned_json.get('data', False):
                guid = returned_json['data'][0].get('orion_guid')
                shopper_id = returned_json['data'][0].get('shopper_id')
                os = 'Linux'
                return {'guid': guid, 'shopper_id': shopper_id, 'os': os}

            elif r.status_code == 400:
                t = ast.literal_eval(r.text)
                self._logger.info(t)

            self._logger.error("Failed Diablo Lookup")

        except Exception as e:
            self._logger.error("Failed Diablo Lookup: %s", e.message)

        return None
