# AWS Version 4 signing example

# AWIS API (Alexa Web Information Services)

# See: http://docs.aws.amazon.com/general/latest/gr/sigv4_signing.html
# This version makes a GET request and passes the signature
# in the Authorization header.

import sys, os, base64, datetime, hashlib, hmac 
import requests  # pip install requests

import xml.etree.ElementTree as ET


class CallAwis(object):

    # ************* REQUEST VALUES *************
    METHOD = 'GET'
    SERVICE = 'awis'
    HOST = 'awis.us-west-1.amazonaws.com'
    REGION = 'us-west-1'
    ENDPOINT = 'https://awis.amazonaws.com/api'
    REQUEST_PARAMETERS = 'Action=UrlInfo&ResponseGroup=Rank&Url='

    def __init__(self, settings):

        # Needed settings
        self.access_key = os.environ.get('ACCESS_ID')
        self.secret_key = os.environ.get('SECRET_ACCESS_KEY')

    def sign(self, key, msg):
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

    def get_signature_key(self, key, date_stamp, region_name, service_name):
        key_date = self.sign(('AWS4' + key).encode('utf-8'), date_stamp)
        key_region = self.sign(key_date, region_name)
        key_service = self.sign(key_region, service_name)
        key_signing = self.sign(key_service, 'aws4_request')
        return key_signing

    def urlinfo(self, domain):
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
        canonical_request = self.METHOD + '\n' \
                            + canonical_uri + '\n' \
                            + canonical_querystring + '\n' \
                            + canonical_headers + '\n' \
                            + signed_headers + '\n' \
                            + payload_hash

        # ************* CREATE THE STRING TO SIGN *************
        algorithm = 'AWS4-HMAC-SHA256'
        credential_scope = datestamp + '/' \
                           + self.REGION \
                           + '/' \
                           + self.SERVICE \
                           + '/' \
                           + 'aws4_request'

        string_to_sign = algorithm + '\n' \
                         + amzdate + '\n' \
                         + credential_scope \
                         + '\n' \
                         + hashlib.sha256(canonical_request).hexdigest()

        # Create the signing key
        signing_key = self.get_signature_key(self.secret_key, datestamp, self.REGION, self.SERVICE)

        # Sign the string_to_sign using the signing_key
        signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

        # Create authorization header and add to request headers
        authorization_header = algorithm + ' ' \
                               + 'Credential=' \
                               + self.access_key \
                               + '/' + credential_scope \
                               + ', ' + 'SignedHeaders=' \
                               + signed_headers \
                               + ', ' \
                               + 'Signature=' \
                               + signature

        headers = {'x-amz-date': amzdate, 'Authorization': authorization_header}

        # ************* SEND THE REQUEST *************
        request_url = CallAwis.ENDPOINT + '?' + canonical_querystring

        r = requests.get(request_url, headers=headers)

        root = ET.fromstring(r.text)
        element = root.find('.//{http://awis.amazonaws.com/doc/2005-07-11}Rank')
        return element.text


if __name__ == '__main__':
    s = 'settings'
    a = CallAwis(s)
    # A domain name to request rank for
    d = 'godaddy.com'
    value = a.urlinfo(d)
    print value
