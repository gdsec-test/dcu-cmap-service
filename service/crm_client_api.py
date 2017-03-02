import re
import xml.etree.ElementTree as ET


class CrmClientApi(object):
    _WSDL = 'https://crmclient-api.prod.phx3.int.godaddy.com/Shopper.svc?singleWsdl'
    _FACTORY = '{http://schemas.datacontract.org/2004/07/GoDaddy.CRM.ClientAPI.DataContracts}ShopperPortfolioInformationRequest'

    def __init__(self):
        from suds.client import Client
        self._client = Client(self._WSDL)
        self._request = self._client.factory.create(self._FACTORY)

    def get_shopper_portfolio_information(self, shopper_id):
        self._request.shopperID = shopper_id
        resp = self._client.service.GetShopperPortfolioInformation(self._request)
        match = re.search('<data count=.(\d+).>', resp.ResultXml)
        if match.group(1) == '0':
            return "No Premium Services For This Shopper"
        doc = ET.fromstring(resp.ResultXml)
        self._elem = doc.find(".//*[@PortfolioType]").attrib
        return self._elem
