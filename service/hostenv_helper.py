from pathos.multiprocessing import ProcessingPool as Pool
from itertools import product
from diablo_api import DiabloApi
from vertigo_api import VertigoApi
from angelo_api import AngeloApi
# from tz_api import ToolzillaApi
from suds.client import Client
from suds.sax.element import Element
import ssl
from enrichment import nutrition_label
import logging


class Shotgun(object):

    def __init__(self, config):
        self.tz_pass = config.TOOLZILLAPASS
        self.vrun = VertigoApi(config)
        self.drun = DiabloApi(config)
        self.arun = AngeloApi(config)
        #self.trun = ToolzillaApi(config)

    def run_guid(self, data):
        env = data[0]
        domain = data[1]
        if env == 'vertigo':
            return self.vrun.guid_query(domain)
        elif env == 'diablo':
            return self.drun.guid_query(domain)
        elif env == 'angelo':
            return self.arun.guid_query(domain)
        elif env == 'tz':
            return self.guid_query(domain)

    def get_hostname_tz(self, guid):
        url = 'https://toolzilla.int.godaddy.com/webservice.php/AccountSearchService/WSDL'
        user = 'svc_dcu'
        pwd = self.tz_pass

        if pwd is not None:

            auth_head = Element('acc:Authentication User="' + user + '" Password="' + pwd + '"')
            ssl._create_default_https_context = ssl._create_unverified_context

            client = Client(url)
            client.set_options(soapheaders=auth_head)

        else:
            print 'no tz password passed'

        try:

            hostname = client.service.getHostNameByGuid(guid)
            hostname = hostname.split('.')[0]
            hostname = hostname.lower()

            enrichment = nutrition_label(hostname)
            dc = enrichment[0]
            os = enrichment[1]
            product = enrichment[2]

            data = [dc, os, product]

            return data

        except Exception as e:
            print str(e)
            print client.last_received()

    def guid_query(self, domain):
        """
        Queries the Toolzilla API for a GUID for a domain name.
        :param domain:
        :return: GUID or None
        """
        url = 'https://toolzilla.int.godaddy.com/webservice.php/AccountSearchService/WSDL'
        user = 'svc_dcu'
        pwd = self.tz_pass

        if pwd is not None:

            auth_head = Element('acc:Authentication User="' + user + '" Password="' + pwd + '"')
            ssl._create_default_https_context = ssl._create_unverified_context

            client = Client(url)
            client.set_options(soapheaders=auth_head)

        else:
            print 'no tz password passed'

        try:
            data = client.service.searchByDomain(domain)
            # checks to make sure the returned data is not an error
            if str(type(data)) != "<class 'suds.sax.text.Text'>":
                logging.info('Domain searched for: %s', domain)
                hosting_guid = str(data[0][0][2][0])
                return hosting_guid

            return None

        except Exception as e:
            logging.error(e.message)
            logging.error(client.last_received())
            return None

    def setrun(self, domain):
        pool = Pool()
        data = []
        try:
            result = pool.map(self.run_guid, [x for x in product(*[['angelo', 'vertigo', 'diablo', 'tz'], [domain]])])
            env = [self.get_hostname_tz(x) for x in result if x]
            result = filter(lambda x: x is not None, result)
            for x in env[0]:
                data.append(x)

            data.append(result[0])

        except Exception as e:
            print str(e)

        finally:
            pool.close()
            pool.join()
            return data
