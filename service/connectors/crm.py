import json
import logging
import xml.etree.ElementTree as ET

from suds.client import Client

from service.soap.request_transport import RequestsTransport
from service.utils.functions import return_expected_dict_due_to_exception


class CRMClientAPI(object):
    _factory = '{http://schemas.datacontract.org/2004/07/GoDaddy.CRM.ClientAPI.DataContracts}ShopperPortfolioInformationRequest'
    _redis_key = 'result'

    def __init__(self, settings, redis_obj):
        self._logger = logging.getLogger(__name__)
        self._redis = redis_obj

        location = 'https://crmclient-api.prod.phx3.int.godaddy.com/Shopper.svc'
        wsdl = location + '?singleWsdl'

        try:
            self._client = Client(wsdl, location=location,
                                  headers=RequestsTransport.get_soap_headers(),
                                  transport=RequestsTransport(cert=settings.CMAP_API_CERT,
                                                              key=settings.CMAP_API_KEY))
            self._request = self._client.factory.create(self._factory)
        except Exception as e:
            self._logger.error('Failed CRM Client Init: {}'.format(e))

    def get_shopper_portfolio_information(self, shopper_id):
        '''
        Determine a given shopper's PortfolioInformation based on their ShopperID. This may include information
        such as what GoDaddy Representative managers their account, the Rep's email, etc.
        :param shopper_id:
        :return:
        '''

        query_dict = {}

        try:
            if not shopper_id:
                raise ValueError('Blank shopper id was provided')

            redis_record_key = '{}-portfolio_info'.format(shopper_id)
            query_dict = self._redis.get(redis_record_key)

            if query_dict is None:
                self._request.shopperID = shopper_id
                doc = ET.fromstring(self._client.service.GetShopperPortfolioInformation(self._request).ResultXml)
                if doc.find('.//*[@PortfolioType]') is None:
                    query_dict = {'portfolioType': 'No Premium Services For This Shopper'}
                else:
                    hold_dict = doc.find('.//*[@PortfolioType]').attrib
                    query_dict = {'accountRepFirstName': hold_dict.get('FirstName'),
                                  'accountRepLastName': hold_dict.get('LastName'),
                                  'accountRepEmail': hold_dict.get('Email'),
                                  'shopper_id': hold_dict.get('shopper_id'),
                                  'portfolioType': hold_dict.get('PortfolioType')}
                self._redis.set(redis_record_key, json.dumps({self._redis_key: query_dict}))
            else:
                query_dict = json.loads(query_dict).get(self._redis_key)
        except Exception as e:
            self._logger.error('Error in getting the CRM API portfolio info for {} : {}'.format(shopper_id, e))

            query_dict = return_expected_dict_due_to_exception(query_dict, ['shopper_id',
                                                                            'accountRepFirstName',
                                                                            'accountRepLastName',
                                                                            'accountRepEmail',
                                                                            'portfolioType',
                                                                            'blacklist'])
        return query_dict
