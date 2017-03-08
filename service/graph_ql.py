import re
import json
import socket
import graphene

import logging
import logging.config

from whois import whois
from ipwhois import IPWhois
from flask_graphql import GraphQLView


class DomainService(graphene.AbstractType):
    name = graphene.String()
    email = graphene.List(graphene.String, description='Email contact(s) for registrar')


class Registrar(graphene.ObjectType, DomainService):
    """
   Registration info for Shopper domain
   """
    pass


class Host(graphene.ObjectType, DomainService):
    """
    Hosting infor for Shopper domain
    """
    pass


class DomainData(graphene.ObjectType):
    """
    Data returned in a DomainSearch
    """
    domainid = graphene.String()
    domain = graphene.String()


class DomainSearch(graphene.ObjectType):
    """
    Holds the results of a domain search
    """
    results = graphene.List(DomainData)
    domainlist = []
    pattern = ''

    def resolve_results(self, args, context, info):
        regex = re.compile(self.pattern)
        return [DomainData(domainid=item[0], domain=item[1]) for item in self.domainlist if regex.match(item[1])]


class DomainName(graphene.Interface):
    name = graphene.String()
    message = graphene.String()
    parentChild = graphene.String()
    domain = ''
    abuseContact = graphene.String()


class StatusInfo(graphene.Interface):
    statusCode = graphene.String()
    domain = ''


class DomainCreateDate(graphene.Interface):
    creationDate = graphene.String()
    domain = ''


class ShopperCreateDate(graphene.Interface):
    creationDate = graphene.String()
    id = ''


class ShopperPortfolio(graphene.Interface):
    PhoneExt = graphene.String()
    FirstName = graphene.String()
    LastName = graphene.String()
    Email = graphene.String()
    PortfolioTypeID = graphene.String()
    InternalPhoneQueue = graphene.String()
    InternalImageURL = graphene.String()
    PortfolioType = graphene.String()
    Vip = graphene.String()
    shopper_id = graphene.String()
    accountRep = graphene.String()


class DomainPortfolio(graphene.Interface):
    Vip = graphene.String()


class ShopperId(graphene.Interface):
    domaincount = graphene.String()


class HostInfo(graphene.ObjectType):
    class Meta:
        interfaces = (DomainName,)

    def resolve_name(self, args, context, info):
        # Check redis cache for self.domain key
        redis_key = '{}-hosted'.format(self.domain)
        query_value = context.get('redis').get_value(redis_key)
        if query_value is None:
            try:
                ip = socket.gethostbyname(self.domain)
                ip_lookup = socket.gethostbyaddr(ip)
                server_name = ip_lookup[0]
                # split up server name and find domain before TLD
                server_name_array = server_name.split(".")
                query_value = server_name_array[len(server_name_array) - 2]
                context.get('redis').set_value(redis_key, query_value)
            except Exception as e:
                logging.warning("Error in reverse DNS lookup %s : %s, attempting whois lookup..", ip, e.message)
                regex = re.compile('[^a-zA-Z]')
                query_value = regex.sub('', IPWhois(ip).lookup_rdap().get('network',[]).get('name', ''))
                context.get('redis').set_value(redis_key, query_value)
        return query_value.upper()

    def resolve_abuseContact(self, args, context, info):
        redis_key = '{}-host_abuse_contact'.format(self.domain)
        query_value = context.get('redis').get_value(redis_key)
        host_abuse = context.get('host_whois').get_abuse_email(self.domain)
        return host_abuse


class RegistrarInfo(graphene.ObjectType):
    class Meta:
        interfaces = (DomainName,)

    def resolve_name(self, args, context, info):
        # Check redis cache for self.domain key
        redis_key = '{}-registrar'.format(self.domain)
        query_value = context.get('redis').get_value(redis_key)
        if query_value is None:
            w = whois(self.domain)
            query_value = w.registrar
            context.get('redis').set_value(redis_key, query_value)
        return query_value

    def resolve_abuseContact(self, args, context, info):
        redis_key = '{}-registrar_abuse_contact'.format(self.domain)
        query_value = context.get('redis').get_value(redis_key)
        reg_abuse = context.get('whois').get_registrar_abuse(self.domain)
        return reg_abuse


class ResellerInfo(graphene.ObjectType):
    class Meta:
        interfaces = (DomainName,)

    def resolve_parentChild(self, args, context, info):
        # Check redis cache for self.domain key
        redis_key = '{}-reseller'.format(self.domain)
        query_value = context.get('redis').get_value(redis_key)
        if query_value is None:
            api = context.get('regdb')
            retval = api.get_parent_child_shopper_by_domain_name(self.domain)
            if retval[0] is False:
                query_value =  "No Parent/Child Info Found"
            else:
                query_value = 'Parent:{}, Child:{}'.format(retval[0], retval[1])
            context.get('redis').set_value(redis_key, query_value)
        return query_value


