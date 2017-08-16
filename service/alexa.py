from datetime import datetime
from urllib import quote, urlencode
import base64
import hashlib
import hmac
import xml.etree.ElementTree as ET
import requests


class CallAwis(object):
    """Class for calling the Amazon Web Information Service API to get Alexa Rank for domain names"""

    def __init__(self, settings):
        self.secret_access_key = settings.SECRET_ACCESS_KEY
        signature_version = 2
        signature_method = "HmacSHA256"
        self.ServiceHost = "awis.amazonaws.com"
        self.PATH = "/"
        self.params = {
            'Action': "UrlInfo",
            'ResponseGroup': "Rank",
            'SignatureVersion': signature_version,
            'SignatureMethod': signature_method,
            'AWSAccessKeyId': settings.ACCESS_ID,
        }

    @staticmethod
    def _create_timestamp():
        now = datetime.utcnow()
        timestamp = now.isoformat()
        return timestamp

    @staticmethod
    def _create_uri(params):
        params = [(key, params[key]) for key in sorted(params.keys())]
        return urlencode(params)

    def _create_signature(self):
        uri = CallAwis._create_uri(self.params)
        msg = "\n".join(["GET", self.ServiceHost, self.PATH, uri])
        try:
            hmac_signature = hmac.new(self.secret_access_key, msg, hashlib.sha256)
        except TypeError:
            hmac_signature = hmac.new(self.secret_access_key.encode('utf-8'), msg.encode('utf-8'), hashlib.sha256)
        signature = base64.b64encode(hmac_signature.digest())
        return quote(signature)

    def urlinfo(self, domain):
        self.params['Timestamp'] = CallAwis._create_timestamp()
        self.params['Url'] = domain
        uri = CallAwis._create_uri(self.params)
        signature = self._create_signature()

        url = "https://%s/?%s&Signature=%s" % (self.ServiceHost, uri, signature)
        return CallAwis._return_output(url)

    @staticmethod
    def _return_output(url):
        r = requests.get(url)
        root = ET.fromstring(r.text)
        element = root.find('.//{http://awis.amazonaws.com/doc/2005-07-11}Rank')
        return element.text
