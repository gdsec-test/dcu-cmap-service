import re
import json
import xml.etree.ElementTree as ET


class RegDbAPI(object):
    _WSDL = 'https://dsweb.prod.phx3.gdg/RegDBWebSvc/RegDBWebSvc.dll?Handler=GenRegDBWebSvcWSDL'
    REDIS_KEY = 'result'

    def __init__(self, redis_obj):
        from suds.client import Client
        self._client = Client(self._WSDL)
        self._redis = redis_obj

    def get_domain_count_by_shopper_id(self, shopper_id):
        xml_query = '<request><shopper shopperid="{}"/></request>'.format(shopper_id)
        xml_response = self._client.service.GetDomainCountByShopperID(xml_query)
        match = re.search('domaincount="(\d+)"', xml_response)
        return match.group(1)

    def get_parent_child_shopper_by_domain_name(self, domain_name):
        # Check redis cache for self.domain key
        redis_key = '{}-reseller_parent_child'.format(domain_name)
        query_value = self._redis.get_value(redis_key)
        if query_value is None:
            xml_response = self._client.service.GetParentChildShopperByDomainName(domain_name)
            match = re.search('<PARENT_SHOPPER_ID>(\d+)</PARENT_SHOPPER_ID><CHILD_SHOPPER_ID>(\d+)</CHILD_SHOPPER_ID>',
                              xml_response)
            if match is None:
                query_value = dict(parent=None, child=None)
            else:
                query_value = dict(parent=match.group(1), child=match.group(2))
            self._redis.set_value(redis_key, json.dumps({self.REDIS_KEY: query_value}))
        else:
            query_value = json.loads(query_value).get(self.REDIS_KEY)
        return query_value

    def get_shopper_id_by_domain_name(self, domain_name):
        doc = self._client.service.GetShopperIdByDomainName(domain_name)
        active_shopper = re.search(r'SHOPPER_ID>(\d+)', doc).group(1)
        return active_shopper

    def get_domain_list_by_shopper_id(self, shopper_id):
        domain_data = ET.fromstring(self._client.service.GetDomainListByShopperID(shopper_id, '', 0, 0, 10000))
        data = [(node.findtext('DOMAIN_ID'), node.findtext('DOMAIN_NAME')) for node in domain_data.iter('RECORD')]
        return data
