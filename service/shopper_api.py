import logging
import xml.etree.ElementTree as ET

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
