import os
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

    TZ_URL = 'https://toolzilla.cmap.proxy.int.godaddy.com/webservice.php/AccountSearchService/WSDL'
    VERT_URL = 'https://vertigo.cmap.proxy.int.godaddy.com/vertigo/v1/container/?ips__ipv4='
    ANGELO_URL = 'https://p3nwplskapp-v01.shr.prod.phx3.secureserver.net:8084/v1/accounts?SearchAddonDomain&'
    DIABLO_URL = 'https://cpanelprovapi.prod.phx3.secureserver.net/v1/accounts?addon_domain_eq='
    SMDB_URL = 'https://smdb.int.godaddy.com/IPService/ipam.asmx?WSDL'
    MWPONE_URL = 'https://api.servicemanager.godaddy.com/v1/accounts/?domain='

    CMAPSERVICE_APP = 'cmapservice.int'
    WITHOUT_SSO = False
    AD_GROUP = {'DCU-Phishstory'}

    VPS4_URLS = OrderedDict([('IAD2', 'https://vps4.api.iad2.godaddy.com/api/'),
                             ('SIN2', 'https://vps4.api.sin2.godaddy.com/api/'),
                             ('AMS3', 'https://vps4.api.ams3.godaddy.com/api/')])

    SUBSCRIPTIONS_BLACKLIST = {'102704532'}

    def __init__(self):
        self.DB_PASS = quote(os.getenv('DB_PASS', 'password'))
        self.DBURL = 'mongodb://{}:{}@{}/{}'.format(self.DB_USER, self.DB_PASS, self.DB_HOST, self.DB)

        self.CMAP_PROXY_USER = os.getenv('CMAP_PROXY_USER', 'cmap_proxy_user')
        self.CMAP_PROXY_PASS = os.getenv('CMAP_PROXY_PASS', 'cmap_prox_password')
        self.CMAP_PROXY_CERT = os.getenv('CMAP_PROXY_CERT', 'proxy.crt')
        self.CMAP_PROXY_KEY = os.getenv('CMAP_PROXY_KEY', 'proxy.key')
        self.CMAP_SERVICE_CERT = os.getenv('CMAP_SERVICE_CERT', 'service.crt')
        self.CMAP_SERVICE_KEY = os.getenv('CMAP_SERVICE_KEY', 'service.key')

        self.CMAP_API_CERT = os.getenv('CMAP_API_CERT', 'api.crt')
        self.CMAP_API_KEY = os.getenv('CMAP_API_KEY', 'api.key')

        self.VERTIGO_USER = os.getenv('VERTIGO_USER', 'vertigo_user')
        self.VERTIGO_PASS = os.getenv('VERTIGO_PASS', 'vertiog_pass')
        self.DIABLO_USER = os.getenv('DIABLO_USER', 'diablo_user')
        self.DIABLO_PASS = os.getenv('DIABLO_PASS', 'diablo_pass')
        self.ANGELO_USER = os.getenv('ANGELO_USER', 'angelo_user')
        self.ANGELO_PASS = os.getenv('ANGELO_PASS', 'angelo_pass')
        self.MWP_ONE_USER = os.getenv('MWP_ONE_USER', 'mwp_one_user')
        self.MWP_ONE_PASS = os.getenv('MWP_ONE_PASS', 'mwp_one_pass')

        # VPS4 User/Pass are creds for a DCU Service account in the DCU-PHISHSTORY AD Group
        self.VPS4_USER = os.getenv('VPS4_USER', 'vps4user')
        self.VPS4_PASS = os.getenv('VPS4_PASS', 'vps4pass')

        self.SMDB_USER = os.getenv('SMDB_USER', 'smdb_user')
        self.SMDB_PASS = os.getenv('SMDB_PASS', 'smdb_pass')

        self.ALEXA_ACCESS_ID = os.getenv('ALEXA_ACCESS_ID', 'alexa_access_id')
        self.ALEXA_ACCESS_KEY = os.getenv('ALEXA_ACCESS_KEY', 'secret_access_key')


