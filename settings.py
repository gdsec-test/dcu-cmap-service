import os
import urllib
from blindal.crypter import Crypter


class PasswordDecrypter:

    @staticmethod
    def decrypt(password):
        keyfile = os.getenv('KEYFILE') or None
        if keyfile:
            f = open(keyfile, "r")
            try:
                key, iv = f.readline().split()
                return Crypter.decrypt(password, key, iv)
            finally:
                f.close()
        return password


class AppConfig(object):
    REDIS_TTL = 24 * 60 * 60  # Seconds in a day
    DB = ''
    DB_USER = ''
    DB_HOST = ''
    DB_PORT = '27017'
    COLLECTION = 'blacklist'
    DATE_FORMAT = '%Y-%m-%d'
    TZ_URL = 'https://toolzilla.int.godaddy.com/webservice.php/AccountSearchService/WSDL'
    VERT_URL = 'https://vertigo.godaddy.com/vertigo/v1/container/?ips__ipv4='
    ANGELO_URL = 'https://p3nwplskapp-v01.shr.prod.phx3.secureserver.net:8084/v1/accounts?SearchAddonDomain&'
    DIABLO_URL = 'https://cpanelprovapi.prod.phx3.secureserver.net/v1/accounts?addon_domain_eq='

    def __init__(self):
        self.REDIS = os.getenv('REDIS') or 'redis'
        self.DB_PASS = os.getenv('DB_PASS') or 'password'
        self.DB_PASS = urllib.quote(PasswordDecrypter.decrypt(self.DB_PASS))
        self.DBURL = 'mongodb://{}:{}@{}/{}'.format(self.DB_USER, self.DB_PASS, self.DB_HOST, self.DB)
        self.CMAP_PROXY_USER = os.getenv('CMAP_PROXY_USER') or 'user'
        self.CMAP_PROXY_PASS = PasswordDecrypter.decrypt(os.getenv('CMAP_PROXY_PASS') or 'password')
        self.CMAP_PROXY_CERT = os.getenv('CMAP_PROXY_CERT') or 'proxy.crt'
        self.CMAP_PROXY_KEY = os.getenv('CMAP_PROXY_KEY') or 'proxy.key'
        self.VERTIGOUSER = os.getenv('VERTIGOUSER') or 'vertuser'
        self.VERTIGOPASS = os.getenv('VERTIGOPASS') or 'vertpass'
        self.VERTIGOPASS = PasswordDecrypter.decrypt(self.VERTIGOPASS)
        self.TOOLZILLAUSER = os.getenv('TOOLZILLAUSER') or 'tzuser'
        self.TOOLZILLAPASS = os.getenv('TOOLZILLAPASS') or 'tzpass'
        self.TOOLZILLAPASS = PasswordDecrypter.decrypt(self.TOOLZILLAPASS)
        self.DIABLOUSER = os.getenv('DIABLOUSER') or 'diablouser'
        self.DIABLOPASS = os.getenv('DIABLOPASS') or 'diablopass'
        self.DIABLOPASS = PasswordDecrypter.decrypt(self.DIABLOPASS)
        self.ANGELOUSER = os.getenv('ANGELOUSER') or 'angelouser'
        self.ANGELOPASS = os.getenv('ANGELOPASS') or 'angelopass'
        self.ANGELOPASS = PasswordDecrypter.decrypt(self.ANGELOPASS)
        self.SMDBUSER = os.getenv('SMDBUSER') or 'smdbuser'
        self.SMDBPASS = os.getenv('SMDBPASS') or 'smdbpass'
        self.SMDBPASS = PasswordDecrypter.decrypt(self.SMDBPASS)
        self.ACCESS_ID = os.getenv('ACCESS_ID') or 'access.id'
        self.ACCESS_ID = PasswordDecrypter.decrypt(self.ACCESS_ID)
        self.SECRET_ACCESS_KEY = os.getenv('SECRET_ACCESS_KEY') or 'secret.access.key'
        self.SECRET_ACCESS_KEY = PasswordDecrypter.decrypt(self.SECRET_ACCESS_KEY)


class ProductionAppConfig(AppConfig):
    DB = 'phishstory'
    DB_HOST = '10.22.9.209'
    DB_USER = 'sau_p_phish'
    SMDB_URL = 'https://smdb.int.godaddy.com/IPService/ipam.asmx?WSDL'

    def __init__(self):
        super(ProductionAppConfig, self).__init__()


class OTEAppConfig(AppConfig):
    DB = 'otephishstory'
    DB_HOST = '10.22.9.209'
    DB_USER = 'sau_o_phish'
    SMDB_URL = 'https://smdb.test.intranet.gdg/ipservice/ipam.asmx?WSDL'

    def __init__(self):
        super(OTEAppConfig, self).__init__()


class DevelopmentAppConfig(AppConfig):
    DB = 'devphishstory'
    DB_HOST = '10.22.188.208'
    DB_USER = 'devuser'
    SMDB_URL ='https://smdb.int.dev-godaddy.com/IPService/ipam.asmx?WSDL'

    def __init__(self):
        super(DevelopmentAppConfig, self).__init__()


class LocalAppConfig(AppConfig):
    DB = 'local'
    DB_HOST = 'localhost'
    SMDB_URL ='https://smdb.int.dev-godaddy.com/IPService/ipam.asmx?WSDL'

    def __init__(self):
        super(LocalAppConfig, self).__init__()
        self.DBURL = 'mongodb://{}/{}'.format(self.DB_HOST, self.DB)


config_by_name = {'dev': DevelopmentAppConfig,
                  'prod': ProductionAppConfig,
                  'ote': OTEAppConfig,
                  'local': LocalAppConfig}
