import re
import graphene
from flask_graphql import GraphQLView
from whois import whois
import xml.etree.ElementTree as ET
from flask import Flask


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
    shopper_id = graphene.String()
    accountRep = graphene.String()


class ShopperId(graphene.Interface):
    domaincount = graphene.String()


class HostInfo(graphene.ObjectType):
    pass


class RegistrarInfo(graphene.ObjectType):
    class Meta:
        interfaces = (DomainName,)

    def resolve_name(self, args, context, info):
        w = whois(self.domain)
        return w.registrar


class ResellerInfo(graphene.ObjectType):
    class Meta:
        interfaces = (DomainName,)

    def resolve_parentChild(self, args, context, info):
        api = RegDbAPI()
        retval = api.get_parent_child_shopper_by_domain_name(self.domain)
        if retval[0] is False:
            return "No Parent/Child Info Found"
        return 'Parent:{}, Child:{}'.format(retval[0], retval[1])


class ShopperProfile(graphene.ObjectType):
    class Meta:
        interfaces = (ShopperPortfolio,)

    def resolve_phoneExt(self, args, context, info):
        return self.PhoneExt

    def resolve_firstName(self, args, context, info):
        return self.FirstName

    def resolve_lastName(self, args, context, info):
        return self.LastName

    def resolve_email(self, args, context, info):
        return self.Email

    def resolve_portfolioTypeID(self, args, context, info):
        return self.PortfolioTypeID

    def resolve_internalPhoneQueue(self, args, context, info):
        return self.InternalPhoneQueue

    def resolve_internalImageURL(self, args, context, info):
        return self.InternalImageURL

    def resolve_portfolioType(self, args, context, info):
        return self.PortfolioType

    def resolve_accountRep(self, args, context, info):
        return '{} {} ({})'.format(self.FirstName, self.LastName, self.Email)


class ShopperInfo(graphene.ObjectType):
    class Meta:
        interfaces = (ShopperId,)

    def resolve_domaincount(self, args, context, info):
        api = RegDbAPI()
        retval = api.get_domain_count_by_shopper_id(self.id)
        return retval


class ShopperQuery(graphene.ObjectType):
    shopperid = graphene.Field(ShopperInfo)
    profile = graphene.Field(ShopperProfile)
    id = graphene.String()

    def resolve_shopperid(self, args, context, info):
        shopper = ShopperInfo()
        shopper.id = self.id
        return shopper

    def resolve_profile(self, args, context, info):
        api = CrmClientApi()
        query_dict = api.get_shopper_portfolio_information(self.id)
        profile = ShopperProfile(**query_dict)
        return profile


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
    shopper_query = graphene.Field(ShopperQuery, id=graphene.Int(required=True))

    def resolve_domain_query(self, args, context, info):
        return DomainQuery(domain=args.get('domain'))

    def resolve_shopper_query(self, args, context, info):
        return ShopperQuery(id=args.get('id'))


app = Flask(__name__)
app.debug = True
schema = graphene.Schema(query=Query)
app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True  # for having the GraphiQL interface
    )
)

if __name__ == '__main__':
    app.run()
