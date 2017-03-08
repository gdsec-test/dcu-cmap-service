import logging
import xml.etree.ElementTree as ET

from datetime import datetime
from suds.client import Client


class ShopperAPI(object):
    _WSDL = 'https://shopper.prod.phx3.gdg/WSCgdShopper/WSCgdShopper.dll?Handler=GenWSCgdShopperWSDL'

    def __init__(self):
        self._client = Client(self._WSDL, timeout=5)

    def get_shopper_by_domain_name(self, domain, fields):
        """
        Return fields by domain
        :param domain:
        :return:
        """
        shopper_search = ET.Element("ShopperSearch", IPAddress='', RequestedBy='DCU-ENG')
        searchFields = ET.SubElement(shopper_search, 'SearchFields')
        ET.SubElement(searchFields, 'Field', Name='domain').text = domain

        returnFields = ET.SubElement(shopper_search, "ReturnFields")
        for field_item in fields:
            ET.SubElement(returnFields, 'Field', Name=field_item)
        xmlstr = ET.tostring(shopper_search, encoding='utf8', method='xml')
        data = ET.fromstring(self._client.service.SearchShoppers(xmlstr))
        return [item.attrib for item in data.iter('Shopper')]

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

    def get_shopper_by_shopper_id(self, shopper, fields):
        """
        Return fields by shopper id
        :param shopper:
        :param fields:
        :return:
        """
        shopper_search = ET.Element("ShopperGet", IPAddress='', RequestedBy='DCU-ENG', ID=shopper)
        returnFields = ET.SubElement(shopper_search, "ReturnFields")
        for field in fields:
            ET.SubElement(returnFields, 'Field', Name=field)
        xmlstr = ET.tostring(shopper_search, encoding='utf8', method='xml')
        data = ET.fromstring(self._client.service.GetShopper(xmlstr))
        return {item.attrib['Name']: item.text for item in data.iter('Field')}

    def get_shopper_info(self, domain):
        """
        Returns a tuple containing the shopper id, and the date created
        :param domain:
        :return:
        """
        #try:
        # doc = ET.fromstring(self._lookup_shopper_info(domain))
        doc = ET.fromstring(self.get_shopper_by_domain_name(self.domain, ['shopper_id', 'date_created']))
        elem = doc.find(".//*[@shopper_id]")
        return elem.get('shopper_id'), datetime.strptime(elem.get('date_created'), '%m/%d/%Y %I:%M:%S %p')
        #except Exception as e:
        #    #self._logger.error("Unable to lookup shopper info for {}:{}".format(domain, e))
        #    return None, None


