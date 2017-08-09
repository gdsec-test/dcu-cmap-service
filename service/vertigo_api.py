import logging
import requests
import socket


class VertigoApi(object):

    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    def __init__(self, settings):
        self.url = settings.VERT_URL
        self.auth = (settings.CMAP_PROXY_USER, settings.CMAP_PROXY_PASS)
        self.cert = (settings.CMAP_PROXY_CERT, settings.CMAP_PROXY_KEY)

    def guid_query(self, domain):

        requests.packages.urllib3.disable_warnings()

        try:

            ip = socket.gethostbyname(domain)

            response = requests.get(self.url + ip, cert=self.cert, auth=self.auth, headers=self.headers, verify=False)
            returned_json = response.json()

            if returned_json.get('data', False):
                guid = returned_json['data'][0].get('accountUid', None)
                shopper_id = returned_json['data'][0].get('shopperId', None)
                os = returned_json['data'][0].get('template_name', None)
                return {'guid': guid, 'shopper_id': shopper_id, 'os': os}

        except Exception as e:
            logging.error("Failed Vertigo Lookup: %s", e.message)

        return None
