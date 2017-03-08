import xml.etree.ElementTree as ET
import re

from datetime import datetime
from whois import NICClient


class KnoxAPI(object):
    #test WSDL
    _WSDL = 'https://shopper.test.glbt1.gdg/WSCgdShopper/WSCgdShopper.dll?Handler=GenWSCgdShopperWSDL'

    def __init__(self):
        from suds.client import Client
        self._client = Client(self._WSDL, timeout=5)

    def get_shopper_info(self, domain):
        """
        Returns a tuple containing the shopper id, and the date created
        :param domain:
        :return:
        """
        #try:
        doc = ET.fromstring(self._lookup_shopper_info(domain))
        elem = doc.find(".//*[@shopper_id]")
        print elem.get('shopper_id'), datetime.strptime(elem.get('date_created'), '%m/%d/%Y %I:%M:%S %p')
        #except Exception as e:
        #    #self._logger.error("Unable to lookup shopper info for {}:{}".format(domain, e))
        #    return None, None

    def _lookup_shopper_info(self, domain):
        """
        Returns the xml representing the shopper id(s)
        :param domain:
        :return:
        """
        shopper_search = ET.Element("ShopperSearch", IPAddress='', RequestedBy='DCU-ENG')
        searchFields = ET.SubElement(shopper_search, 'SearchFields')
        ET.SubElement(searchFields, 'Field', Name='domain').text = domain

        returnFields = ET.SubElement(shopper_search, "ReturnFields")
        ET.SubElement(returnFields, 'Field', Name='shopper_id')
        ET.SubElement(returnFields, 'Field', Name='date_created')
        xmlstr = ET.tostring(shopper_search, encoding='utf8', method='xml')
        # The following Fort Knox client will timeout on the dev side, unless a firewall rule is created
        #  allowing access from dev Rancher, which means no shopper id, account create date, etc when
        #  running from dev
        # client = Client(self._WSDL, timeout=5)
        client = self._client
        return client.service.SearchShoppers(xmlstr)


    def domain_whois(self, domain_name):
        """
        Returns a tuple
        Possible return value for first in tuple could be REG or NOT_REG_HOSTED based on being registered with GoDaddy
        or elsewhere
        Possible return value for second in tuple is the creation date of a registered only domain or None if registered
        elsewhere
        :param domain_name:
        :return:
        """
        whois_server = 'whois.godaddy.com'
        nicclient = NICClient()
        domain_name = domain_name[4:] if domain_name[:4] == 'www.' else domain_name
        #try:
        domain = nicclient.whois(domain_name, whois_server, True)
        if "No match" not in domain:
                #try:
                    # get creation date from whois and format it
            creation_date = datetime.strptime(re.search(r'Creation Date:\s?(\S+)', domain).group(1),
                                              '%Y-%m-%dT%H:%M:%SZ')
            print creation_date
                # except Exception as e:
                #     self._logger.error("Error in determing create date of %s : %s", domain_name, e.message)
                #     return URIHelper.REG, None
        #     else:
        #         return URIHelper.NOT_REG_HOSTED, None
        # except Exception as e:
        #     self._logger.error("Error in determing whois of %s : %s", domain_name, e.message)
        return None


    # def domain_whois(self, domain_name):
    #     """
    #     Returns a tuple
    #     Possible return value for first in tuple could be REG or NOT_REG_HOSTED based on being registered with GoDaddy
    #     or elsewhere
    #     Possible return value for second in tuple is the creation date of a registered only domain or None if registered
    #     elsewhere
    #     :param domain_name:
    #     :return:
    #     """
    #     whois_server = 'whois.godaddy.com'
    #     nicclient = NICClient()
    #     domain_name = domain_name[4:] if domain_name[:4] == 'www.' else domain_name
    #     #try:
    #     domain = nicclient.whois(domain_name, whois_server, True)
    #     if "No match" not in domain:
    #             #try:
    #                 # get creation date from whois and format it
    #         creation_date = datetime.strptime(re.search(r'Creation Date:\s?(\S+)', domain).group(1),
    #                                           '%Y-%m-%dT%H:%M:%SZ')
    #         print creation_date
    #             # except Exception as e:
    #             #     self._logger.error("Error in determing create date of %s : %s", domain_name, e.message)
    #             #     return URIHelper.REG, None
    #     #     else:
    #     #         return URIHelper.NOT_REG_HOSTED, None
    #     # except Exception as e:
    #     #     self._logger.error("Error in determing whois of %s : %s", domain_name, e.message)
    #     return None


if __name__ == '__main__':
    knox = KnoxAPI()
    knox.get_shopper_info("dmvsuspension.com")
    # ox.domain_whois("lancehalvorson.com")



