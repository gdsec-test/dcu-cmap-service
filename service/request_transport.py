import requests
import io
from suds.transport import Reply, TransportError
from suds.transport.https import HttpAuthenticated

class RequestsTransport(HttpAuthenticated):
    def __init__(self, **kwargs):
        self.cert = (kwargs.pop('cert', None), kwargs.pop('key', None))
        self.auth = (kwargs.pop('username', None), kwargs.pop('password', None))
        # super won't work because not using new style class
        HttpAuthenticated.__init__(self, **kwargs)

    def open(self, request):

        resp = requests.get(request.url, data=request.message,
                            headers=request.headers, cert=self.cert, auth=self.auth)
        result = io.StringIO(resp.content.decode('utf-8'))
        return result

    def send(self, request):

        resp = requests.post(request.url, data=request.message,
                             headers=request.headers, cert=self.cert, auth=self.auth)
        result = Reply(resp.status_code, resp.headers, resp.content)
        return result

    @staticmethod
    def get_soap_headers():
        return {"Content-Type": "text/xml;charset=UTF-8", "SOAPAction": ""}
