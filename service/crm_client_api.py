import re
import json
import logging

import xml.etree.ElementTree as ET

from suds.client import Client


class CrmClientApi(object):
    _WSDL = 'https://crmclient-api.prod.phx3.int.godaddy.com/Shopper.svc?singleWsdl'
    _FACTORY = '{http://schemas.datacontract.org/2004/07/GoDaddy.CRM.ClientAPI.DataContracts}ShopperPortfolioInformationRequest'
    REDIS_KEY = 'result'

    def __init__(self, redis_obj):
        self._client = Client(self._WSDL)
        self._request = self._client.factory.create(self._FACTORY)
        self._redis = redis_obj

    def get_shopper_portfolio_information(self, shopper_id):
        try:
            redis_key = '{}-portfolio_info'.format(shopper_id)
            query_value = self._redis.get_value(redis_key)
            if query_value is None:
                self._request.shopperID = shopper_id
                resp = self._client.service.GetShopperPortfolioInformation(self._request)
                match = re.search('<data count=.(\d+).>', resp.ResultXml)
                if match.group(1) == '0':
                    query_value = {"PortfolioType": "No Premium Services For This Shopper"}
                else:
                    doc = ET.fromstring(resp.ResultXml)
                    query_value = doc.find(".//*[@PortfolioType]").attrib
                self._redis.set_value(redis_key, json.dumps({self.REDIS_KEY: query_value}))
            else:
                query_value = json.loads(query_value).get(self.REDIS_KEY)
            return query_value
        except Exception as e:
            logging.warning("Error in getting the CRM API portfolio info for %s : %s", shopper_id, e.message)
