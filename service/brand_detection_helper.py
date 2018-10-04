import logging

from requests import sessions


class BrandDetectionHelper(object):
    _HOSTING_ENDPOINT = '/hosting'
    _REGISTRAR_ENDPOINT = '/registrar'

    def __init__(self, settings):
        self._logger = logging.getLogger(__name__)
        self._brand_detection_url = settings.BRAND_DETECTION_URL

    def get_hosting_info(self, domain):
        """
        Attempt to retrieve the hosting information from the Brand Detection service
        :param domain:
        :return:
        """
        try:
            with sessions.Session() as session:
                self._logger.info("Fetching hosting information for {}".format(domain))
                url = self._brand_detection_url + self._HOSTING_ENDPOINT + "?domain={}".format(domain)
                return session.get(url=url).json()
        except Exception as e:
            self._logger.error("Unable to query Brand Detection service for {} : {}".format(domain, e.message))
            return {'brand': None, 'hosting_company_name': None, 'hosting_abuse_email': None, 'ip': None}

    def get_registrar_info(self, domain):
        """
        Attempt to retrieve the registrar information from the Brand Detection service
        :param domain:
        :return:
        """
        try:
            with sessions.Session() as session:
                self._logger.info("Fetching registrar information for {}".format(domain))
                url = self._brand_detection_url + self._REGISTRAR_ENDPOINT + "?domain={}".format(domain)
                return session.get(url=url).json()
        except Exception as e:
            self._logger.error("Unable to query Brand Detection service for {} : {}".format(domain, e.message))
            return {'brand': None, 'registrar_name': None, 'registrar_abuse_email': None, 'domain_create_date': None,
                    'domain_id': None}
