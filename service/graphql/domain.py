import re
from asyncio import run
from datetime import timedelta

import graphene
import tld
from csetutils.flask.logging import get_logging
from dateutil import parser

from service.graphql.host import HostInfo
from service.graphql.registrar import RegistrarInfo
from service.graphql.shopper import (APIReseller, ShopperByDomain,
                                     ShopperProfile)
from service.graphql.ssl import SSLSubscription
from service.graphql.sucuri import SecuritySubscription
from service.utils.functions import convert_str_to_none, get_fld_by_domain_name


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
    path = graphene.String(description='Reported content path')
    shopper_id = graphene.String(description='Shopper ID from DomainQuery')
    domain_status = graphene.Field(DomainStatusInfo, description='Registrar Domain Status for Provided Domain Name')
    host = graphene.Field(HostInfo, description='Hosting Information for Provided Domain Name')
    registrar = graphene.Field(RegistrarInfo, description='Registrar Information for Provided Domain Name')
    shopper_info = graphene.Field(ShopperByDomain, description='Shopper Information for Provided Domain Name')
    security_subscription = graphene.Field(SecuritySubscription,
                                           description='Security Product Information for Provided Domain Name')
    ssl_subscriptions = graphene.List(SSLSubscription,
                                      description='List of SSL Product Information for Provided Domain Name')
    is_domain_high_value = graphene.String(description='Valuation API Information for Provided Domain Name')

    @staticmethod
    def clean_attributes(info: dict, results: dict):
        results['data_center'] = info.get('data_center')
        results['created_date'] = info.get('created_date')
        results['friendly_name'] = info.get('friendly_name')
        results['os'] = info.get('os')
        results['product'] = info.get('product')
        results['guid'] = info.get('guid')
        results['container_id'] = info.get('container_id')
        results['shopper_id'] = info.get('shopper_id')
        results['entitlement_id'] = info.get('entitlement_id')
        results['hostname'] = info.get('hostname')
        results['ip'] = info.get('ip')
        results['mwp_id'] = info.get('account_id')
        results['private_label_id'] = info.get('private_label_id')
        results['username'] = info.get('username')
        results['managed_level'] = info.get('managed_level')
        results['first_pass_enrichment'] = info.get('first_pass_enrichment')
        results['second_pass_enrichment'] = info.get('second_pass_enrichment')
        results['abuse_report_email'] = info.get('abuse_report_email')

    def resolve_host(self, info):
        if hasattr(self.shopper_id, 'decode'):
            self.shopper_id = self.shopper_id.decode()

        whois = info.context.get('bd').get_hosting_info(self.domain)
        if whois['hosting_company_name'] == 'GoDaddy.com LLC':
            host_info = run(info.context.get('ipam').get_properties_for_domain(self.domain, self.shopper_id, self.path))
            if type(host_info) is dict:
                DomainQuery.clean_attributes(host_info, whois)

        vip = {}
        host_shopper = whois.get('shopper_id')
        if host_shopper:
            vip.update(info.context.get('crm').get_shopper_portfolio_information(host_shopper))
            # Query the blacklist, whose entities never get suspended
            vip['blacklist'] = info.context.get('vip').is_blacklisted(host_shopper)

            shopper_data = self.resolve_shopper_info(info, host_shopper)
            whois['customer_id'] = shopper_data.customer_id
            whois['shopper_create_date'] = shopper_data.shopper_create_date
            whois['shopper_plid'] = shopper_data.shopper_plid

            # If we have a PLID, overwrite the email with that PLID's email
            if shopper_data.shopper_plid:
                email = info.context.get('bd').get_email_info(shopper_data.shopper_plid)
                whois['abuse_report_email'] = email['email']

        whois['hosting_plan'] = None
        whois['subscription_status'] = None
        whois['started_as_free_trial'] = None
        if whois.get('customer_id') and whois.get('entitlement_id'):
            subscription = info.context.get('subscription_shim').get_subscription(whois.get('customer_id'), whois.get('entitlement_id'))
            whois['hosting_plan'] = subscription.get('offer', {}).get('plan', None)
            whois['subscription_status'] = subscription.get('status')
            entitlement = info.context.get('entitlementsapi').get_entitlement(whois.get('customer_id'), whois.get('entitlement_id'))
            keys = entitlement.get('prePurchaseKeyMap', {})
            recent = (parser.parse(subscription['metadata']['createdAt']) - parser.parse(subscription['statusUpdatedAt'])) <= timedelta(hours=24)
            started_as_free = (keys.get('custom_data.startedAsFreeMatTrial', False) or keys.get('custom_data.startedAsFreemium', False)) and recent
            whois['started_as_free_trial'] = started_as_free

        whois = convert_str_to_none(whois)
        host_obj = HostInfo(**whois)
        host_obj.vip = ShopperProfile(**vip)
        return host_obj

    def resolve_registrar(self, info):
        # If we were given a domain with a subdomain, request registrar information for just the domain.tld
        domain = get_fld_by_domain_name(self.domain)
        whois = info.context.get('bd').get_registrar_info(domain)
        return RegistrarInfo(**whois)

    def resolve_api_reseller(self, info):
        parent_child = info.context.get('regdb').get_parent_child_shopper_by_domain_name(self.domain)
        return APIReseller(**parent_child)

    def resolve_shopper_info(self, info, shopper_id=None):
        if hasattr(self.shopper_id, 'decode'):
            self.shopper_id = self.shopper_id.decode()

        if not shopper_id:
            shopper_id = self.shopper_id

        shopper_client = info.context.get('shopper')
        extra_data = shopper_client.get_shopper_by_shopper_id(shopper_id, ['shopper_create_date',
                                                                           'shopper_first_name',
                                                                           'shopper_email',
                                                                           'shopper_plid',
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
                                                                           'shopper_country',
                                                                           'customer_id'])
        return ShopperByDomain(shopper_id=shopper_id, **extra_data)

    def resolve_blacklist(self, info):
        bl = False
        try:
            domain_object = tld.get_tld(f'http://{self.domain}', as_object=True, search_private=False)
        except Exception:
            get_logging().exception('Error in tdl lookup for blacklist returing false')
            return False
        base_domain = domain_object.fld
        if info.context.get('vip').is_blacklisted(base_domain):
            bl = True
        elif domain_object.subdomain and info.context.get('vip').is_blacklisted(f'{domain_object.subdomain}.{base_domain}'):
            bl = True
        return bl

    def resolve_alexa_rank(self, info):
        return None

    def resolve_domain_status(self, info):
        domain = DomainStatusInfo()
        domain.domain = self.domain
        return domain

    def resolve_security_subscription(self, info):
        if hasattr(self.shopper_id, 'decode'):
            self.shopper_id = self.shopper_id.decode()

        sucuri_product = info.context.get('subscriptions').get_sucuri_subscriptions(self.shopper_id, self.domain)
        return SecuritySubscription(**{
            'sucuri_product': [x['sucuri_product'] for x in sucuri_product],
            'products': sucuri_product
        })

    def resolve_ssl_subscriptions(self, info):
        if hasattr(self.shopper_id, 'decode'):
            self.shopper_id = self.shopper_id.decode()

        ssl_subscriptions = info.context.get('subscriptions').get_ssl_subscriptions(self.shopper_id, self.domain)
        return [SSLSubscription(**{'cert_common_name': ssl_subscription.get('cert_common_name'),
                                   'cert_type': ssl_subscription.get('cert_type'),
                                   'created_at': ssl_subscription.get('created_at'),
                                   'expires_at': ssl_subscription.get('expires_at'),
                                   'entitlement_id': ssl_subscription.get('entitlement_id')})
                for ssl_subscription in ssl_subscriptions]

    def resolve_is_domain_high_value(self, info):
        return info.context.get('valuation').get_valuation_by_domain(self.domain)
