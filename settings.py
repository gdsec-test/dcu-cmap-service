import os
import socket
from collections import OrderedDict
from urllib.parse import quote


class AppConfig(object):
    REDIS_TTL = 24 * 60 * 60  # Seconds in a day
    DB = ''
    DB_USER = ''
    DB_HOST = ''
    DB_PORT = '27017'
    COLLECTION = 'blacklist'
    DATE_FORMAT = '%Y-%m-%d'

    VERT_URL = 'https://vertigo.cmap.proxy.int.godaddy.com/vertigo/v1/container/?ips__ipv4='
    ANGELO_URL = 'https://p3nwplskapp-v01.shr.prod.phx3.secureserver.net:8084/v1/accounts?SearchAddonDomain&'
    DIABLO_URL = 'http://localhost:8080/diablo/v1/accounts'
    DIABLO_WHMCS_URL = 'https://cpanelprovapi.prod.phx3.secureserver.net/v1/servers/'
    SMDB_URL = 'https://smdb.int.godaddy.com/IPService/ipam.asmx?WSDL'
    MWPONE_URL = 'http://localhost:8080/mwpone/v1/accounts'

    CMAPSERVICE_APP = 'cmapservice.cset.int'
    WITHOUT_SSO = False
    AD_GROUP = {'DCU-Phishstory'}

    VPS4_URLS = OrderedDict([('IAD2', 'https://vps4.api.iad2.godaddy.com/api/'),
                             ('SIN2', 'https://vps4.api.sin2.godaddy.com/api/'),
                             ('AMS3', 'https://vps4.api.ams3.godaddy.com/api/')])

    SUBSCRIPTIONS_BLACKLIST = {'102704532'}
    METRICS_PORT = int(os.getenv("METRICS_PORT", "9200"))

    PARKED_IPS = ['34.102.136.180', '34.98.99.30']
    CRM_CLIENT_API_URL = 'https://crmclient-api.dev.int.godaddy.com/Shopper.svc'
    SHOPPER_API_URL = 'http://localhost:8080/shopperapi/v1/shoppers/{}'

    CUSTOM_NS = None

    def __init__(self):
        self.DB_PASS = quote(os.getenv('DB_PASS', 'password'))
        self.DBURL = 'mongodb://{}:{}@{}/{}'.format(self.DB_USER, self.DB_PASS, self.DB_HOST, self.DB)

        self.CMAP_PROXY_USER = os.getenv('CMAP_PROXY_USER')
        self.CMAP_PROXY_PASS = os.getenv('CMAP_PROXY_PASS')
        self.CMAP_PROXY_CERT = os.getenv('CMAP_PROXY_CERT')
        self.CMAP_PROXY_KEY = os.getenv('CMAP_PROXY_KEY')
        self.CMAP_SERVICE_CERT = os.getenv('CMAP_SERVICE_CERT', 'service.crt')
        self.CMAP_SERVICE_KEY = os.getenv('CMAP_SERVICE_KEY', 'service.key')
        self.CMAP_SERVICE_CLIENT_CERT = os.getenv('CMAP_SERVICE_CLIENT_CERT', 'service.crt')
        self.CMAP_SERVICE_CLIENT_KEY = os.getenv('CMAP_SERVICE_CLIENT_KEY', 'service.key')

        self.CMAP_API_CERT = os.getenv('CMAP_API_CERT', 'api.crt')
        self.CMAP_API_KEY = os.getenv('CMAP_API_KEY', 'api.key')

        self.VERTIGO_USER = os.getenv('VERTIGO_USER', 'vertigo_user')
        self.VERTIGO_PASS = os.getenv('VERTIGO_PASS', 'vertigo_pass')
        self.DIABLO_USER = os.getenv('DIABLO_USER', 'diablo_user')
        self.DIABLO_PASS = os.getenv('DIABLO_PASS', 'diablo_pass')
        self.ANGELO_USER = os.getenv('ANGELO_USER', 'angelo_user')
        self.ANGELO_PASS = os.getenv('ANGELO_PASS', 'angelo_pass')

        # VPS4 User/Pass are creds for a DCU Service account in the DCU-PHISHSTORY AD Group
        self.VPS4_USER = os.getenv('VPS4_USER', 'vps4user')
        self.VPS4_PASS = os.getenv('VPS4_PASS', 'vps4pass')

        self.SMDB_USER = os.getenv('SMDB_USER', 'smdb_user')
        self.SMDB_PASS = os.getenv('SMDB_PASS', 'smdb_pass')

        self.ALEXA_ACCESS_ID = os.getenv('ALEXA_ACCESS_ID', 'alexa_access_id')
        self.ALEXA_ACCESS_KEY = os.getenv('ALEXA_ACCESS_KEY', 'secret_access_key')

        self.VALUATION_KEY = os.getenv('VALUATION_KEY', 'valuation_key')