# DomainStatusInfo type is an implementation of the StatusInfo interface
class DomainStatusInfo(graphene.ObjectType):
    class Meta:
        interfaces = (StatusInfo,)

    def resolve_statusCode(self, args, context, info):
        # Check redis cache for self.domain key
        redis_key = '{}-domain_status'.format(self.domain)
        query_value = context.get('redis').get_value(redis_key)
        # if query_value is None:
        #     try:
        #         ip = socket.gethostbyname(self.domain)
        #         ip_lookup = socket.gethostbyaddr(ip)
        #         server_name = ip_lookup[0]
        #         # split up server name and find domain before TLD
        #         server_name_array = server_name.split(".")
        #         query_value = server_name_array[len(server_name_array) - 2]
        #         context.get('redis').set_value(redis_key, query_value)
        #     except Exception as e:
        #         logging.warning("Error in reverse DNS lookup %s : %s, attempting whois lookup..", ip, e.message)
        #         regex = re.compile('[^a-zA-Z]')
        #         query_value = regex.sub('', IPWhois(ip).lookup_rdap().get('network',[]).get('name', ''))
        #         context.get('redis').set_value(redis_key, query_value)
        return "domain"


class DomainCreationInfo(graphene.ObjectType):
    class Meta:
        interfaces = (DomainCreateDate,)

    def resolve_creationDate(self, args, context, info):
        # Check redis cache for self.domain key
        redis_key = '{}-domain_creation_date'.format(self.domain)
        query_value = context.get('redis').get_value(redis_key)
        # if query_value is None:
        #     try:
        #         ip = socket.gethostbyname(self.domain)
        #         ip_lookup = socket.gethostbyaddr(ip)
        #         server_name = ip_lookup[0]
        #         # split up server name and find domain before TLD
        #         server_name_array = server_name.split(".")
        #         query_value = server_name_array[len(server_name_array) - 2]
        #         context.get('redis').set_value(redis_key, query_value)
        #     except Exception as e:
        #         logging.warning("Error in reverse DNS lookup %s : %s, attempting whois lookup..", ip, e.message)
        #         regex = re.compile('[^a-zA-Z]')
        #         query_value = regex.sub('', IPWhois(ip).lookup_rdap().get('network',[]).get('name', ''))
        #         context.get('redis').set_value(redis_key, query_value)
        return "domain creation date"


class ShopperCreateDateInfo(graphene.ObjectType):
    class Meta:
        interfaces = (ShopperCreateDate,)

    def resolve_creationDate(self, args, context, info):
        # Check redis cache for self.domain key
        redis_key = '{}-shopper_creation_date'.format(self.id)
        query_value = context.get('redis').get_value(redis_key)
        if query_value is None:
            shopper_client = context.get('shopper')
            shopper_create_date = shopper_client.get_shopper_by_shopper_id(self.id, ['date_created'])
            query_value = shopper_create_date
            context.get('redis').set_value(redis_key, query_value)
            # except Exception as e:
            #     logging.warning("Error in getting the shopper creation date for %s : %s", self.domain, e.message)
            #     regex = re.compile('[^a-zA-Z]')
            #     query_value = regex.sub('', IPWhois(ip).lookup_rdap().get('network',[]).get('name', ''))
            #     context.get('redis').set_value(redis_key, query_value)
        return query_value


class ShopperProfile(graphene.ObjectType):
    class Meta:
        interfaces = (ShopperPortfolio,)

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
        return '{} {} ({})'.format(self.FirstName, self.LastName, self.Email)


class DomainProfile(graphene.ObjectType):
    class Meta:
        interfaces = (DomainPortfolio,)

    # The following is a dynamic 'catch-all' method to intercept calls
    #  to any of the resolve_??? methods, instead of having to explicitly
    #  write out however many of them there need to be.  The member variables
    #  will still need to be defined in the DomainPortfolio class.
    # http://stackoverflow.com/questions/42215848/specifically-named-dynamic-class-methods-in-python
    def __getattribute__(self, attr):
        if attr.startswith('resolve_'):
            if hasattr(self, attr[8:]):
                return lambda: getattr(self, attr[8:])
            return lambda: 'There is no value for {}'.format(attr[8:])
        return super(DomainProfile, self).__getattribute__(attr)


class ShopperInfo(graphene.ObjectType):
    class Meta:
        interfaces = (ShopperId,)

    def resolve_domaincount(self, args, context, info):
        # Check redis cache for self.id key
        redis_key = '{}-domaincount'.format(self.id)
        query_value = context.get('redis').get_value(redis_key)
        if query_value is None:
            api = context.get('regdb')
            query_value = api.get_domain_count_by_shopper_id(self.id)
            context.get('redis').set_value(redis_key, query_value)
        return query_value


