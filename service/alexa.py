import datetime
import hashlib
import hmac
import logging
import xml.etree.ElementTree as ET

from requests import sessions


class CallAwis(object):
    """
    Makes a GET request to the AWIS API (Alexa Web Information Service) to get Alexa Rank for a domain name
    AWIS API
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
    REQUEST_PARAMETERS = 'Action=UrlInfo&ResponseGroup=Rank&Url='

    def __init__(self, settings):
        self._access_key = settings.ALEXA_ACCESS_ID
        self._secret_key = settings.ALEXA_ACCESS_KEY
        self._logger = logging.getLogger(__name__)

    @staticmethod
    def _sign(key, msg):
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

    def _get_signature_key(self, key, date_stamp, region_name, service_name):
        key_date = self._sign(('AWS4' + key).encode('utf-8'), date_stamp)
        key_region = self._sign(key_date, region_name)
        key_service = self._sign(key_region, service_name)
        key_signing = self._sign(key_service, 'aws4_request')
        return key_signing

    def _build_request(self, domain):
        # Create a date for headers and the credential string
        t = datetime.datetime.utcnow()
        amzdate = t.strftime('%Y%m%dT%H%M%SZ')
        datestamp = t.strftime('%Y%m%d')  # Date w/o time, used in credential scope
        # ************* CREATE A CANONICAL REQUEST *************
        # Create canonical URI
        canonical_uri = '/api'
        # Create the canonical query string.
        canonical_querystring = self.REQUEST_PARAMETERS + domain
        # Create the canonical headers and signed headers.
        canonical_headers = 'host:' + self.HOST + '\n' + 'x-amz-date:' + amzdate + '\n'
        # Create the list of signed headers.
        signed_headers = 'host;x-amz-date'
        # Create payload hash (hash of the request body content). For GET
        # requests, the payload is an empty string ("").
        payload_hash = hashlib.sha256('').hexdigest()
        # Combine elements to create canonical request
        canonical_request = self.METHOD + '\n' + canonical_uri + '\n' + canonical_querystring + '\n' \
            + canonical_headers + '\n' + signed_headers + '\n' + payload_hash

        # ************* CREATE THE STRING TO SIGN *************
        algorithm = 'AWS4-HMAC-SHA256'
        credential_scope = datestamp + '/' + self.REGION + '/' + self.SERVICE + '/' + 'aws4_request'
        string_to_sign = algorithm + '\n' + amzdate + '\n' + credential_scope + '\n' \
            + hashlib.sha256(canonical_request).hexdigest()

        # Create the signing key
        signing_key = self._get_signature_key(self._secret_key, datestamp, self.REGION, self.SERVICE)
        # Sign the _string_to_sign using the signing_key
        signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
        # Create authorization header and add to request headers
        authorization_header = algorithm + ' ' + 'Credential=' + self._access_key + '/' + credential_scope + ', ' \
            + 'SignedHeaders=' + signed_headers + ', ' + 'Signature=' + signature

        headers = {'x-amz-date': amzdate, 'Authorization': authorization_header}
        request_url = self.ENDPOINT + '?' + canonical_querystring

        try:
            with sessions.Session() as session:
                r = session.get(request_url, headers=headers)

            if r.status_code == 200:
                root = ET.fromstring(r.text)
                element = root.find('.//{http://awis.amazonaws.com/doc/2005-07-11}Rank')
                return element.text

            else:
                self._logger.error("Failed call to AWIS AlexaRank for domain: %s - request status code: %s",
                                   domain, r.status_code)

        except Exception as e:
            self._logger.error("Failed call to AWIS AlexaRank for %s - Error: %s", domain, e.message)

        return None

    def urlinfo(self, domain):
        """
        This method will return an Alexa Rank when given a domain name ex. godaddy.com
        :param domain: string
        :return: a string representing an Alexa Rank or None if lookup fails
        """
        return self._build_request(domain)
