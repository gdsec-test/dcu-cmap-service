import logging
import socket

from requests import sessions, packages


class VertigoApi(object):

    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    def __init__(self, settings):
        self._logger = logging.getLogger(__name__)
        self.url = settings.VERT_URL
        self.auth = (settings.CMAP_PROXY_USER, settings.CMAP_PROXY_PASS)
        self.cert = (settings.CMAP_PROXY_CERT, settings.CMAP_PROXY_KEY)

    def guid_query(self, domain):

        packages.urllib3.disable_warnings()

        try:

            ip = socket.gethostbyname(domain)

            with sessions.Session() as session:
                response = session.get(self.url + ip, cert=self.cert, auth=self.auth, headers=self.headers, verify=False)
            returned_json = response.json()

            if returned_json.get('data', False):
                guid = returned_json['data'][0].get('accountUid', None)
                created_date = returned_json['data'][0].get('created', None)
                friendly_name = returned_json['data'][0].get('friendlyName', None)
                shopper_id = returned_json['data'][0].get('shopperId', None)
                os = returned_json['data'][0].get('template_name', None)
                return {'guid': guid, 'created_date': created_date, 'friendly_name': friendly_name,
                        'shopper_id': shopper_id, 'os': os}

        except Exception as e:
            self._logger.error("Failed Vertigo Lookup: %s", e.message)

        return None
