import datetime
import hashlib
import hmac
import logging
import xml.etree.ElementTree as ET

import requests


class AlexaWebInformationService(object):
    """
    Makes a GET request to the AWIS API (Alexa Web Information Service) to get Alexa Rank for a domain name
    See: https://aws.amazon.com/documentation/awis/
    Uses AWS Signing Version 4
    See: http://docs.aws.amazon.com/general/latest/gr/sigv4_signing.html
    """

    # ************* REQUEST VALUES *************
    METHOD = 'GET'
    SERVICE = 'awis'
    HOST = 'awis.us-west-1.amazonaws.com'
    REGION = 'us-west-1'
    ENDPOINT = 'https://awis.amazonaws.com/api'
    REQUEST_PARAMETERS = 'Action=UrlInfo&ResponseGroup=Rank&Url={}'
    CANONICAL_URI = '/api'
    SIGNED_HEADERS = 'host;x-amz-date'
    ALGORITHM = 'AWS4-HMAC-SHA256'

    def __init__(self, id, key):
        self._access_key = id
        self._secret_key = key
        self._logger = logging.getLogger(__name__)

    @staticmethod
    def _sign(key, msg):
        return hmac.new(key, msg.encode(), hashlib.sha256).digest()

    def get_url_information(self, domain):
        """
        This method will return an Alexa Rank when given a domain name ex. godaddy.com
        :param domain: string
        :return: a string representing an Alexa Rank or None if lookup fails
        """
        return self._build_request(domain)

    def _get_signature_key(self, key, date_stamp, region_name, service_name):
        key_date = self._sign(('AWS4' + key).encode(), date_stamp)
        key_region = self._sign(key_date, region_name)
        key_service = self._sign(key_region, service_name)
        key_signing = self._sign(key_service, 'aws4_request')
        return key_signing

    def _build_request(self, domain):
        # Create a date for headers and the credential string
        current_time = datetime.datetime.utcnow()
        amzdate = current_time.strftime('%Y%m%dT%H%M%SZ')
        datestamp = current_time.strftime('%Y%m%d')  # Date w/o time, used in credential scope

        # ************* CREATE A CANONICAL REQUEST *************

        # Create the canonical query string.
        canonical_querystring = self.REQUEST_PARAMETERS.format(domain)

        # Create the canonical headers and signed headers.
        canonical_headers = 'host:{}\nx-amz-date:{}\n'.format(self.HOST, amzdate)

        # Create payload hash (hash of the request body content). For GET
        # requests, the payload is an empty string ("").
        payload_hash = hashlib.sha256(b'').hexdigest()

        # Combine elements to create canonical request
        canonical_request = '{}\n{}\n{}\n{}\n{}\n{}'.format(self.METHOD, self.CANONICAL_URI, canonical_querystring, canonical_headers, self.SIGNED_HEADERS, payload_hash)

        # ************* CREATE THE STRING TO SIGN *************
        credential_scope = '{}/{}/{}/aws4_request'.format(datestamp, self.REGION, self.SERVICE)

        hex = hashlib.sha256(canonical_request.encode()).hexdigest()
        string_to_sign = '{}\n{}\n{}\n{}'.format(self.ALGORITHM, amzdate, credential_scope, hex)

        # Create the signing key
        signing_key = self._get_signature_key(self._secret_key, datestamp, self.REGION, self.SERVICE)
        # Sign the _string_to_sign using the signing_key
        signature = hmac.new(signing_key, string_to_sign.encode(), hashlib.sha256).hexdigest()
        # Create authorization header and add to request headers

        authorization_header = '{} Credential={}/{}, SignedHeaders={}, Signature={}'.format(self.ALGORITHM, self._access_key, credential_scope, self.SIGNED_HEADERS, signature)

        headers = {'x-amz-date': amzdate, 'Authorization': authorization_header}

        try:
            r = requests.get(self.ENDPOINT + '?' + canonical_querystring, headers=headers)

            if r.status_code == 200:
                root = ET.fromstring(r.text)
                element = root.find('.//{http://awis.amazonaws.com/doc/2005-07-11}Rank')
                return element.text

            else:
                self._logger.error('Failed call to AWIS AlexaRank for domain: {} - request status code: {}'.format(domain, r.status_code))

        except Exception as e:
            self._logger.error('Failed call to AWIS AlexaRank for {} : {}'.format(domain, e))

        return None
