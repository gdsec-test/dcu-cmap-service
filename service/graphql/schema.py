
import graphene

from service.graphql.domain import DomainQuery
from service.graphql.shopper import ShopperQuery


class Query(graphene.ObjectType):
    domain_query = graphene.Field(DomainQuery,
                                  domain=graphene.String(required=True),
                                  path=graphene.String(required=False),
                                  description='Top level query based on domain names, with path optional')
    shopper_query = graphene.Field(ShopperQuery,
                                   id=graphene.String(required=True),
                                   description='Top level query based on shopper id')

    def resolve_domain_query(self, info, domain, path=''):
        whois = info.context.get('whois')

        if domain is None or len(domain) < 4:
            raise ValueError('Invalid domain string provided')
        if whois.is_ip(domain):
            domain = whois.get_domain_from_ip(domain)

        shopper_id = info.context.get('regdb').get_shopper_id_by_domain_name(domain)
        return DomainQuery(domain=domain, shopper_id=shopper_id)

    def resolve_shopper_query(self, info, id):
        if id is None or len(id) < 1:
            raise ValueError('Invalid shopper id string provided')
        extra_data = info.context.get('shopper').get_shopper_by_shopper_id(id, ['shopper_create_date',
                                                                                'shopper_first_name',
                                                                                'shopper_email',
                                                                                'customer_id'])
        return ShopperQuery(shopper_id=id, **extra_data)
