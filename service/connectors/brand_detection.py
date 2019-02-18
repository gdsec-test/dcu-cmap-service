import logging

import requests


class BrandDetectionHelper(object):
    '''
    Provides a simple interface for interacting with the Brand Detection Service which aids in determining
    the brand associated with a given domain. It also returns limited information such as abuse contact emails, etc.
    '''

    def __init__(self, url):
        self._logger = logging.getLogger(__name__)

        self._hosting_endpoint = '{}/hosting?domain={{}}'.format(url)
        self._registrar_endpoint = '{}/registrar?domain={{}}'.format(url)

    def get_hosting_info(self, domain):
        """
        Attempt to retrieve the hosting information from the Brand Detection service
        :param domain:
        :return:
        """
        self._logger.info('Fetching hosting information for {}'.format(domain))

        try:
            return requests.get(self._hosting_endpoint.format(domain)).json()
        except Exception as e:
            self._logger.error('Unable to query Brand Detection service for {} : {}'.format(domain, e))
            return {'brand': None, 'hosting_company_name': None, 'hosting_abuse_email': None, 'ip': None}

    def get_registrar_info(self, domain):
        """
        Attempt to retrieve the registrar information from the Brand Detection service
        :param domain:
        :return:
        """
        self._logger.info('Fetching registrar information for {}'.format(domain))

        try:
            return requests.get(self._registrar_endpoint.format(domain)).json()
        except Exception as e:
            self._logger.error('Unable to query Brand Detection service for {} : {}'.format(domain, e))
            return {'brand': None, 'registrar_name': None, 'registrar_abuse_email': None, 'domain_create_date': None,
                    'domain_id': None}
