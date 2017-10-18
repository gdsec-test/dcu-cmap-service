import requests
import logging


class MwpOneApi:

    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    def __init__(self, settings):
        self.url = settings.MWPONE_URL
        self.auth = (settings.MWPONEUSER, settings.MWPONEPASS)

    def mwpone_locate(self, domain):
        """
        This functions sole purpose is to locate all data for a MWP 1.0 account to be placed into the data
        sub document of the incident's mongo document
        :param domain:
        :return:
        """

        try:
            r = requests.get(self.url + domain, auth=self.auth, headers=self.headers, verify=False)
            text = r.json()

        except Exception as e:
            logging.error(e.message)

        if len(text['data']) == 1:
            status = text['data'][0]['status']['id']
            if status == 1:
                guid = text['data'][0]['accountUid']
                shopper = text['data'][0]['shopperId']
                os = 'Linux'
                dc = text['data'][0]['dataCenter']['description']
                dc = self._dc_helper(dc)
                accountid = text['data'][0]['id']
                ip = text['data'][0]['ipAddress']
                return {'guid': guid, 'shopper': shopper, 'os': os, 'dc': dc, 'product': 'MWP 1.0',
                        'ip': ip, 'hostname': 'MWP 1.0 does not return hostname', 'accountid': accountid}

            else:
                logging.error('no active MWP 1.0 account ID found')
                return None

        elif len(text['data']) > 1:
            for i in range(len(text['data'])):
                status = text['data'][i]['status']['id']
                if status == 1:
                    guid = text['data'][i]['accountUid']
                    shopper = text['data'][i]['shopperId']
                    os = 'Linux'
                    dc = text['data'][0]['dataCenter']['description']
                    dc = self._dc_helper(dc)
                    accountid = text['data'][i]['id']
                    ip = text['data'][0]['ipAddress']
                    return {'guid': guid, 'shopper': shopper, 'os': os, 'dc': dc, 'product': 'MWP 1.0',
                            'ip': ip, 'hostname': 'MWP 1.0 does not return hostname', 'accountid': accountid}



    def _dc_helper(self, dc):
        if dc == 'Buckeye':
            dc = 'P3'
            return dc
        elif dc == 'Ashburn':
            dc = 'A2'
            return dc
        elif dc == 'Amsterdam':
            dc = 'N1'
            return dc
