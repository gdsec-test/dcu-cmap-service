import re
import json
import graphene

from flask_graphql import GraphQLView


class DomainService(graphene.AbstractType):
    name = graphene.String(description='Name of registrar or hosting provider')
    email = graphene.List(graphene.String, description='Email contact(s)')


class RegistrarInfo(graphene.ObjectType, DomainService):
    create_date = graphene.String(description='Date domain was registered')


class HostInfo(graphene.ObjectType, DomainService):
    ip = graphene.String(description='IP address of the reported domain')
    env = graphene.String(description='Domain/IP GoDaddy hosting environment')
    hostname = graphene.String(description='Hostname of our server')
    os = graphene.String(description='OS of our server')
    guid = graphene.String(description='GUID for hosting account')
    dc = graphene.String(description='Name of DC that our server is in')
    product = graphene.String(description='Name of our hosting product in use')


class ApiResellerService(graphene.AbstractType):
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

    def resolve_results(self, args, context, info):
        regex = re.compile(self.pattern)
        return [DomainData(domainid=item[0], domain=item[1].decode('idna')) for item in self.domainlist if regex.match(item[1])]


class StatusInfo(graphene.Interface):
    domain = ''
    statusCode = graphene.String(description='The registrar status code for provided domain name')


class ShopperPortfolio(graphene.AbstractType):
    PhoneExt = graphene.String(description='Account Rep Phone Extension')
    FirstName = graphene.String(description='Account Rep First Name')
    LastName = graphene.String(description='Account Rep Last Name')
    accountRep = graphene.String(description='Account Rep Full Name')
    Email = graphene.String(description='Account Rep Email Address')
    PortfolioTypeID = graphene.String(description='Account Rep Portfolio Type ID')
    InternalPhoneQueue = graphene.String(description='Account Rep Internal Phone Queue')
    InternalImageURL = graphene.String(description='Image URL for Shopper Portfolio Type')
    PortfolioType = graphene.String(description='Shopper Portfolio Type')
    blacklist = graphene.Boolean(description='Shopper Blacklist Status - Do Not Suspend!')
    shopper_id = graphene.String(description='Shopper ID')


#TODO: Finish endpoint once client cert is white-listed
class DomainStatusInfo(graphene.ObjectType):
    class Meta:
        interfaces = (StatusInfo,)

    def resolve_statusCode(self, args, context, info):
        return "PLACEHOLDER: domain status code"


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

    def resolve_accountRep(self, args, context, info):
        # In case the 'self' class properties are not present, substitute with empty strings
        first_name = self.__dict__.get('FirstName') if self.__dict__.get('FirstName') is not None else ''
        last_name = self.__dict__.get('LastName') if self.__dict__.get('LastName') is not None else ''
        email = self.__dict__.get('Email') if self.__dict__.get('Email') is not None else ''
        if '' == first_name + last_name + email:
            return None
        return '{} {} ({})'.format(first_name, last_name, email)


class Shopper(graphene.AbstractType):
    """
    Top level Shopper Info
    """
    shopper_id = graphene.String(description='The oldest shopper_id on record')
    date_created = graphene.String(description='The create data of the shopper')
    domain_count = graphene.Int(description='Number of domains owned by the shopper')
    vip = graphene.Field(ShopperProfile, description='Shoppers VIP status')
    # TODO: I dont think "child" does anything...
    child = graphene.String(description='Child account owned by the shopper')
    domainsearch = graphene.Field(DomainSearch, regex=graphene.String(required=True))
    first_name = graphene.String(description='First Name for Shopper')
    email = graphene.String(description='Email Address for Shopper')

    def resolve_domain_count(self, args, context, info):
        client = context.get('regdb')
        return client.get_domain_count_by_shopper_id(self.shopper_id)

    def resolve_domainsearch(self, args, context, info):
        regex = args.get('regex')
        client = context.get('regdb')
        data = client.get_domain_list_by_shopper_id(self.shopper_id)
        ds = DomainSearch()
        ds.domainlist = data
        ds.pattern = regex
        return ds

    def resolve_vip(self, args, context, info):
        query_dict = context.get('crm').get_shopper_portfolio_information(self.shopper_id)
        # Query the blacklist, whose entities never get suspended
        query_dict['blacklist'] = context.get('vip').query_entity(self.shopper_id)
        return ShopperProfile(**query_dict)


class ShopperQuery(graphene.ObjectType, Shopper):
    pass


class ShopperByDomain(graphene.ObjectType, Shopper):
    """
    Holds Shopper data when only the domain is known
    """
    pass


class DomainQuery(graphene.ObjectType):
    host = graphene.Field(HostInfo, description='Hosting Information for Provided Domain Name')
    registrar = graphene.Field(RegistrarInfo, description='Registrar Information for Provided Domain Name')
    api_reseller = graphene.Field(ApiResellerInfo, description='API Reseller Information for Provided Domain Name')
    shopper_info = graphene.Field(ShopperByDomain, description='Shopper Information for Provided Domain Name')
    domain_status = graphene.Field(DomainStatusInfo, description='Registrar Domain Status for Provided Domain Name')
    domain = graphene.String(description='Domain Name from DomainQuery')
    blacklist = graphene.Boolean(description='Domain Name Blacklist Status - Do Not Suspend!')

    def resolve_host(self, args, context, info):
        whois = context.get('whois').get_hosting_info(self.domain)
        if whois['name'] == 'GoDaddy.com LLC':
            environment = context.get('shotgun').setrun(self.domain)
            whois['dc'] = environment[0]
            whois['os'] = environment[1]
            whois['product'] = environment[2]
            whois['guid'] = environment[3]

        return HostInfo(**whois)

    def resolve_registrar(self, args, context, info):
        whois = context.get('whois').get_registrar_info(self.domain)
        return RegistrarInfo(**whois)

    def resolve_api_reseller(self, args, context, info):
        parent_child = context.get('regdb').get_parent_child_shopper_by_domain_name(self.domain)
        return ApiResellerInfo(**parent_child)

    def resolve_shopper_info(self, args, context, info):
        client = context.get('regdb')
        active_shopper = client.get_shopper_id_by_domain_name(self.domain)
        shopper_client = context.get('shopper')
        extra_data = shopper_client.get_shopper_by_shopper_id(active_shopper, ['date_created',
                                                                               'first_name',
                                                                               'email'])
        return ShopperByDomain(shopper_id=active_shopper, **extra_data)

    def resolve_blacklist(self, args, context, info):
        vip = context.get('vip').query_entity(self.domain)
        return vip

    def resolve_domain_status(self, args, context, info):
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

    def resolve_domain_query(self, args, context, info):
        domain = args.get('domain')
        if context.get('whois').is_ip(domain):
            domain = context.get('whois').get_domain_from_ip(domain)
        return DomainQuery(domain=domain)

    def resolve_shopper_query(self, args, context, info):
        shopper = args.get('id')
        extra_data = context.get('shopper').get_shopper_by_shopper_id(shopper, ['date_created',
                                                                                'first_name',
                                                                                'email'])
        return ShopperQuery(shopper_id=args.get('id'), **extra_data)


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
