import json
import logging
import functions

import xml.etree.ElementTree as ET
from request_transport import RequestsTransport
from suds.client import Client
from functions import return_expected_dict_due_to_exception


class ShopperAPI(object):
    _LOCATION = 'https://shopper.cmap.proxy.int.godaddy.com:8443/WSCgdShopper/WSCgdShopper.dll'
    _WSDL = _LOCATION + '?Handler=GenWSCgdShopperWSDL'
    DATE_STRING = 'date_created'
    ENCODING = 'utf8'
    SOAP_METHOD = 'xml'
    REQUESTED_BY = 'DCU-ENG'
    REDIS_DATA_KEY = 'result'

    def __init__(self, settings, redis_obj):
        self._client = Client(self._WSDL, location=self._LOCATION, 
                              headers=RequestsTransport.get_soap_headers(),
                              transport=RequestsTransport(username=settings.CMAP_PROXY_USER,
                                                          password=settings.CMAP_PROXY_PASS,
                                                          cert=settings.CMAP_PROXY_CERT,
                                                          key=settings.CMAP_PROXY_KEY))
        self._redis = redis_obj

    def get_shopper_by_domain_name(self, domain_name, fields):
        """
        Return fields by domain
        :param domain_name:
        :param fields:
        :return:
        """
        query_list = []
        try:
            if domain_name is None or domain_name == '':
                raise ValueError('Blank domain name was provided')
            redis_record_key = '{}-shopper_info_by_domain'.format(domain_name)
            query_list = self._redis.get_value(redis_record_key)
            if query_list is None:
                shopper_search = ET.Element("ShopperSearch", IPAddress='', RequestedBy=self.REQUESTED_BY)
                search_fields = ET.SubElement(shopper_search, 'SearchFields')
                ET.SubElement(search_fields, 'Field', Name='domain').text = domain_name

                return_fields = ET.SubElement(shopper_search, "ReturnFields")
                for field_item in fields:
                    ET.SubElement(return_fields, 'Field', Name=field_item)
                xmlstr = ET.tostring(shopper_search, encoding=self.ENCODING, method=self.SOAP_METHOD)
                data = ET.fromstring(self._client.service.SearchShoppers(xmlstr))
                query_list = [item.attrib for item in data.iter('Shopper')]
                for query_index in range(len(query_list)):
                    if self.DATE_STRING in query_list[query_index]:
                        # Change the format of the date string
                        query_list[query_index][self.DATE_STRING] = functions.convert_string_date_to_mongo_format(
                            query_list[query_index].get(self.DATE_STRING))
                self._redis.set_value(redis_record_key, json.dumps({self.REDIS_DATA_KEY: query_list}))
            else:
                query_list = json.loads(query_list).get(self.REDIS_DATA_KEY)
        except Exception as e:
            logging.error("Error in getting the shopper info for %s : %s", domain_name, e.message)
            # If exception occurred before query_value had completed assignment, set keys to None
            query_list = list(return_expected_dict_due_to_exception(query_list, fields))
        return query_list

    def get_shopper_by_shopper_id(self, shopper_id, fields):
        """
        Return fields by shopper id
        :param shopper_id:
        :param fields:
        :return:
        """
        query_dict = {}
        try:
            if shopper_id is None or shopper_id == '':
                raise ValueError('Blank shopper id was provided')
            redis_record_key = '{}-shopper_info_by_id'.format(shopper_id)
            query_dict = self._redis.get_value(redis_record_key)
            if query_dict is None:
                shopper_search = ET.Element("ShopperGet", IPAddress='', RequestedBy=self.REQUESTED_BY, ID=shopper_id)
                return_fields = ET.SubElement(shopper_search, "ReturnFields")
                for field in fields:
                    ET.SubElement(return_fields, 'Field', Name=field)
                xmlstr = ET.tostring(shopper_search, encoding=self.ENCODING, method=self.SOAP_METHOD)
                data = ET.fromstring(self._client.service.GetShopper(xmlstr))
                query_dict = {item.attrib['Name']: item.text for item in data.iter('Field')}
                if self.DATE_STRING in query_dict:
                    # Change the format of the date string
                    query_dict[self.DATE_STRING] = functions.convert_string_date_to_mongo_format(
                        query_dict.get(self.DATE_STRING))
                self._redis.set_value(redis_record_key, json.dumps({self.REDIS_DATA_KEY: query_dict}))
            else:
                query_dict = json.loads(query_dict).get(self.REDIS_DATA_KEY)
        except Exception as e:
            logging.error("Error in getting the shopper info for %s : %s", shopper_id, e.message)
            # If exception occurred before query_value had completed assignment, set keys to None
            query_dict = return_expected_dict_due_to_exception(query_dict, fields)
        return query_dict
