import json
import logging
import xml.etree.ElementTree as ET

from request_transport import RequestsTransport
from functions import get_tld_by_domain_name


class RegDbAPI(object):
    _LOCATION = 'https://dsweb.cmap.proxy.int.godaddy.com/RegDBWebSvc/RegDBWebSvc.dll'
    _WSDL = _LOCATION + '?Handler=GenRegDBWebSvcWSDL'
    REDIS_DATA_KEY = 'result'

    def __init__(self, settings, redis_obj):
        self._logger = logging.getLogger(__name__)
        self._redis = redis_obj
        from suds.client import Client
        try:
            self._client = Client(self._WSDL, location=self._LOCATION,
                                  headers=RequestsTransport.get_soap_headers(),
                                  transport=RequestsTransport(username=settings.CMAP_PROXY_USER,
                                                              password=settings.CMAP_PROXY_PASS,
                                                              cert=settings.CMAP_PROXY_CERT,
                                                              key=settings.CMAP_PROXY_KEY))
        except Exception as e:
            self._logger.error("Failed REG DB Client Init: %s", e.message)

    def get_domain_count_by_shopper_id(self, shopper_id):
        # Check redis cache for domain count
        redis_record_key = '{}-domain_count'.format(shopper_id)
        try:
            query_value = self._redis.get_value(redis_record_key)
            if query_value is None:
                xml_query = '<request><shopper shopperid="{}"/></request>'.format(shopper_id)
                doc = ET.fromstring(self._client.service.GetDomainCountByShopperID(xml_query))
                if doc.find(".//*[@domaincount]") is not None:
                    query_value = doc.find(".//*[@domaincount]").get('domaincount')
                self._redis.set_value(redis_record_key, query_value)
            return query_value
        except Exception as e:
            self._logger.error("Error in getting the domain count for %s : %s", shopper_id, e.message)

    def get_parent_child_shopper_by_domain_name(self, domain_name_as_provided):
        # In the event that we were provided a sub-domain name as opposed to a tld
        domain_name = get_tld_by_domain_name(domain_name_as_provided)
        # Check redis cache for parent/child api reseller info
        redis_record_key = u'{}-reseller_parent_child'.format(domain_name)
        try:
            query_value = self._redis.get_value(redis_record_key)
            if query_value is None:
                doc = ET.fromstring(self._client.service.GetParentChildShopperByDomainName(domain_name.encode('idna')))
                if doc.find('RECORDSET') is None or doc.find('RECORDSET').find('RECORD') is None:
                    query_value = dict(parent=None, child=None)
                else:
                    doc_record = doc.find('RECORDSET').find('RECORD')
                    parent = doc_record.find('PARENT_SHOPPER_ID').text
                    child = doc_record.find('CHILD_SHOPPER_ID').text
                    query_value = dict(parent=parent, child=child)
                self._redis.set_value(redis_record_key, json.dumps({self.REDIS_DATA_KEY: query_value}))
            else:
                query_value = json.loads(query_value).get(self.REDIS_DATA_KEY)
            return query_value
        except Exception as e:
            self._logger.error("Error in getting the parent/child api reseller for %s : %s", domain_name, e.message)

    def get_shopper_id_by_domain_name(self, domain_name_as_provided):
        # In the event that we were provided a sub-domain name as opposed to a tld
        domain_name = get_tld_by_domain_name(domain_name_as_provided)

        # Check redis cache for shopper id
        redis_record_key = u'{}-shopper_id_by_domain'.format(domain_name)
        try:
            query_value = self._redis.get_value(redis_record_key)
            if query_value is None:
                doc = ET.fromstring(self._client.service.GetShopperIdByDomainName(domain_name.encode('idna')))
                if doc.find('RECORDSET') is None or \
                                doc.find('RECORDSET').find('RECORD') is None or \
                                doc.find('RECORDSET').find('RECORD').find('SHOPPER_ID') is None:
                    return None
                query_value = doc.find('RECORDSET').find('RECORD').find('SHOPPER_ID').text
                self._redis.set_value(redis_record_key, query_value)
            return query_value
        except Exception as e:
            self._logger.error("Error in getting the shopper id for %s : %s", domain_name, e.message)

    def get_domain_list_by_shopper_id(self, shopper_id):
        # Check redis cache for domain list by shopper id
        redis_record_key = '{}-domain_list_by_shopper'.format(shopper_id)
        try:
            query_value = self._redis.get_value(redis_record_key)
            if query_value is None:
                domain_data = ET.fromstring(self._client.service.GetDomainListByShopperID(shopper_id, '', 0, 0, 10000))
                query_value = [(node.findtext('DOMAIN_ID'), node.findtext('DOMAIN_NAME'))
                               for node in domain_data.iter('RECORD')]
                self._redis.set_value(redis_record_key, json.dumps({self.REDIS_DATA_KEY: query_value}))
            else:
                query_value = json.loads(query_value).get(self.REDIS_DATA_KEY)
            return query_value
        except Exception as e:
            self._logger.error("Error in getting the domain list for %s : %s", shopper_id, e.message)
