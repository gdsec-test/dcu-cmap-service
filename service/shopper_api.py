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
        :param fields:
        :return:
        """
        shopper_search = ET.Element("ShopperSearch", IPAddress='', RequestedBy='DCU-ENG')
        search_fields = ET.SubElement(shopper_search, 'SearchFields')
        ET.SubElement(search_fields, 'Field', Name='domain').text = domain

        return_fields = ET.SubElement(shopper_search, "ReturnFields")
        for field_item in fields:
            ET.SubElement(return_fields, 'Field', Name=field_item)
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
        search_fields = ET.SubElement(shopper_search, 'SearchFields')
        ET.SubElement(search_fields, 'Field', Name='domain').text = domain

        return_fields = ET.SubElement(shopper_search, "ReturnFields")
        ET.SubElement(return_fields, 'Field', Name='shopper_id')
        ET.SubElement(return_fields, 'Field', Name='date_created')
        xmlstr = ET.tostring(shopper_search, encoding='utf8', method='xml')
        # The following Fort Knox client will timeout on the dev side, unless a firewall rule is created
        #  allowing access from dev Rancher, which means no shopper id, account create date, etc when
        #  running from dev
        client = self._client
        return client.service.SearchShoppers(xmlstr)

    def get_shopper_by_shopper_id(self, shopper_id, fields):
        """
        Return fields by shopper id
        :param shopper_id:
        :param fields:
        :return:
        """
        shopper_search = ET.Element("ShopperGet", IPAddress='', RequestedBy='DCU-ENG', ID=shopper_id)
        return_fields = ET.SubElement(shopper_search, "ReturnFields")
        for field in fields:
            ET.SubElement(return_fields, 'Field', Name=field)
        xmlstr = ET.tostring(shopper_search, encoding='utf8', method='xml')
        data = ET.fromstring(self._client.service.GetShopper(xmlstr))
        return {item.attrib['Name']: item.text for item in data.iter('Field')}

