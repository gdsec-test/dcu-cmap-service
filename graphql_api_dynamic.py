import os
import re
import json
import yaml
import socket
import graphene

import logging
import logging.config

import xml.etree.ElementTree as ET

from flask import Flask
from redis import Redis
from whois import whois
from ipwhois import IPWhois
from pymongo import MongoClient
from flask_graphql import GraphQLView


class CrmClientApi(object):
    _WSDL = 'https://crmclient-api.prod.phx3.int.godaddy.com/Shopper.svc?singleWsdl'
    _FACTORY = '{http://schemas.datacontract.org/2004/07/GoDaddy.CRM.ClientAPI.DataContracts}ShopperPortfolioInformationRequest'

    def __init__(self):
        from suds.client import Client
        self._client = Client(self._WSDL)
        self._request = self._client.factory.create(self._FACTORY)

    def get_shopper_portfolio_information(self, shopper_id):
        self._request.shopperID = shopper_id
        resp = self._client.service.GetShopperPortfolioInformation(self._request)
        match = re.search('<data count=.(\d+).>', resp.ResultXml)
        if match.group(1) == '0':
            return "No Premium Services For This Shopper"
        doc = ET.fromstring(resp.ResultXml)
        self._elem = doc.find(".//*[@PortfolioType]").attrib
        return self._elem


class RegDbAPI(object):
    _WSDL = 'https://dsweb.prod.phx3.gdg/RegDBWebSvc/RegDBWebSvc.dll?Handler=GenRegDBWebSvcWSDL'

    def __init__(self):
        from suds.client import Client
        self._client = Client(self._WSDL)

    def get_domain_count_by_shopper_id(self, shopper_id):
        xml_query = '<request><shopper shopperid="{}"/></request>'.format(shopper_id)
        xml_response = self._client.service.GetDomainCountByShopperID(xml_query)
        match = re.search('domaincount="(\d+)"', xml_response)
        return match.group(1)

    def get_parent_child_shopper_by_domain_name(self, domain_name):
        xml_response = self._client.service.GetParentChildShopperByDomainName(domain_name)
        match = re.search('<PARENT_SHOPPER_ID>(\d+)</PARENT_SHOPPER_ID><CHILD_SHOPPER_ID>(\d+)</CHILD_SHOPPER_ID>', xml_response)
        if match is None:
            return False, False
        return match.group(1), match.group(2)


class VipClients(object):

    def __init__(self, db_host='localhost', db_port=27017, db='local', table='vip_user'):
        client = MongoClient(db_host, db_port)
        db = client.db
        self.collection = db.table

    def query_shopper(self, shopper_id):
        db_key = '_id'
        result = self.collection.find({db_key: str(shopper_id)})
        # If the shopper id exists, they are VIP
        vip_status = True
        if result is None:
            vip_status = False
        return vip_status


class DomainName(graphene.Interface):
    name = graphene.String()
    message = graphene.String()
    parentChild = graphene.String()
    domain = ''


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


class ShopperId(graphene.Interface):
    domaincount = graphene.String()


class HostInfo(graphene.ObjectType):
    class Meta:
        interfaces = (DomainName,)

    def resolve_name(self, args, context, info):
        # Check redis cache for self.domain key
        redis_key = '{}-hosted'.format(self.domain)
        query_value = app.redis.get_value(redis_key)
        if query_value is None:
            try:
                ip = socket.gethostbyname(self.domain)
                ip_lookup = socket.gethostbyaddr(ip)
                server_name = ip_lookup[0]
                # split up server name and find domain before TLD
                server_name_array = server_name.split(".")
                query_value = server_name_array[len(server_name_array) - 2]
                app.redis.set_value(redis_key, query_value)
            except Exception as e:
                logging.warning("Error in reverse DNS lookup %s : %s, attempting whois lookup..", ip, e.message)
                regex = re.compile('[^a-zA-Z]')
                query_value = regex.sub('', IPWhois(ip).lookup_rdap().get('network',[]).get('name', ''))
                app.redis.set_value(redis_key, query_value)
        return query_value.upper()


class RegistrarInfo(graphene.ObjectType):
    class Meta:
        interfaces = (DomainName,)

    def resolve_name(self, args, context, info):
        # Check redis cache for self.domain key
        redis_key = '{}-registrar'.format(self.domain)
        query_value = app.redis.get_value(redis_key)
        if query_value is None:
            w = whois(self.domain)
            query_value = w.registrar
            app.redis.set_value(redis_key, query_value)
        return query_value


