import json
import logging
import xml.etree.ElementTree as ET

from service.soap.request_transport import RequestsTransport
from service.utils.functions import get_tld_by_domain_name


class RegDbAPI(object):
    '''
    Provides an interface for interacting with RegDB which provides information about domains that are registered
    with GoDaddy. Functions include getting domain counts, determining API Reseller, finding shoppers associated with
    a given domain name, etc.
    '''
    _location = 'https://dsweb.cmap.proxy.int.godaddy.com/RegDBWebSvc/RegDBWebSvc.dll'
    _wsdl = _location + '?Handler=GenRegDBWebSvcWSDL'
    _redis_key = 'result'

    def __init__(self, settings, redis_obj):
        self._logger = logging.getLogger(__name__)
        self._redis = redis_obj
        from suds.client import Client
        try:
            self._client = Client(self._wsdl, location=self._location,
                                  headers=RequestsTransport.get_soap_headers(),
                                  transport=RequestsTransport(username=settings.CMAP_PROXY_USER,
                                                              password=settings.CMAP_PROXY_PASS,
                                                              cert=settings.CMAP_PROXY_CERT,
                                                              key=settings.CMAP_PROXY_KEY))
        except Exception as e:
            self._logger.error('Failed REG DB Client Init: {}'.format(e))

    def get_domain_count_by_shopper_id(self, shopper_id):
        '''
        Given a ShopperID, determine how many domains are registered within that shopper.
        :param shopper_id:
        :return:
        '''
        redis_key = '{}-domain_count'.format(shopper_id)
        query_value = None

        try:
            query_value = self._redis.get(redis_key)
            if query_value is None:
                xml_query = '<request><shopper shopperid="{}"/></request>'.format(shopper_id)
                doc = ET.fromstring(self._client.service.GetDomainCountByShopperID(xml_query))
                if doc.find('.//*[@domaincount]') is not None:
                    query_value = doc.find('.//*[@domaincount]').get('domaincount')

                self._redis.set(redis_key, query_value)
            else:
                query_value = query_value.decode()
        except Exception as e:
            self._logger.error('Error in getting the domain count for {} : {}'.format(shopper_id, e))
        finally:
            return query_value

    def get_parent_child_shopper_by_domain_name(self, domain_name_as_provided):
        '''
        Given a domain name, attempt to retrieve the Parent Shopper and the Child Shopper for a domain that is
        registered as part of an API Reseller e.g. Wild West Domains, Google, etc.
        :param domain_name_as_provided:
        :return:
        '''
        # In the event that we were provided a sub-domain name as opposed to a tld
        domain_name = get_tld_by_domain_name(domain_name_as_provided)

        # Check redis cache for parent/child api reseller info
        redis_key = '{}-reseller_parent_child'.format(domain_name)
        query_value = dict(parent=None, child=None)

        try:
            query_value = self._redis.get(redis_key)
            if query_value is None:
                domain_name = domain_name.encode('idna').decode()
                doc = ET.fromstring(self._client.service.GetParentChildShopperByDomainName(domain_name))

                if doc.find('RECORDSET') is None or doc.find('RECORDSET').find('RECORD') is None:
                    query_value = dict(parent=None, child=None)
                else:
                    doc_record = doc.find('RECORDSET').find('RECORD')
                    query_value = dict(parent=doc_record.find('PARENT_SHOPPER_ID').text,
                                       child=doc_record.find('CHILD_SHOPPER_ID').text)
                self._redis.set(redis_key, json.dumps({self._redis_key: query_value}))
            else:
                query_value = json.loads(query_value).get(self._redis_key)
        except Exception as e:
            self._logger.error('Error in getting the parent/child api reseller for {} : {}'.format(domain_name, e))
        finally:
            return query_value

    def get_shopper_id_by_domain_name(self, domain_name_as_provided):
        '''
        Given a domain, attempt to retrieve a corresponding Shopper account.
        :param domain_name_as_provided:
        :return:
        '''

        # In the event that we were provided a sub-domain name as opposed to a tld
        domain_name = get_tld_by_domain_name(domain_name_as_provided)

        redis_key = '{}-shopper_id_by_domain'.format(domain_name)
        query_value = None

        try:
            query_value = self._redis.get(redis_key)

            if not query_value:
                domain_name = domain_name.encode('idna').decode()
                doc = ET.fromstring(self._client.service.GetShopperIdByDomainName(domain_name))

                if doc.find('RECORDSET') is None or \
                        doc.find('RECORDSET').find('RECORD') is None or \
                        doc.find('RECORDSET').find('RECORD').find('SHOPPER_ID') is None:
                    return None

                query_value = doc.find('RECORDSET').find('RECORD').find('SHOPPER_ID').text
                self._redis.set(redis_key, query_value)
            else:
                query_value = query_value.decode()

        except Exception as e:
            self._logger.error('Error in getting the shopper id for {} : {}'.format(domain_name, e))
        finally:
            return query_value

    def get_domain_list_by_shopper_id(self, shopper_id):
        '''
        Given a ShopperID, attempt to return a list of domains that are registered within that shopper.
        :param shopper_id:
        :return:
        '''
        redis_key = '{}-domain_list_by_shopper'.format(shopper_id)
        query_value = None

        try:
            query_value = self._redis.get(redis_key).decode()

            if query_value is None:
                domain_data = ET.fromstring(self._client.service.GetDomainListByShopperID(shopper_id, '', 0, 0, 10000))
                query_value = [(node.findtext('DOMAIN_ID'), node.findtext('DOMAIN_NAME'))
                               for node in domain_data.iter('RECORD')]
                self._redis.set(redis_key, json.dumps({self._redis_key: query_value}))
            else:
                query_value = json.loads(query_value).get(self._redis_key)

        except Exception as e:
            self._logger.error('Error in getting the domain list for {} : {}'.format(shopper_id, e))
        finally:
            return query_value
