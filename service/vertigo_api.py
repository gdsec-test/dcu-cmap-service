import logging
import requests
import socket


class VertigoApi(object):

    url = 'https://vertigo.godaddy.com/vertigo/v1/container/?ips__ipv4='
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    def __init__(self, settings):
        self.user = settings.VERTIGOUSER
        self.pwd = settings.VERTIGOPASS

    def guid_query(self, domain):

        requests.packages.urllib3.disable_warnings()

        try:

            ip = socket.gethostbyname(domain)

            response = requests.get(self.url + ip, auth=(self.user, self.pwd), headers=self.headers, verify=False)
            returned_json = response.json()

            if returned_json['data']:
                guid = returned_json['data'][0]['accountUid']
                shopper = returned_json['data'][0]['shopperId']
                os = returned_json['data'][0]['template_name']
                return {'guid': guid, 'shopper': shopper, 'os': os}

            return None

        except Exception as e:
            logging.error(e.message)
            return None