class ProductionAppConfig(AppConfig):
    DB = 'phishstory'
    DB_HOST = '10.22.9.209'
    DB_USER = 'sau_p_phishv2'

    SSO_URL = 'https://sso.gdcorp.tools'

    REDIS = 'cmap-service-redis.abuse-api-prod.svc.cluster.local'
    BRAND_DETECTION_URL = 'http://brand-detection.abuse-api-prod.svc.cluster.local:5000'
    GOCENTRAL_URL = 'https://websites.api.godaddy.com/v2/domains/{domain}/website'
    SUBSCRIPTIONS_URL = 'https://subscription.api.int.godaddy.com/v1/subscriptions'
    CNDNS_URL = 'https://abuse.partners.int.godaddy.com/v1/'
    CN_WHITELIST = ['cmap.threatapi.godaddy.com',
                    'cmapservice.client.cset.int.gdcorp.tools',
                    'kelvinservice.client.cset.int.gdcorp.tools']
    DB_WEB_SVC_URL = 'https://dsweb.phx3.int.godaddy.com/RegDBWebSvc/RegDBWebSvc.dll'
    CRM_CLIENT_API_URL = 'https://crmclient-api.prod.phx3.int.godaddy.com/Shopper.svc'
    SHOPPER_API_URL = 'https://shopper.api.int.godaddy.com/v1/shoppers/{}'
    DIABLO_URL = 'https://cpanelprovapi.prod.phx3.secureserver.net/v1/accounts'
    MWPONE_URL = 'https://api.servicemanager.godaddy.com/v1/accounts'

    def __init__(self):
        super().__init__()


class OTEAppConfig(AppConfig):
    DB = 'otephishstory'
    DB_HOST = '10.22.9.209'
    DB_USER = 'sau_o_phish'

    SSO_URL = 'https://sso.ote-gdcorp.tools'

    REDIS = 'cmap-service-redis.abuse-api-ote.svc.cluster.local'
    BRAND_DETECTION_URL = 'http://brand-detection.abuse-api-ote.svc.cluster.local:5000'
    # Go Central OTE URL does not exist.  Using Test
    GOCENTRAL_URL = 'https://websites.api.test-godaddy.com/v2/domains/{domain}/website'
    SUBSCRIPTIONS_URL = 'https://subscription.api.int.ote-godaddy.com/v1/subscriptions'
    CNDNS_URL = 'http://abuse.partners.int.test-godaddy.com/v1/'
    CN_WHITELIST = ['cmapservice.client.cset.int.ote-gdcorp.tools',
                    'kelvinservice.client.cset.int.ote-gdcorp.tools']
    DB_WEB_SVC_URL = 'https://dsweb.ote.phx3.gdg/RegDBWebSvc/RegDBWebSvc.dll'
    CRM_CLIENT_API_URL = 'https://crmclient-api.prod.phx3.int.godaddy.com/Shopper.svc'
    SHOPPER_API_URL = 'https://shopper.api.int.ote-godaddy.com/v1/shoppers/{}'

    def __init__(self):
        super().__init__()


