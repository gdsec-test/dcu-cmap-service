import json
import logging

import xml.etree.ElementTree as ET

from suds.client import Client
from functions import return_expected_dict_due_to_exception


class CrmClientApi(object):
    _WSDL = 'https://crmclient-api.prod.phx3.int.godaddy.com/Shopper.svc?singleWsdl'
    _FACTORY = '{http://schemas.datacontract.org/2004/07/GoDaddy.CRM.ClientAPI.DataContracts}ShopperPortfolioInformationRequest'
    REDIS_DATA_KEY = 'result'

    def __init__(self, redis_obj):
        self._client = Client(self._WSDL)
        self._request = self._client.factory.create(self._FACTORY)
        self._redis = redis_obj

    def get_shopper_portfolio_information(self, shopper_id):
        query_dict = {}
        try:
            if shopper_id is None or shopper_id == '':
                raise ValueError('Blank shopper id was provided')
            redis_record_key = '{}-portfolio_info'.format(shopper_id)
            query_dict = self._redis.get_value(redis_record_key)
            if query_dict is None:
                self._request.shopperID = shopper_id
                doc = ET.fromstring(self._client.service.GetShopperPortfolioInformation(self._request).ResultXml)
                if doc.find(".//*[@PortfolioType]") is None:
                    query_dict = {"PortfolioType": "No Premium Services For This Shopper"}
                else:
                    query_dict = doc.find(".//*[@PortfolioType]").attrib
                self._redis.set_value(redis_record_key, json.dumps({self.REDIS_DATA_KEY: query_dict}))
            else:
                query_dict = json.loads(query_dict).get(self.REDIS_DATA_KEY)
        except Exception as e:
            logging.error("Error in getting the CRM API portfolio info for %s : %s", shopper_id, e.message)
            # If exception occurred before query_value had completed assignment, set keys to None
            query_dict = return_expected_dict_due_to_exception(query_dict, ['shopper_id',
                                                                            'accountRep',
                                                                            'FirstName',
                                                                            'LastName',
                                                                            'Email',
                                                                            'PhoneExt',
                                                                            'InternalPhoneQueue',
                                                                            'InternalImageURL',
                                                                            'PortfolioTypeID',
                                                                            'PortfolioType',
                                                                            'blacklist'])
        return query_dict
