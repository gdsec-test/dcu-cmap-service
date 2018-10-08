import json
import re

import graphene
from flask_graphql import GraphQLView

from functions import get_tld_by_domain_name


class ShopperPortfolio:
    accountRepFirstName = graphene.String(description='Account Rep First Name')
    accountRepLastName = graphene.String(description='Account Rep Last Name')
    accountRepEmail = graphene.String(description='Account Rep Email Address')
    portfolioType = graphene.String(description='Shopper Portfolio Type')
    blacklist = graphene.Boolean(description='Shopper Blacklist Status - Do Not Suspend!')
    shopper_id = graphene.String(description='Shopper ID')


class ShopperProfile(graphene.ObjectType, ShopperPortfolio):
    # The following is a dynamic 'catch-all' method to intercept calls
    #  to any of the resolve_??? methods, instead of having to explicitly
    #  write out however many of them there need to be.  The member variables
    #  will still need to be defined in the ShopperPortfolio class.
    # http://stackoverflow.com/questions/42215848/specifically-named-dynamic-class-methods-in-python
    def __getattribute__(self, attr):
        if attr.startswith('resolve_'):
            if hasattr(self, attr[8:]):
                return lambda: getattr(self, attr[8:])
            return lambda: 'There is no value for {}'.format(attr[8:])
        return super(ShopperProfile, self).__getattribute__(attr)


class RegistrarInfo(graphene.ObjectType):
    brand = graphene.String(description='Registrar brand detected by Brand Detection')
    domain_create_date = graphene.String(description='Date domain was registered')
    domain_id = graphene.String(description='ID of domain name')
    registrar_abuse_email = graphene.List(graphene.String, description='Email contact(s)')
    registrar_name = graphene.String(description='Name of registrar or hosting provider')


class HostInfo(graphene.ObjectType):
    created_date = graphene.String(description='Created Date')
    data_center = graphene.String(description='Name of DataCenter that our server is in')
    friendly_name = graphene.String(description='Friendly Name')
    guid = graphene.String(description='GUID for hosting account')
    brand = graphene.String(description='Hosting brand detected by Brand Detection')
    hosting_abuse_email = graphene.List(graphene.String, description='Email contact(s)')
    hosting_company_name = graphene.String(description='Name of registrar or hosting provider')
    hostname = graphene.String(description='Hostname of our server')
    ip = graphene.String(description='IP address of the reported domain')
    os = graphene.String(description='OS of our server')
    product = graphene.String(description='Name of our hosting product in use')
    shopper_id = graphene.String(description='Shopper account ID')
    mwp_id = graphene.String(description='ID required for MWP 1.0 account suspension/reinstatement')
    vip = graphene.Field(ShopperProfile, description='Shoppers VIP status')


class ApiResellerService:
    parent = graphene.String(description='API Reseller Parent shopper id')
    child = graphene.String(description='API Reseller Child shopper id')


class ApiResellerInfo(graphene.ObjectType, ApiResellerService):
    pass


class DomainData(graphene.ObjectType):
    """
    Data returned in a DomainSearch
    """
    domainid = graphene.String(description='ID of domain name')
    domain = graphene.String(description='Actual domain name')


class DomainSearch(graphene.ObjectType):
    """
    Holds the results of a domain search
    """
    pattern = ''
    results = graphene.List(DomainData, description='List of results matching domain search regex')
    domainlist = []

    def resolve_results(self, info):
        regex = re.compile(self.pattern)
        return [DomainData(domainid=item[0], domain=item[1].decode('idna'))
                for item in self.domainlist if regex.match(item[1])]


class StatusInfo(graphene.Interface):
    domain = ''
    statusCode = graphene.String(description='The registrar status code for provided domain name')


# TODO: Finish endpoint once client cert is white-listed
class DomainStatusInfo(graphene.ObjectType):
    class Meta:
        interfaces = (StatusInfo,)

    def resolve_statusCode(self, info):
        return "PLACEHOLDER: domain status code"


