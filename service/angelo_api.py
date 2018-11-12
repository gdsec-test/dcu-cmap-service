import ast
import logging
import socket

from requests import packages, sessions


class AngeloApi(object):
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    def __init__(self, settings):
        self._logger = logging.getLogger(__name__)
        self.url = settings.ANGELO_URL
        self.auth = (settings.ANGELO_USER, settings.ANGELO_PASS)

    def guid_query(self, domain):

        packages.urllib3.disable_warnings()

        try:

            ip = socket.gethostbyname(domain)
            with sessions.Session() as session:
                r = session.post(self.url + 'addonDomain=' + domain + '&serverIp=' + ip,
                                 auth=self.auth, headers=self.headers, verify=False)
            if r.status_code == 200:
                returned_json = r.json()
                guid = str(returned_json.get('orion_id'))
                shopper_id = str(returned_json.get('shopper_id'))
                private_label_id = str(returned_json.get('reseller_id'))
                os = 'Windows'
                return {'guid': guid, 'shopper_id': shopper_id, 'os': os, 'private_label_id': private_label_id}

            elif r.status_code == 400:
                t = ast.literal_eval(r.text)
                self._logger.info(t)

            self._logger.error("Failed Angelo Lookup")

        except Exception as e:
            self._logger.error("Failed Angelo Lookup: %s", e.message)

        return None
