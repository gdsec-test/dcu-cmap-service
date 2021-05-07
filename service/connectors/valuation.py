import json
import logging

import requests


class ValuationAPI(object):
    _url = 'https://valuation.int.prod.godaddy.com/v6/domains/{}/highValueFeatures'
    _headers = {'Accept': 'application/json', 'Authorization': ''}
    DEFAULT_VALUATION = 'Unsupported'

    def __init__(self, settings):
        self._logger = logging.getLogger(__name__)
        self._headers['Authorization'] = settings.VALUATION_KEY

    def get_valuation_by_domain(self, domain_name):
        """
        Given a domain name, retrieve boolean value for "isHighValue" response key
        :param domain_name:
        :return:
        """
        try:
            if not domain_name:
                raise ValueError('Domain name was not provided')

            self._logger.info('Retrieving valuation for domain name {} from Valuation API'.format(domain_name))
            req_val = requests.get(self._url.format(domain_name), headers=self._headers)

            if req_val.status_code != 200:
                raise ValueError('Response from Valuation API: {}'.format(req_val.status_code))

            valuation = json.loads(req_val.text).get('isHighValue', self.DEFAULT_VALUATION)

        except Exception as e:
            self._logger.error('Error in getting the domain valuation info for {} : {}'.format(domain_name, e))
            valuation = self.DEFAULT_VALUATION

        return valuation
