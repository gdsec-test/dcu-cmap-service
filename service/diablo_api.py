import requests
import ast
import logging


class DiabloApi(object):

    url = 'https://cpanelprovapi.prod.phx3.secureserver.net/v1/accounts?addon_domain_eq='
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    def __init__(self, settings):
        self.user = settings.DIABLOUSER
        self.pwd = settings.DIABLOPASS

    def guid_query(self, domain):

        requests.packages.urllib3.disable_warnings()

        try:

            r = requests.get(self.url + domain, auth=(self.user, self.pwd), headers=self.headers, verify=False)
            returned_json = r.json()

            if returned_json['data']:
                guid = returned_json['data'][0]['orion_guid']
                return guid

            elif r.status_code == 400:
                t = ast.literal_eval(r.text)
                logging.info(t)
                return None

        except Exception as e:
            logging.error(e.message)
            return None