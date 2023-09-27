import os
import socket
from collections import OrderedDict
from urllib.parse import quote


class AppConfig(object):
    REDIS_TTL = 24 * 60 * 60  # Seconds in a day
    REDIS = os.getenv('REDIS')
    PERSISTENT_REDIS = os.getenv('PERSISTENT_REDIS')
    DB = ''
    DB_USER = ''
    DB_HOST = ''
    DB_PORT = '27017'
    COLLECTION = 'blacklist'
    DATE_FORMAT = '%Y-%m-%d'

    ANGELO_URL = 'https://gdapi.plesk-shared-app.int.gdcorp.tools/v1/accounts?SearchAddonDomain&'
    DIABLO_URL = 'http://localhost:8080/diablo/v1/accounts'
    DIABLO_WHMCS_URL = 'https://cpanelprovapi.prod.phx3.secureserver.net/v1/servers/'
    NETBOX_URL = 'https://netbox.int.gdcorp.tools'
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
    SIMILAR_WEB_URL = 'https://api.similarweb.com'
    CUSTOM_NS = None
    SUBDOMAIN_ENRICHMENT_LIST = ['godaddysites.com', 'go.studio', 'secureserversites.net']

    def __init__(self):
        self.CLIENT_CERT = os.getenv("MONGO_CLIENT_CERT", '')
        self.DB_PASS = quote(os.getenv('DB_PASS', 'password'))
        self.DBURL = f'mongodb://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}/?authSource={self.DB}&readPreference=primary&directConnection=true&tls=true&tlsCertificateKeyFile={self.CLIENT_CERT}'

        self.CMAP_SERVICE_CLIENT_CERT = os.getenv('CMAP_SERVICE_CLIENT_CERT', 'service.crt')
        self.CMAP_SERVICE_CLIENT_KEY = os.getenv('CMAP_SERVICE_CLIENT_KEY', 'service.key')

        self.DIABLO_USER = os.getenv('DIABLO_USER', 'diablo_user')
        self.DIABLO_PASS = os.getenv('DIABLO_PASS', 'diablo_pass')
        self.ANGELO_USER = os.getenv('ANGELO_USER', 'angelo_user')
        self.ANGELO_PASS = os.getenv('ANGELO_PASS', 'angelo_pass')

        # VPS4 User/Pass are creds for a DCU Service account in the DCU-PHISHSTORY AD Group
        self.VPS4_USER = os.getenv('VPS4_USER', 'vps4user')
        self.VPS4_PASS = os.getenv('VPS4_PASS', 'vps4pass')

        self.NETBOX_TOKEN = os.getenv('NETBOX_TOKEN', None)

        self.VALUATION_KEY = os.getenv('VALUATION_KEY', 'valuation_key')
        self.SIMILAR_WEB_API_KEY = os.getenv('SIMILAR_WEB_API_KEY')


class ProductionAppConfig(AppConfig):
    DB = 'phishstory'
    DB_HOST = 'p3plsocritmdb00-00-f0.prod.phx3.gdg'
    DB_USER = 'sau_p_phishv2'
    SSO_URL = 'https://sso.gdcorp.tools'
    BRAND_DETECTION_URL = 'http://brand-detection.abuse-api-prod.svc.cluster.local:5000'
    GOCENTRAL_URL = 'https://websites.api.godaddy.com'
    SUBSCRIPTIONS_URL = 'https://subscription.api.int.godaddy.com/v1/subscriptions'
    CN_WHITELIST = ['cmap.threatapi.godaddy.com',
                    'cmapservice.client.cset.int.gdcorp.tools',
                    'kelvinservice.client.cset.int.gdcorp.tools',
                    'middleware.client.cset.int.gdcorp.tools',
                    'mwnotifications.client.cset.int.gdcorp.tools']
    DB_WEB_SVC_URL = 'https://dsweb.phx3.int.godaddy.com/RegDBWebSvc/RegDBWebSvc.dll'
    CRM_CLIENT_API_URL = 'https://crmclient-api.prod.phx3.int.godaddy.com/Shopper.svc'
    SHOPPER_API_URL = 'https://shopper.api.int.godaddy.com/v1/shoppers/{}'
    DIABLO_URL = 'https://cpanelprovapi.prod.phx3.secureserver.net/v1/accounts'
    MWPONE_URL = 'https://mwp.api.phx3.godaddy.com/api/v1/mwp/sites/search'
    SUBSCRIPTIONS_SHIM_URL = 'https://subscriptions-shim-ext-ro.cp.api.prod.godaddy.com'
    ENTITLEMENTS_URL = 'https://entitlements-ext.cp.api.prod.godaddy.com'

    def __init__(self):
        super().__init__()


class StagingAppConfig(ProductionAppConfig):
    CN_WHITELIST = []
    AD_GROUP = {'org-infosec-software-engineering'}

    CMAPSERVICE_APP = 'cmapservice-stg.cset.int'

    def __init__(self):
        super().__init__()


