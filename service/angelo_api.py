import requests
import socket
import ast
import logging


class AngeloApi(object):

    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    def __init__(self, settings):
        self.url = settings.ANGELO_URL
        self.auth = (settings.ANGELOUSER, settings.ANGELOPASS)

    def guid_query(self, domain):

        requests.packages.urllib3.disable_warnings()

        try:

            ip = socket.gethostbyname(domain)
            r = requests.post(self.url + 'addonDomain=' + domain + '&serverIp=' + ip,
                              auth=self.auth, headers=self.headers, verify=False)
            if r.status_code == 200:
                returned_json = r.json()
                guid = str(returned_json.get('orion_id', None))
                shopper = str(returned_json.get('shopper_id', None))
                os = 'Windows'
                return {'guid': guid, 'shopper': shopper, 'os': os}

            elif r.status_code == 400:
                t = ast.literal_eval(r.text)
                logging.info(t)

            logging.error("Failed Angelo Lookup")

        except Exception as e:
            logging.error("Failed Angelo Lookup: %s", e.message)

        return None