class ResellerInfo(graphene.ObjectType):
    class Meta:
        interfaces = (DomainName,)

    def resolve_parentChild(self, args, context, info):
        # Check redis cache for self.domain key
        redis_key = '{}-reseller'.format(self.domain)
        query_value = app.redis.get_value(redis_key)
        if query_value is None:
            api = context.get('regdb')
            retval = api.get_parent_child_shopper_by_domain_name(self.domain)
            if retval[0] is False:
                query_value =  "No Parent/Child Info Found"
            else:
                query_value = 'Parent:{}, Child:{}'.format(retval[0], retval[1])
            app.redis.set_value(redis_key, query_value)
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


class ShopperInfo(graphene.ObjectType):
    class Meta:
        interfaces = (ShopperId,)

    def resolve_domaincount(self, args, context, info):
        # Check redis cache for self.id key
        redis_key = '{}-domaincount'.format(self.id)
        query_value = app.redis.get_value(redis_key)
        if query_value is None:
            api = context.get('regdb')
            query_value = api.get_domain_count_by_shopper_id(self.id)
            app.redis.set_value(redis_key, query_value)
        return query_value


class ShopperQuery(graphene.ObjectType):
    shopperid = graphene.Field(ShopperInfo)
    profile = graphene.Field(ShopperProfile)
    id = graphene.String()

    def resolve_shopperid(self, args, context, info):
        shopper = ShopperInfo()
        shopper.id = self.id
        return shopper

    def resolve_profile(self, args, context, info):
        # Check redis cache for self.id key
        redis_key = self.id
        query_value = app.redis.get_value(redis_key)
        if query_value is None:
            api = context.get('crm')
            query_dict = api.get_shopper_portfolio_information(self.id)
            # Query the VIP USERS table, whose shoppers never get suspended
            db = context.get('vip')
            vip = db.query_shopper(self.id)
            query_dict['Vip'] = vip
            app.redis.set_value(redis_key, json.dumps({"result": query_dict}))
        else:
            query_dict = json.loads(query_value).get("result")
        return ShopperProfile(**query_dict)


class DomainQuery(graphene.ObjectType):
    host = graphene.Field(HostInfo)
    registrar = graphene.Field(RegistrarInfo)
    reseller = graphene.Field(ResellerInfo)
    domain = graphene.String()

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


class Query(graphene.ObjectType):
    domain_query = graphene.Field(DomainQuery, domain=graphene.String(required=True))
    shopper_query = graphene.Field(ShopperQuery, id=graphene.String(required=True))

    def resolve_domain_query(self, args, context, info):
        return DomainQuery(domain=args.get('domain'))

    def resolve_shopper_query(self, args, context, info):
        return ShopperQuery(id=args.get('id'))


class RedisCache(object):
    def __init__(self, redis_host='redis', redis_ttl=86400):
        self.redis = Redis(redis_host)
        self.redis_ttl = redis_ttl

    def get_value(self, redis_key):
        try:
            redis_value = self.redis.get(redis_key)
        except Exception:
            redis_value = None
        return redis_value

    def set_value(self, redis_key, redis_value):
        self.redis.set(redis_key, redis_value)
        self.redis.expire(redis_key, self.redis_ttl)


class GraphQLViewWithCaching(GraphQLView):
    # Subclassing GraphQLView in order to intercept the incoming query, so that it
    #  may be compared to a Redis cache for quick response (if cached entry exists).
    #  If the query is not yet cached, then cache it along with the result/status_code
    #  after the call to superclass get_response() has returned
    def get_response(self, request, data, show_graphiql=False):
        redis_key = request.data
        query_value = app.redis.get_value(redis_key)
        if query_value is None:
            result, status_code = super(GraphQLViewWithCaching, self).get_response(request, data, show_graphiql)
            app.redis.set_value(redis_key, json.dumps({"result": result, "status_code": status_code}))
        else:
            query_dict = json.loads(query_value)
            result = query_dict.get("result")
            status_code = query_dict.get("status_code")
        return result, status_code


# setup logging
path = 'logging.yml'
value = os.getenv('LOG_CFG', None)
if value:
    path = value
if os.path.exists(path):
    with open(path, 'rt') as f:
        lconfig = yaml.safe_load(f.read())
    logging.config.dictConfig(lconfig)
else:
    logging.basicConfig(level=logging.INFO)


app = Flask(__name__)
app.debug = True
app.redis = RedisCache()
# Only instantiate the helper classes once, and attach it to the context, which is available
#  to all the other classes which need to use them
ctx = {'crm': CrmClientApi(),
       'regdb': RegDbAPI(),
       'vip': VipClients()}
schema = graphene.Schema(query=Query)
app.add_url_rule(
    '/graphql',
    view_func=GraphQLViewWithCaching.as_view(
        'graphql',
        schema=schema,
        graphiql=True,  # for having the GraphiQL interface
        context = ctx
    )
)

if __name__ == '__main__':
    app.run()