class OTEAppConfig(AppConfig):
    DB = 'otephishstory'
    DB_HOST = 'p3plsocritmdb00-00-f0.prod.phx3.gdg'
    DB_USER = 'sau_o_phish'

    SSO_URL = 'https://sso.ote-gdcorp.tools'

    BRAND_DETECTION_URL = 'http://brand-detection.abuse-api-ote.svc.cluster.local:5000'
    # Go Central OTE URL does not exist.  Using Test
    GOCENTRAL_URL = 'https://websites.api.test-godaddy.com'
    SUBSCRIPTIONS_URL = 'https://subscription.api.int.ote-godaddy.com/v1/subscriptions'
    SUBSCRIPTIONS_SHIM_URL = 'https://subscriptions-shim-ext-ro.cp.api.ote.godaddy.com'
    ENTITLEMENTS_URL = 'https://entitlements-ext.cp.api.ote.godaddy.com'
    CN_WHITELIST = ['cmapservice.client.cset.int.ote-gdcorp.tools',
                    'kelvinservice.client.cset.int.ote-gdcorp.tools',
                    'middleware.client.cset.int.ote-gdcorp.tools']
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

    BRAND_DETECTION_URL = 'http://brand-detection.abuse-api-test.svc.cluster.local:5000'
    CN_WHITELIST = ['cmap.threatapi.test-godaddy.com',
                    'cmapservice.client.cset.int.test-gdcorp.tools',
                    'kelvinservice.client.cset.int.test-gdcorp.tools',
                    'middleware.client.cset.int.test-gdcorp.tools',
                    'mwnotifications.client.cset.int.test-gdcorp.tools']
    VPS4_URLS = OrderedDict([('IAD2', 'https://vps4.api.test-godaddy.com'),
                             ('SIN2', 'https://vps4.api.test-godaddy.com'),
                             ('AMS3', 'https://vps4.api.test-godaddy.com')])
    DIABLO_URL = 'https://diablo.api.test-godaddy.com/v1/accounts'
    DIABLO_WHMCS_URL = 'https://diablo.api.test-godaddy.com/v1/servers/'
    MWPONE_URL = 'https://mwp.api.phx3.test-godaddy.com/api/v1/mwp/sites/search'
    ANGELO_URL = 'https://gdapi.plesk-shared-app.int.test-gdcorp.tools/v1/accounts?SearchAddonDomain&'
    DB_WEB_SVC_URL = 'https://dsweb.int.test-godaddy.com/RegDBWebSvc/RegDBWebSvc.dll'
    SHOPPER_API_URL = 'https://shopper.api.int.test-godaddy.com/v1/shoppers/{}'
    TZ_URL = 'https://toolzilla.int.test-godaddy.com/webservice.php/AccountSearchService'
    GOCENTRAL_URL = 'https://websites.api.test-godaddy.com'
    CRM_CLIENT_API_URL = 'https://crmclient-api.test.int.godaddy.com/Shopper.svc'
    SUBSCRIPTIONS_URL = 'https://subscription.api.int.test-godaddy.com/v1/subscriptions'
    SUBSCRIPTIONS_SHIM_URL = 'https://subscriptions-shim-ext-ro.cp.api.test.godaddy.com'
    ENTITLEMENTS_URL = 'https://entitlements-ext.cp.api.test.godaddy.com'

    def __init__(self):
        super().__init__()
        self.CUSTOM_NS = socket.gethostbyname('ns05.test-dc.gdns.godaddy.com')


class DevelopmentAppConfig(AppConfig):
    DB = 'devphishstory'
    DB_HOST = 'mongodb.cset.int.dev-gdcorp.tools'
    DB_USER = 'devuser'
    SSO_URL = 'https://sso.dev-gdcorp.tools'
    BRAND_DETECTION_URL = 'http://localhost:8080/branddetection'
    GOCENTRAL_URL = 'http://localhost:8080/gocentral'
    SUBSCRIPTIONS_URL = 'https://subscription.api.int.dev-godaddy.com/v1/subscriptions'
    CN_WHITELIST = ['cmap.threatapi.dev-godaddy.com',
                    'cmapservice.client.cset.int.dev-gdcorp.tools',
                    'kelvinservice.client.cset.int.dev-gdcorp.tools',
                    'middleware.client.cset.int.dev-gdcorp.tools',
                    'mwnotifications.client.cset.int.dev-gdcorp.tools']
    DB_WEB_SVC_URL = 'http://localhost:8080/regdb/RegDbWebSvc/RegDVWebSvc.dll'
    SHOPPER_API_URL = 'https://shopper.api.int.dev-godaddy.com/v1/shoppers/{}'
    SUBSCRIPTIONS_SHIM_URL = 'https://subscriptions-shim-ext-ro.cp.api.dp.godaddy.com'
    ENTITLEMENTS_URL = 'https://entitlements-ext.cp.api.dp.godaddy.com'

    def __init__(self):
        super().__init__()


class LocalAppConfig(AppConfig):
    DB = 'local'
    DB_HOST = 'localhost'
    MWPONE_URL = 'https://mwp.api.phx3.test-godaddy.com/api/v1/mwp/sites/search'
    SSO_URL = 'https://sso.test-gdcorp.tools'

    REDIS = 'localhost'
    BRAND_DETECTION_URL = 'http://brand-detection.abuse-api-dev.svc.cluster.local:5000'
    GOCENTRAL_URL = 'https://websites.api.godaddy.com'
    SUBSCRIPTIONS_URL = 'https://subscription.api.int.godaddy.com/v1/subscriptions'
    CN_WHITELIST = ['']
    WITHOUT_SSO = True
    DB_WEB_SVC_URL = 'http://localhost:8080/regdb/RegDbWebSvc/RegDVWebSvc.dll'

    def __init__(self):
        super().__init__()
        self.DBURL = 'mongodb://{}/{}'.format(self.DB_HOST, self.DB)


config_by_name = {'dev': DevelopmentAppConfig,
                  'ote': OTEAppConfig,
                  'staging': StagingAppConfig,
                  'prod': ProductionAppConfig,
                  'test': TestAppConfig,
                  'local': LocalAppConfig}