class TestAppConfig(AppConfig):
    DB = 'testphishstory'
    DB_HOST = 'mongodb.cset.int.dev-gdcorp.tools'
    DB_USER = 'testuser'

    SSO_URL = 'https://sso.test-gdcorp.tools'

    REDIS = 'cmap-service-redis.abuse-api-test.svc.cluster.local'
    BRAND_DETECTION_URL = 'http://brand-detection.abuse-api-test.svc.cluster.local:5000'
    CN_WHITELIST = ['cmap.threatapi.test-godaddy.com',
                    'cmapservice.client.cset.int.test-gdcorp.tools',
                    'kelvinservice.client.cset.int.test-gdcorp.tools']
    VPS4_URLS = OrderedDict([('IAD2', 'https://vps4.api.test-godaddy.com'),
                             ('SIN2', 'https://vps4.api.test-godaddy.com'),
                             ('AMS3', 'https://vps4.api.test-godaddy.com')])
    DIABLO_URL = 'https://diablo.api.test-godaddy.com/v1/accounts'
    DIABLO_WHMCS_URL = 'https://diablo.api.test-godaddy.com/v1/servers/'
    VERT_URL = ''
    ANGELO_URL = 'https://p3nwplskapp.test-godaddy.com:8084/v1/accounts?SearchAddonDomain&'
    MWPONE_URL = 'https://api.servicemanager.test-godaddy.com/v1/accounts'
    DB_WEB_SVC_URL = 'https://dsweb.int.test-godaddy.com/RegDBWebSvc/RegDBWebSvc.dll'
    SHOPPER_API_URL = 'https://shopper.api.int.test-godaddy.com/v1/shoppers/{}'
    TZ_URL = 'https://toolzilla.int.test-godaddy.com/webservice.php/AccountSearchService'
    GOCENTRAL_URL = 'https://websites.api.test-godaddy.com/v2/domains/{domain}/website'
    SMDB_URL = 'https://smdb.int.godaddy.com/IPService/ipam.asmx?WSDL'
    CNDNS_URL = ''
    CRM_CLIENT_API_URL = 'https://crmclient-api.test.int.godaddy.com/Shopper.svc'
    SUBSCRIPTIONS_URL = 'https://subscription.api.int.test-godaddy.com/v1/subscriptions'

    def __init__(self):
        super().__init__()
        self.CUSTOM_NS = socket.gethostbyname('ns05.test-dc.gdns.godaddy.com')


class DevelopmentAppConfig(AppConfig):
    DB = 'devphishstory'
    DB_HOST = 'mongodb.cset.int.dev-gdcorp.tools'
    DB_USER = 'devuser'

    SSO_URL = 'https://sso.dev-gdcorp.tools'

    REDIS = 'cmap-service-redis.abuse-api-dev.svc.cluster.local'
    BRAND_DETECTION_URL = 'http://localhost:8080/branddetection'
    GOCENTRAL_URL = 'http://localhost:8080/gocentral/v2/domains/{domain}/website'
    SUBSCRIPTIONS_URL = 'https://subscription.api.int.dev-godaddy.com/v1/subscriptions'
    CNDNS_URL = 'http://abuse.partners.int.dev-godaddy.com/v1/'
    CN_WHITELIST = ['cmap.threatapi.dev-godaddy.com',
                    'cmapservice.client.cset.int.dev-gdcorp.tools',
                    'kelvinservice.client.cset.int.dev-gdcorp.tools']
    DB_WEB_SVC_URL = 'http://localhost:8080/regdb/RegDbWebSvc/RegDVWebSvc.dll'
    SHOPPER_API_URL = 'http://localhost:8080/shopperapi/v1/shoppers/{}'

    def __init__(self):
        super().__init__()


class LocalAppConfig(AppConfig):
    DB = 'local'
    DB_HOST = 'localhost'

    SSO_URL = 'https://sso.gdcorp.tools'

    REDIS = 'localhost'
    BRAND_DETECTION_URL = 'http://brand-detection.abuse-api-dev.svc.cluster.local:5000'
    GOCENTRAL_URL = 'https://websites.api.godaddy.com/v2/domains/{domain}/website'
    SUBSCRIPTIONS_URL = 'https://subscription.api.int.godaddy.com/v1/subscriptions'
    CNDNS_URL = 'https://abuse.partners.int.godaddy.com/v1/'
    CN_WHITELIST = ['']
    WITHOUT_SSO = True
    DB_WEB_SVC_URL = 'http://localhost:8080/regdb/RegDbWebSvc/RegDVWebSvc.dll'

    def __init__(self):
        super().__init__()
        self.DBURL = 'mongodb://{}/{}'.format(self.DB_HOST, self.DB)


config_by_name = {'dev': DevelopmentAppConfig,
                  'ote': OTEAppConfig,
                  'prod': ProductionAppConfig,
                  'test': TestAppConfig,
                  'local': LocalAppConfig}