class Shopper:
    """
    Top level Shopper Info
    """
    shopper_id = graphene.String(description='The oldest shopper_id on record')
    domain_count = graphene.Int(description='Number of domains owned by the shopper')
    domain_search = graphene.Field(DomainSearch, regex=graphene.String(required=True))
    shopper_create_date = graphene.String(description='The create data of the shopper')
    shopper_email = graphene.String(description='Email Address for Shopper')
    shopper_first_name = graphene.String(description='First Name for Shopper')
    shopper_last_name = graphene.String(description='Last Name for Shopper')
    shopper_address_1 = graphene.String(description='Address 1 for Shopper')
    shopper_address_2 = graphene.String(description='Address 2 for Shopper')
    shopper_city = graphene.String(description='City for Shopper')
    shopper_state = graphene.String(description='State for Shopper')
    shopper_postal_code = graphene.String(description='Postal Code for Shopper')
    shopper_country = graphene.String(description='Country for Shopper')
    shopper_phone_mobile = graphene.String(description='Mobile Phone Number for Shopper')
    shopper_phone_home = graphene.String(description='Home Phone Number for Shopper')
    shopper_phone_work = graphene.String(description='Work Phone Number Shopper')
    shopper_phone_work_ext = graphene.String(description='Work Phone Number Ext for Shopper')
    vip = graphene.Field(ShopperProfile, description='Shoppers VIP status')

    def resolve_domain_count(self, info):
        client = info.context.get('regdb')
        return client.get_domain_count_by_shopper_id(self.shopper_id)

    def resolve_domainsearch(self, info, regex):
        client = info.context.get('regdb')
        data = client.get_domain_list_by_shopper_id(self.shopper_id)
        ds = DomainSearch()
        ds.domainlist = data
        ds.pattern = regex
        return ds

    def resolve_vip(self, info):
        # These default initializations are put in place to allow for upgrade to Graphql 2.0. A bug currently exists
        # that defaults all uninitialized fields as a `graphene.String object at X memory location` rather than null
        # in Graphql 1.4.1. This fixes that bug until it is addressed. 8 Nov 2017 @nlemay.
        query_dict = dict(blacklist=False, accountRepFirstName=None, accountRepLastName=None, accountRepEmail=None,
                          portfolioType=None, shopper_id=None)
        query_dict.update(info.context.get('crm').get_shopper_portfolio_information(self.shopper_id))
        # Query the blacklist, whose entities never get suspended
        query_dict['blacklist'] = info.context.get('vip').query_entity(self.shopper_id)
        return ShopperProfile(**query_dict)


class ShopperQuery(graphene.ObjectType, Shopper):
    pass


class ShopperByDomain(graphene.ObjectType, Shopper):
    """
    Holds Shopper data when only the domain is known
    """
    pass


