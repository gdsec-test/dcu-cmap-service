from typing import Optional

import requests


class Netbox(object):

    def __init__(self, url, token):
        self.url = f'{url}/api/ipam/ip-addresses/'
        self.token = token

    def lookup_hostname(self, ip: str) -> Optional[str]:
        hostname = None
        resp = requests.get(
            self.url,
            params={'address': ip},
            headers={'Authorization': f'Token {self.token}', 'Accept': 'application/json'}
        )
        resp.raise_for_status()
        data = resp.json()
        if len(data.get('results')) > 0:
            hostname = data['results'][0].get('custom_fields', {}).get('IPPlan_HostName', None)
            if not hostname:
                hostname = data['results'][0].get('description', None)

        return hostname
