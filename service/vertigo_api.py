import logging
import requests
import socket


class VertigoApi(object):

    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    def __init__(self, settings):
        self.user = settings.VERTIGOUSER
        self.pwd = settings.VERTIGOPASS
        self.url = settings.VERT_URL

    def guid_query(self, domain):

        requests.packages.urllib3.disable_warnings()

        try:

            ip = socket.gethostbyname(domain)

            response = requests.get(self.url + ip, auth=(self.user, self.pwd), headers=self.headers, verify=False)
            returned_json = response.json()

            if returned_json['data']:
                guid = returned_json['data'][0].get('accountUid', None)
                shopper = returned_json['data'][0].get('shopperId', None)
                os = returned_json['data'][0].get('template_name', None)
                return {'guid': guid, 'shopper': shopper, 'os': os}

        except Exception as e:
            logging.error(e.message)
            return None