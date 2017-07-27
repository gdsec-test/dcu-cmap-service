import requests
import ast
import logging


class DiabloApi(object):

    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    def __init__(self, settings):
        self.user = settings.DIABLOUSER
        self.pwd = settings.DIABLOPASS
        self.url = settings.DIABLO_URL

    def guid_query(self, domain):

        requests.packages.urllib3.disable_warnings()

        try:

            r = requests.get(self.url + domain, auth=(self.user, self.pwd), headers=self.headers, verify=False)
            returned_json = r.json()

            if returned_json.get('data', False):
                guid = returned_json['data'][0].get('orion_guid')
                shopper = returned_json['data'][0].get('shopper_id')
                os = 'Linux'
                return {'guid': guid, 'shopper': shopper, 'os': os}

            elif r.status_code == 400:
                t = ast.literal_eval(r.text)
                logging.info(t)

        except Exception as e:
            logging.error(e.message)

        return None
