import json
import xml.etree.ElementTree as ET

from csetutils.flask.logging import get_logging

from service.connectors.shopper import ShopperAPI
from service.soap.request_transport import RequestsTransport
from service.utils.functions import get_fld_by_domain_name


class RegDbAPI(object):
    '''
    Provides an interface for interacting with RegDB which provides information about domains that are registered
    with GoDaddy. Functions include getting domain counts, determining API Reseller, finding shoppers associated with
    a given domain name, etc.
    '''
    _redis_key = 'result'

    def __init__(self, settings, redis_obj):
        self._location = settings.DB_WEB_SVC_URL
        self._wsdl = self._location + '?Handler=GenRegDBWebSvcWSDL'
        self._logger = get_logging()
        self._redis = redis_obj
        self._shopper_api = ShopperAPI(settings)
        from suds.client import Client
        try:
            self._client = Client(self._wsdl, location=self._location,
                                  headers=RequestsTransport.get_soap_headers(),
                                  transport=RequestsTransport())
        except Exception as e:
            self._logger.error('Failed REG DB Client Init: {}'.format(e))

    def get_domain_count_by_shopper_id(self, shopper_id):
        '''
        Given a ShopperID, determine how many domains are registered within that shopper.
        :param shopper_id:
        :return:
        '''
        self._logger.info('Retrieving domain count from RegDB for shopper {}'.format(shopper_id))
        redis_key = '{}-domain_count'.format(shopper_id)
        query_value = None

        if not shopper_id:
            return query_value

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
        Given a domain name, attempt to retrieve the Parent shopper and customer IDs and the Child shopper and customer
        IDs for a domain that is registered as part of an API Reseller e.g. Wild West Domains, Google, etc.
        :param domain_name_as_provided:
        :return:
        '''
        self._logger.info('Retrieving parent child info from RegDB for {}'.format(domain_name_as_provided))

        # In the event that we were provided a sub-domain name as opposed to a tld
        domain_name = get_fld_by_domain_name(domain_name_as_provided)
        # Check redis cache for parent/child api reseller info
        redis_key = '{}-reseller_parent_child'.format(domain_name)

        query_value = dict(parent=None, child=None)

        if not domain_name:
            return query_value

        try:
            query_value = self._redis.get(redis_key)
            if query_value is None:
                domain_name = domain_name.encode('idna').decode()
                doc = ET.fromstring(self._client.service.GetParentChildShopperByDomainName(domain_name))

                if doc.find('RECORDSET') is None or doc.find('RECORDSET').find('RECORD') is None:
                    query_value = dict(parent=None, child=None)
                else:
                    doc_record = doc.find('RECORDSET').find('RECORD')
                    parent_shopper_id = doc_record.find('PARENT_SHOPPER_ID').text
                    child_shopper_id = doc_record.find('CHILD_SHOPPER_ID').text

                    parent_info = self._shopper_api.get_shopper_by_shopper_id(parent_shopper_id, ['customerId'])
                    parent_customer_id = parent_info.get('customer_id')

                    child_info = self._shopper_api.get_shopper_by_shopper_id(child_shopper_id, ['customerId'])
                    child_customer_id = child_info.get('customer_id')

                    query_value = dict(parent=parent_shopper_id,
                                       child=child_shopper_id,
                                       parent_customer_id=parent_customer_id,
                                       child_customer_id=child_customer_id)

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
        self._logger.info('Retrieving shopper id from RegDB for {}'.format(domain_name_as_provided))

        # In the event that we were provided a sub-domain name as opposed to a tld
        domain_name = get_fld_by_domain_name(domain_name_as_provided)
        redis_key = '{}-shopper_id_by_domain'.format(domain_name)
        query_value = None

        if not domain_name:
            return query_value

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

        if not shopper_id:
            return query_value

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
