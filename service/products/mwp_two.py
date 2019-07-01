import logging

import requests


class MWPTwoAPI(object):
    _url = 'http://{domain}/__mwp2_check__'

    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def locate(self, domain):
        """
        This functions sole purpose use the available URL query to determine if a domain name is hosted with a MWP 2.0
        hosting product.  query url is http://example.com/__mwp2_check__
        :param domain:
        :return: True if hosted mwp 2.0, False if not, or if error
        """

        try:
            r = requests.get(self._url.format(domain=domain), timeout=5)

            if r.status_code == 200 and r.text.strip().upper() == 'OK':
                return {'product': 'MWP 2.0'}
            else:
                self._logger.info('MWP 2.0 lookup failed for {}'.format(domain))
        except Exception as e:
            self._logger.error(e)
        return {}
