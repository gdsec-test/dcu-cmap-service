import requests
import ast
import logging


class DiabloApi(object):

    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    def __init__(self, settings):
        self.url = settings.DIABLO_URL
        self.auth = (settings.DIABLOUSER, settings.DIABLOPASS)

    def guid_query(self, domain):

        requests.packages.urllib3.disable_warnings()

        try:

            r = requests.get(self.url + domain, auth=self.auth, headers=self.headers, verify=False)
            returned_json = r.json()

            if returned_json.get('data', False):
                guid = returned_json['data'][0].get('orion_guid')
                shopper = returned_json['data'][0].get('shopper_id')
                os = 'Linux'
                return {'guid': guid, 'shopper': shopper, 'os': os}

            elif r.status_code == 400:
                t = ast.literal_eval(r.text)
                logging.info(t)

            logging.error("Failed Diablo Lookup")

        except Exception as e:
            logging.error("Failed Diablo Lookup: %s", e.message)

        return None
