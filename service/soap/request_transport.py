import io

import requests
from suds.transport import Reply
from suds.transport.https import HttpAuthenticated


class RequestsTransport(HttpAuthenticated):
    def __init__(self, **kwargs):
        self.cert = (kwargs.pop('cert', None), kwargs.pop('key', None))
        self.auth = (kwargs.pop('username', None), kwargs.pop('password', None))
        self.verify = kwargs.pop('verify', True)

        super().__init__(**kwargs)

    def open(self, request):
        resp = requests.get(request.url, data=request.message, headers=request.headers, cert=self.cert, auth=self.auth, verify=self.verify)
        return io.StringIO(resp.content.decode())

    def send(self, request):
        resp = requests.post(request.url, data=request.message, headers=request.headers, cert=self.cert, auth=self.auth, verify=self.verify)
        return Reply(resp.status_code, resp.headers, resp.content)

    @staticmethod
    def get_soap_headers():
        return {'Content-Type': 'text/xml;charset=UTF-8', 'SOAPAction': ''}
