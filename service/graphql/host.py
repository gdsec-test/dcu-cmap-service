import graphene

from service.graphql.shopper import ShopperProfile


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
    private_label_id = graphene.String(description='Private Label ID for the reseller')