class DomainQuery(graphene.ObjectType):
    alexa_rank = graphene.Int(description='Alexa World Wide Rank for domain')
    api_reseller = graphene.Field(ApiResellerInfo, description='API Reseller Information for Provided Domain Name')
    blacklist = graphene.Boolean(description='Domain Name Blacklist Status - Do Not Suspend!')
    domain = graphene.String(description='Domain Name from DomainQuery')
    domain_status = graphene.Field(DomainStatusInfo, description='Registrar Domain Status for Provided Domain Name')
    host = graphene.Field(HostInfo, description='Hosting Information for Provided Domain Name')
    registrar = graphene.Field(RegistrarInfo, description='Registrar Information for Provided Domain Name')
    shopper_info = graphene.Field(ShopperByDomain, description='Shopper Information for Provided Domain Name')

    def resolve_host(self, info):
        # These default initializations are put in place to allow for upgrade to Graphql 2.0. A bug currently exists
        # that defaults all uninitialized fields as a `graphene.String object at X memory location` rather than null
        # in Graphql 1.4.1. This fixes that bug until it is addressed. 8 Nov 2017 @nlemay.
        vip = dict(blacklist=False, accountRepFirstName=None, accountRepLastName=None, accountRepEmail=None,
                   portfolioType=None, shopper_id=None)
        whois = dict(data_center=None, os=None, product=None, guid=None, shopper_id=None, hostname=None, ip=None,
                     mwp_id=None, hosting_company_name=None, brand=None, hosting_abuse_email=None, created_date=None,
                     friendly_name=None)

        whois.update(info.context.get('bd').get_hosting_info(self.domain))
        if whois['hosting_company_name'] == 'GoDaddy.com LLC':
            host_info = info.context.get('ipam').get_properties_for_ip(self.domain)
            if type(host_info) is dict:
                whois['data_center'] = host_info.get('data_center', None)
                whois['created_date'] = host_info.get('created_date', None)
                whois['friendly_name'] = host_info.get('friendly_name', None)
                whois['os'] = host_info.get('os', None)
                whois['product'] = host_info.get('product', None)
                whois['guid'] = host_info.get('guid', None)
                whois['shopper_id'] = host_info.get('shopper_id', None)
                whois['hostname'] = host_info.get('hostname', None)
                whois['ip'] = host_info.get('ip', None)
                whois['mwp_id'] = host_info.get('accountid', None)

        if whois.get('shopper_id', None) is not None:
            vip.update(info.context.get('crm').get_shopper_portfolio_information(whois.get('shopper_id')))
            # Query the blacklist, whose entities never get suspended
            vip['blacklist'] = info.context.get('vip').query_entity(whois.get('shopper_id'))

        host_obj = HostInfo(**whois)
        host_obj.vip = ShopperProfile(**vip)
        return host_obj

    def resolve_registrar(self, info):
        # If we were given a domain with a subdomain, request registrar information for just the domain.tld
        domain = get_tld_by_domain_name(self.domain)
        whois = info.context.get('bd').get_registrar_info(domain)
        return RegistrarInfo(**whois)

    def resolve_api_reseller(self, info):
        parent_child = info.context.get('regdb').get_parent_child_shopper_by_domain_name(self.domain)
        return ApiResellerInfo(**parent_child)

    def resolve_shopper_info(self, info):
        client = info.context.get('regdb')
        active_shopper = client.get_shopper_id_by_domain_name(self.domain)
        shopper_client = info.context.get('shopper')
        extra_data = shopper_client.get_shopper_by_shopper_id(active_shopper, ['shopper_create_date',
                                                                               'shopper_first_name',
                                                                               'shopper_email',
                                                                               'shopper_last_name',
                                                                               'shopper_phone_work',
                                                                               'shopper_phone_work_ext',
                                                                               'shopper_phone_home',
                                                                               'shopper_phone_mobile',
                                                                               'shopper_address_1',
                                                                               'shopper_address_2',
                                                                               'shopper_city',
                                                                               'shopper_state',
                                                                               'shopper_postal_code',
                                                                               'shopper_country'])
        return ShopperByDomain(shopper_id=active_shopper, **extra_data)

    def resolve_blacklist(self, info):
        return info.context.get('vip').query_entity(self.domain)

    def resolve_alexa_rank(self, info):
        return info.context.get('alexa').urlinfo(self.domain)

    def resolve_domain_status(self, info):
        domain = DomainStatusInfo()
        domain.domain = self.domain
        return domain


class Query(graphene.ObjectType):
    domain_query = graphene.Field(DomainQuery,
                                  domain=graphene.String(required=True),
                                  description='Top level query based on domain names')
    shopper_query = graphene.Field(ShopperQuery,
                                   id=graphene.String(required=True),
                                   description='Top level query based on shopper id')

    def resolve_domain_query(self, info, domain):
        if domain is None or len(domain) < 4:
            raise ValueError("Invalid domain string provided")
        if info.context.get('whois').is_ip(domain):
            domain = info.context.get('whois').get_domain_from_ip(domain)
        return DomainQuery(domain=domain)

    def resolve_shopper_query(self, info, id):
        if id is None or len(id) < 1:
            raise ValueError("Invalid shopper id string provided")
        extra_data = info.context.get('shopper').get_shopper_by_shopper_id(id, ['shopper_create_date',
                                                                                'shopper_first_name',
                                                                                'shopper_email'])
        return ShopperQuery(shopper_id=id, **extra_data)


class GraphQLViewWithCaching(GraphQLView):
    REDIS_KEY = 'result'
    STATUS_KEY = 'status_code'

    # Subclassing GraphQLView in order to intercept the incoming query, so that it
    #  may be compared to a Redis cache for quick response (if cached entry exists).
    #  If the query is not yet cached, then cache it along with the result/status_code
    #  after the call to superclass get_response() has returned

    def get_response(self, request, data, show_graphiql=False):
        redis = self.context.get('redis')
        redis_key = request.data
        query_value = redis.get_value(redis_key)
        if query_value is None:
            result, status_code = super(GraphQLViewWithCaching, self).get_response(request, data, show_graphiql)
            redis.set_value(redis_key, json.dumps({self.REDIS_KEY: result, self.STATUS_KEY: status_code}))
        else:
            query_dict = json.loads(query_value)
            result = query_dict.get(self.REDIS_KEY)
            status_code = query_dict.get(self.STATUS_KEY)
        return result, status_code
