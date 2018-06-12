import logging
import requests


class MwpTwo:

    def __init__(self, settings):
        self.url = 'http://{domain}/__mwp2_check__'

    def is_mwp2(self, domain):
        """
        This functions sole purpose use the available URL query to determine if a domain name is hosted with a MWP 2.0
        hosting product.  query url is http://example.com/__mwp2_check__
        :param domain:
        :return: True if hosted mwp 2.0, False if not, or if error
        """

        try:
            r = requests.get(self.url.format(domain=domain))

            if r.status_code == 200 and r.text.strip().upper() == 'OK':
                return True

            else:
                logging.info('MWP 2.0 lookup failed for {}: Status Code {}: Text {}: Reason {}'.format(domain,
                                                                                                       r.status_code,
                                                                                                       r.text,
                                                                                                       r.reason))

        except Exception as e:
            logging.error(e.message)
        return False
