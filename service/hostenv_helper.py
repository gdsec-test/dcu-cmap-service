from multiprocessing import Pool
from itertools import product
from diablo_api import DiabloApi
from vertigo_api import VertigoApi
from angelo_api import AngeloApi
from tz_api import ToolzillaApi
from suds.client import Client
from blindal.crypter import Crypter
from suds.sax.element import Element
import ssl
import os
from settings import config_by_name
from enrichment import nutrition_label

env = os.getenv('sysenv') or 'dev'
config = config_by_name[env]()
vrun = VertigoApi(config)
drun = DiabloApi(config)
arun = AngeloApi(config)
trun = ToolzillaApi(config)


class Shotgun(object):

    def run_guid(self, data):
        env = data[0]
        domain = data[1]
        if env == 'vertigo':
            return vrun.guid_query(domain)
        elif env == 'diablo':
            return drun.guid_query(domain)
        elif env == 'angelo':
            return arun.guid_query(domain)
        elif env == 'tz':
            return trun.guid_query(domain)

    def get_hostname_tz(self, guid):
        url = 'https://toolzilla.int.godaddy.com/webservice.php/AccountSearchService/WSDL'
        user = 'svc_dcu'
        pwd = config.get('TOOLZILLAPASS', None)

        data = None

        with open("key.txt", "r") as f:
            data = f.readline().split()

        if pwd is not None:
            pwd = Crypter.decrypt(pwd, data[0], data[1])
        else:
            print 'no tz password passed'

        auth_head = Element('acc:Authentication User="' + user + '" Password="' + pwd + '"')
        ssl._create_default_https_context = ssl._create_unverified_context

        client = Client(url)
        client.set_options(soapheaders=auth_head)

        try:

            hostname = client.service.getHostNameByGuid(guid)
            hostname = hostname.split('.')[0]
            hostname = hostname.lower()

            enrichment = nutrition_label(hostname)
            dc = enrichment[0]
            os = enrichment[1]
            product = enrichment[2]

            return hostname, dc, os, product

        except Exception as e:
            print str(e)
            print client.last_received()

    def setrun(self, domain):
        pool = Pool()
        try:
            result = pool.map(self.run_guid, [x for x in product(*[['angelo', 'vertigo', 'diablo', 'tz'], [domain]])])
            env = [self.get_hostname_tz(x) for x in result if x]
            return env

        except Exception as e:
            print str(e)

        finally:
            pool.close()
            pool.join()
