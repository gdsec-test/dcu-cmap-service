import re

import graphene

from service.graphql.host import HostInfo
from service.graphql.registrar import RegistrarInfo
from service.graphql.shopper import (APIReseller, ShopperByDomain,
                                     ShopperProfile)
from service.graphql.sucuri import SecuritySubscription
from service.utils.functions import get_tld_by_domain_name


class StatusInfo(graphene.Interface):
    domain = ''
    statusCode = graphene.String(description='The registrar status code for provided domain name')


# TODO: Finish endpoint once client cert is white-listed
class DomainStatusInfo(graphene.ObjectType):
    class Meta:
        interfaces = (StatusInfo,)

    def resolve_statusCode(self, info):
        return "PLACEHOLDER: domain status code"


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


class DomainQuery(graphene.ObjectType):
    alexa_rank = graphene.Int(description='Alexa World Wide Rank for domain')
    api_reseller = graphene.Field(APIReseller, description='API Reseller Information for Provided Domain Name')
    blacklist = graphene.Boolean(description='Domain Name Blacklist Status - Do Not Suspend!')
    domain = graphene.String(description='Domain Name from DomainQuery')
    domain_status = graphene.Field(DomainStatusInfo, description='Registrar Domain Status for Provided Domain Name')
    host = graphene.Field(HostInfo, description='Hosting Information for Provided Domain Name')
    registrar = graphene.Field(RegistrarInfo, description='Registrar Information for Provided Domain Name')
    shopper_info = graphene.Field(ShopperByDomain, description='Shopper Information for Provided Domain Name')
    security_subscription = graphene.Field(SecuritySubscription,
                                           description='Security Product Information for Provided Domain Name')

    def resolve_host(self, info):
        # These default initializations are put in place to allow for upgrade to Graphql 2.0. A bug currently exists
        # that defaults all uninitialized fields as a `graphene.String object at X memory location` rather than null
        # in Graphql 1.4.1. This fixes that bug until it is addressed. 8 Nov 2017 @nlemay.
        vip = dict(blacklist=False, accountRepFirstName=None, accountRepLastName=None, accountRepEmail=None,
                   portfolioType=None, shopper_id=None)
        whois = dict(data_center=None, os=None, product=None, guid=None, shopper_id=None, hostname=None, ip=None,
                     mwp_id=None, hosting_company_name=None, brand=None, hosting_abuse_email=None, created_date=None,
                     friendly_name=None, private_label_id=None)

        shopper_id = info.context.get('regdb').get_shopper_id_by_domain_name(self.domain)
        if hasattr(shopper_id, 'decode'):
            shopper_id = shopper_id.decode()

        whois.update(info.context.get('bd').get_hosting_info(self.domain))
        if whois['hosting_company_name'] == 'GoDaddy.com LLC':
            host_info = info.context.get('ipam').get_properties_for_domain(self.domain, shopper_id)
            if type(host_info) is dict:
                whois['data_center'] = host_info.get('data_center')
                whois['created_date'] = host_info.get('created_date')
                whois['friendly_name'] = host_info.get('friendly_name')
                whois['os'] = host_info.get('os')
                whois['product'] = host_info.get('product')
                whois['guid'] = host_info.get('guid')
                whois['shopper_id'] = host_info.get('shopper_id')
                whois['hostname'] = host_info.get('hostname')
                whois['ip'] = host_info.get('ip')
                whois['mwp_id'] = host_info.get('accountid')
                whois['private_label_id'] = host_info.get('private_label_id')

        shopper_id = whois.get('shopper_id')
        if shopper_id:
            vip.update(info.context.get('crm').get_shopper_portfolio_information(shopper_id))
            # Query the blacklist, whose entities never get suspended
            vip['blacklist'] = info.context.get('vip').is_blacklisted(shopper_id)

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
        return APIReseller(**parent_child)

    def resolve_shopper_info(self, info):
        active_shopper = info.context.get('regdb').get_shopper_id_by_domain_name(self.domain)
        if hasattr(active_shopper, 'decode'):
            active_shopper = active_shopper.decode()

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
        return info.context.get('vip').is_blacklisted(self.domain)

    def resolve_alexa_rank(self, info):
        return info.context.get('alexa').get_url_information(self.domain)

    def resolve_domain_status(self, info):
        domain = DomainStatusInfo()
        domain.domain = self.domain
        return domain

    def resolve_security_subscription(self, info):
        shopper_id = info.context.get('regdb').get_shopper_id_by_domain_name(self.domain)
        if hasattr(shopper_id, 'decode'):
            shopper_id = shopper_id.decode()

        sucuri_product = info.context.get('subscriptions').get_sucuri_subscriptions(shopper_id, self.domain)
        return SecuritySubscription(**{'sucuri_product': sucuri_product})