class ProductionAppConfig(AppConfig):
    DB = 'phishstory'
    DB_HOST = '10.22.9.209'
    DB_USER = 'sau_p_phish'

    SSO_URL = 'https://sso.godaddy.com'

    REDIS = 'cmap-service-redis.abuse-api-prod.svc.cluster.local'
    BRAND_DETECTION_URL = 'http://brand-detection.abuse-api-prod.svc.cluster.local:5000'
    GOCENTRAL_URL = 'https://websites.api.godaddy.com/v2/domains/{domain}/website'
    SUBSCRIPTIONS_URL = 'https://subscription.api.int.godaddy.com/v1/subscriptions'
    CNDNS_URL = 'https://abuse.partners.int.godaddy.com/v1/'
    CN_WHITELIST = ['cmapservice.int.godaddy.com',
                    'cmap.threatapi.godaddy.com',
                    'kelvinservice.int.godaddy.com']

    def __init__(self):
        super().__init__()


class OTEAppConfig(AppConfig):
    DB = 'otephishstory'
    DB_HOST = '10.22.9.209'
    DB_USER = 'sau_o_phish'

    SSO_URL = 'https://sso.ote-godaddy.com'

    REDIS = 'cmap-service-redis.abuse-api-ote.svc.cluster.local'
    BRAND_DETECTION_URL = 'http://brand-detection.abuse-api-ote.svc.cluster.local:5000'
    # Go Central OTE URL does not exist.  Using Test
    GOCENTRAL_URL = 'https://websites.api.test-godaddy.com/v2/domains/{domain}/website'
    SUBSCRIPTIONS_URL = 'https://subscription.api.int.ote-godaddy.com/v1/subscriptions'
    CNDNS_URL = 'http://abuse.partners.int.test-godaddy.com/v1/'
    CN_WHITELIST = ['cmapservice.int.ote-godaddy.com',
                    'kelvinservice.int.ote-godaddy.com']

    def __init__(self):
        super().__init__()


class DevelopmentAppConfig(AppConfig):
    DB = 'devphishstory'
    DB_HOST = '10.36.156.188'
    DB_USER = 'devuser'

    SSO_URL = 'https://sso.dev-godaddy.com'

    REDIS = 'cmap-service-redis.abuse-api-dev.svc.cluster.local'
    BRAND_DETECTION_URL = 'http://brand-detection.abuse-api-dev.svc.cluster.local:5000'
    GOCENTRAL_URL = 'https://websites.api.dev-godaddy.com/v2/domains/{domain}/website'
    SUBSCRIPTIONS_URL = 'https://subscription.api.int.dev-godaddy.com/v1/subscriptions'
    CNDNS_URL = 'http://abuse.partners.int.dev-godaddy.com/v1/'
    CN_WHITELIST = ['cmapservice.int.dev-godaddy.com',
                    'cmap.threatapi.dev-godaddy.com',
                    'kelvinservice.int.dev-godaddy.com']

    def __init__(self):
        super().__init__()


class LocalAppConfig(AppConfig):
    DB = 'local'
    DB_HOST = 'localhost'

    SSO_URL = 'https://sso.godaddy.com'

    REDIS = 'localhost'
    BRAND_DETECTION_URL = 'http://brand-detection.abuse-api-dev.svc.cluster.local:5000'
    GOCENTRAL_URL = 'https://websites.api.godaddy.com/v2/domains/{domain}/website'
    SUBSCRIPTIONS_URL = 'https://subscription.api.int.godaddy.com/v1/subscriptions'
    CN_WHITELIST = ['']
    WITHOUT_SSO = True

    def __init__(self):
        super().__init__()
        self.DBURL = 'mongodb://{}/{}'.format(self.DB_HOST, self.DB)


config_by_name = {'dev': DevelopmentAppConfig,
                  'ote': OTEAppConfig,
                  'prod': ProductionAppConfig,
                  'local': LocalAppConfig}
