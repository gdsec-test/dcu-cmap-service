import json
import logging
import xml.etree.ElementTree as ET

from request_transport import RequestsTransport
from suds.client import Client
from functions import return_expected_dict_due_to_exception


class CrmClientApi(object):
    _LOCATION = 'https://crm.cmap.proxy.int.godaddy.com/Shopper.svc'
    _WSDL = _LOCATION + '?singleWsdl'
    _FACTORY = '{http://schemas.datacontract.org/2004/07/GoDaddy.CRM.ClientAPI.DataContracts}ShopperPortfolioInformationRequest'
    REDIS_DATA_KEY = 'result'

    def __init__(self, settings, redis_obj):
        self._logger = logging.getLogger(__name__)
        self._redis = redis_obj
        try:
            self._client = Client(self._WSDL, location=self._LOCATION,
                                  headers=RequestsTransport.get_soap_headers(),
                                  transport=RequestsTransport(username=settings.CMAP_PROXY_USER,
                                                              password=settings.CMAP_PROXY_PASS,
                                                              cert=settings.CMAP_PROXY_CERT,
                                                              key=settings.CMAP_PROXY_KEY))
            self._request = self._client.factory.create(self._FACTORY)
        except Exception as e:
            self._logger.error("Failed CRM Client Init: {}".format(e.message))

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
                    query_dict = {"portfolioType": "No Premium Services For This Shopper"}
                else:
                    hold_dict = doc.find(".//*[@PortfolioType]").attrib
                    query_dict = {'accountRepFirstName': hold_dict.get('FirstName', None),
                                  'accountRepLastName': hold_dict.get('LastName', None),
                                  'accountRepEmail': hold_dict.get('Email', None),
                                  'shopper_id': hold_dict.get('shopper_id', None),
                                  'portfolioType': hold_dict.get('PortfolioType', None)
                                  }
                self._redis.set_value(redis_record_key, json.dumps({self.REDIS_DATA_KEY: query_dict}))
            else:
                query_dict = json.loads(query_dict).get(self.REDIS_DATA_KEY)
        except Exception as e:
            self._logger.error("Error in getting the CRM API portfolio info for %s : %s", shopper_id, e.message)
            # If exception occurred before query_value had completed assignment, set keys to None
            query_dict = return_expected_dict_due_to_exception(query_dict, ['shopper_id',
                                                                            'accountRepFirstName',
                                                                            'accountRepLastName',
                                                                            'accountRepEmail',
                                                                            'portfolioType',
                                                                            'blacklist'])
        return query_dict
