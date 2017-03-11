import json
import logging
import functions

import xml.etree.ElementTree as ET

from suds.client import Client


class ShopperAPI(object):
    _WSDL = 'https://shopper.prod.phx3.gdg/WSCgdShopper/WSCgdShopper.dll?Handler=GenWSCgdShopperWSDL'
    DATE_STRING = 'date_created'
    ENCODING = 'utf8'
    SOAP_METHOD = 'xml'
    REQUESTED_BY = 'DCU-ENG'
    REDIS_KEY = 'result'

    def __init__(self, redis_obj):
        self._client = Client(self._WSDL, timeout=5)
        self._redis = redis_obj

    def get_shopper_by_domain_name(self, domain_name, fields):
        """
        Return fields by domain
        :param domain_name:
        :param fields:
        :return:
        """
        try:
            redis_key = '{}-domain_shopper_info'.format(domain_name)
            query_list = self._redis.get_value(redis_key)
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
                self._redis.set_value(redis_key, json.dumps({self.REDIS_KEY: query_list}))
            else:
                query_list = json.loads(query_list).get(self.REDIS_KEY)
            return query_list
        except Exception as e:
            logging.warning("Error in getting the shopper info for %s : %s", domain_name, e.message)

    def get_shopper_by_shopper_id(self, shopper_id, fields):
        """
        Return fields by shopper id
        :param shopper_id:
        :param fields:
        :return:
        """
        try:
            redis_key = '{}-id_shopper_info'.format(shopper_id)
            query_dict = self._redis.get_value(redis_key)
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
                self._redis.set_value(redis_key, json.dumps({self.REDIS_KEY: query_dict}))
            else:
                query_dict = json.loads(query_dict).get(self.REDIS_KEY)
            return query_dict
        except Exception as e:
            logging.warning("Error in getting the shopper info for %s : %s", shopper_id, e.message)