class ShopperQuery(graphene.ObjectType):
    shopperid = graphene.Field(ShopperInfo)
    profile = graphene.Field(ShopperProfile)
    id = graphene.String()
    shopper_create_date = graphene.Field(ShopperCreateDateInfo)

    def resolve_shopperid(self, args, context, info):
        shopper = ShopperInfo()
        shopper.id = self.id
        return shopper

    def resolve_profile(self, args, context, info):
        # Check redis cache for self.id key
        redis_key = self.id
        query_value = context.get('redis').get_value(redis_key)
        if query_value is None:
            api = context.get('crm')
            query_dict = api.get_shopper_portfolio_information(self.id)
            # Query the blacklist, whose entities never get suspended
            db = context.get('vip')
            vip = db.query_entity(self.id)
            query_dict['Vip'] = vip
            context.get('redis').set_value(redis_key, json.dumps({"result": query_dict}))
        else:
            query_dict = json.loads(query_value).get("result")
        return ShopperProfile(**query_dict)

    def resolve_shopper_create_date(self, args, context, info):
        shopper = ShopperCreateDateInfo()
        shopper.id = self.id
        return shopper


class Shopper(graphene.AbstractType):
    """
    Top level Shopper Info
    """
    shopper_id = graphene.String(description='The oldest shopper_id on record')
    date_created = graphene.String(description='The create data of the shopper')
    child = graphene.String(description='Child account owned by the shopper')
    domain_count = graphene.Int(description='Number of domains owned by the shopper')
    domainsearch = graphene.Field(DomainSearch, regex=graphene.String(required=True))
    first_name = graphene.String()
    email = graphene.String()

    def resolve_domainsearch(self, args, context, info):
        regex = args.get('regex')
        client = context.get('regdb')
        data = client.get_domain_list_by_shopper_id(self.shopper_id)
        ds = DomainSearch()
        ds.domainlist = data
        ds.pattern = regex
        return ds

    def resolve_domain_count(self, args, context, info):
        client = context.get('regdb')
        return client.get_domain_count_by_shopper_id(self.shopper_id)


class ShopperById(graphene.ObjectType, Shopper):
    """
    Holds Shopper data when only the shopper_id is known
    """
    pass


class ShopperByDomain(graphene.ObjectType, Shopper):
    """
    Holds Shopper data when only the domain is known
    """
    domain = graphene.String()
    othershopperlist = graphene.List(ShopperById, description='Other shopper_ids associated with this domain')


class DomainQuery(graphene.ObjectType):
    host = graphene.Field(HostInfo)
    registrar = graphene.Field(RegistrarInfo)
    reseller = graphene.Field(ResellerInfo)
    shopper_by_domain = graphene.Field(ShopperByDomain)
    domain_status = graphene.Field(DomainStatusInfo)
    domain_create = graphene.Field(DomainCreationInfo)
    domain = graphene.String()
    profile = graphene.Field(DomainProfile)

    def resolve_host(self, args, context, info):
        domain = HostInfo()
        domain.domain = self.domain
        return domain

    def resolve_registrar(self, args, context, info):
        domain = RegistrarInfo()
        domain.domain = self.domain
        return domain

    def resolve_reseller(self, args, context, info):
        domain = ResellerInfo()
        domain.domain = self.domain
        return domain


    def resolve_shopper_by_domain(self, args, context, info):
        client = context.get('regdb')
        active_shopper = client.get_shopper_id_by_domain_name(self.domain)
        shopper_client = context.get('shopper')
        extra_data = shopper_client.get_shopper_by_shopper_id(active_shopper, ['date_created', 'first_name', 'email'])
        othershoppers = shopper_client.get_shopper_by_domain_name(self.domain, ['shopper_id', 'date_created', 'first_name', 'email'])
        lst = [ShopperById(**item) for item in othershoppers if item['shopper_id'] != active_shopper]
        return ShopperByDomain(domain=self.domain, shopper_id=active_shopper, othershopperlist=lst, **extra_data)

    def resolve_profile(self, args, context, info):
        # Check redis cache for self.id key
        redis_key = self.domain
        query_value = context.get('redis').get_value(redis_key)
        if query_value is None:
            # Query the blacklist, whose entities never get suspended
            db = context.get('vip')
            vip = db.query_entity(self.domain)
            query_dict = {}
            query_dict['Vip'] = vip
            context.get('redis').set_value(redis_key, json.dumps({"result": query_dict}))
        else:
            query_dict = json.loads(query_value).get("result")
        return DomainProfile(**query_dict)

    def resolve_domain_status(self, args, context, info):
        domain = DomainStatusInfo()
        domain.domain = self.domain
        return domain

    def resolve_domain_create(self, args, context, info):
        domain = DomainCreationInfo()
        domain.domain = self.domain
        return domain


class Query(graphene.ObjectType):
    domain_query = graphene.Field(DomainQuery, domain=graphene.String(required=True))
    shopper_query = graphene.Field(ShopperQuery, id=graphene.String(required=True))

    def resolve_domain_query(self, args, context, info):
        return DomainQuery(domain=args.get('domain'))

    def resolve_shopper_query(self, args, context, info):
        return ShopperQuery(id=args.get('id'))


class GraphQLViewWithCaching(GraphQLView):
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
            redis.set_value(redis_key, json.dumps({"result": result, "status_code": status_code}))
        else:
            query_dict = json.loads(query_value)
            result = query_dict.get("result")
            status_code = query_dict.get("status_code")
        return result, status_code
