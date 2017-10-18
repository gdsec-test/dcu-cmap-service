import requests
import logging


class MwpOneApi(object):

    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    def __init__(self, settings):
        self.url = settings.MWPONE_URL
        self.auth = (settings.MWPONEUSER, settings.MWPONEPASS)

    def mwpone_locate(self, domain):

        try:
            r = requests.get(self.url + domain, auth=self.auth, headers=self.headers, verify=False)
            text = r.json()

            if len(text['data']) == 1:
                status = text['data'][0]['status']['id']
                if status == 1:
                    guid = text['data'][0]['accountUid']
                    shopper = text['data'][0]['shopperId']
                    os = 'Linux'
                    dc = text['data'][0]['dataCenter']['description']
                    if dc == 'Buckeye':
                        dc = 'P3'
                    elif dc == 'Ashburn':
                        dc = 'A2'
                    elif dc == 'Amsterdam':
                        dc = 'N1'
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
                        if dc == 'Buckeye':
                            dc = 'P3'
                        elif dc == 'Ashburn':
                            dc = 'A2'
                        elif dc == 'Amsterdam':
                            dc = 'N1'
                        accountid = text['data'][i]['id']
                        ip = text['data'][0]['ipAddress']
                        return {'guid': guid, 'shopper': shopper, 'os': os, 'dc': dc, 'product': 'MWP 1.0',
                                'ip': ip, 'hostname': 'MWP 1.0 does not return hostname', 'accountid': accountid}
                    else:
                        pass

        except Exception as e:
            logging.error(e.message)