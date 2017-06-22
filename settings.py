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

    def __init__(self):
        self.REDIS = os.getenv('REDIS') or 'redis'
        self.DB_PASS = os.getenv('DB_PASS') or 'password'
        self.DB_PASS = urllib.quote(PasswordDecrypter.decrypt(self.DB_PASS))
        self.DBURL = 'mongodb://{}:{}@{}/{}'.format(self.DB_USER, self.DB_PASS, self.DB_HOST, self.DB)
        self.CMAP_PROXY_USER = os.getenv('CMAP_PROXY_USER') or 'user'
        self.CMAP_PROXY_PASS = PasswordDecrypter.decrypt(os.getenv('CMAP_PROXY_PASS') or 'password')
        self.CMAP_PROXY_CERT = os.getenv('CMAP_PROXY_CERT') or 'proxy.crt'
        self.CMAP_PROXY_KEY = os.getenv('CMAP_PROXY_KEY') or 'proxy.key'
        self.ACCESS_ID = os.getenv('ACCESS_ID') or 'access.id'
        self.ACCESS_ID = urllib.quote(PasswordDecrypter.decrypt(self.ACCESS_ID))
        self.SECRET_ACCESS_KEY = os.getenv('SECRET_ACCESS_KEY') or 'secret.access.key'
        self.SECRET_ACCESS_KEY = urllib.quote(PasswordDecrypter.decrypt(self.SECRET_ACCESS_KEY))


class ProductionAppConfig(AppConfig):
    DB = 'phishstory'
    DB_HOST = '10.22.9.209'
    DB_USER = 'sau_p_phish'

    def __init__(self):
        super(ProductionAppConfig, self).__init__()


class OTEAppConfig(AppConfig):
    DB = 'otephishstory'
    DB_HOST = '10.22.9.209'
    DB_USER = 'sau_o_phish'

    def __init__(self):
        super(OTEAppConfig, self).__init__()


class DevelopmentAppConfig(AppConfig):
    DB = 'devphishstory'
    DB_HOST = '10.22.188.208'
    DB_USER = 'devuser'

    def __init__(self):
        super(DevelopmentAppConfig, self).__init__()


class LocalAppConfig(AppConfig):
    DB = 'local'
    DB_HOST = 'localhost'

    def __init__(self):
        super(LocalAppConfig, self).__init__()
        self.DBURL = 'mongodb://{}/{}'.format(self.DB_HOST, self.DB)


config_by_name = {'dev': DevelopmentAppConfig,
                  'prod': ProductionAppConfig,
                  'ote': OTEAppConfig,
                  'local': LocalAppConfig}
