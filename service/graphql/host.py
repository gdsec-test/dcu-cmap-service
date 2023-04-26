import graphene

from service.graphql.shopper import ShopperProfile


class HostInfo(graphene.ObjectType):
    created_date = graphene.String(description='Created Date')
    data_center = graphene.String(description='Name of DataCenter that our server is in')
    friendly_name = graphene.String(description='Friendly Name')
    guid = graphene.String(description='GUID for hosting account')
    container_id = graphene.String(description='Container ID of hosting or server account, where applicable')
    brand = graphene.String(description='Hosting brand detected by Brand Detection')
    hosting_abuse_email = graphene.List(graphene.String, description='Email contact(s)')
    hosting_company_name = graphene.String(description='Name of registrar or hosting provider')
    hostname = graphene.String(description='Hostname of our server')
    ip = graphene.String(description='IP address of the reported domain')
    os = graphene.String(description='OS of our server')
    product = graphene.String(description='Name of our hosting product in use')
    shopper_id = graphene.String(description='Shopper account ID')
    shopper_plid = graphene.String(description='Private Label ID for Shopper')
    customer_id = graphene.String(description='Customer ID')
    entitlement_id = graphene.String(description='Entitlement Id')
    mwp_id = graphene.String(description='ID required for MWP 1.0 account suspension/reinstatement')
    vip = graphene.Field(ShopperProfile, description='Shoppers VIP status')
    private_label_id = graphene.String(description='Private Label ID for the reseller')
    reseller_id = graphene.String(description='Reseller ID for the reseller')
    shopper_create_date = graphene.String(description='The create data of the shopper')
    username = graphene.String(description='Username')
    managed_level = graphene.String(description='Managed Service Level, specific to servers')
    first_pass_enrichment = graphene.String(description='Which top level service was used to find the product.')
    second_pass_enrichment = graphene.String(description='Which top level service was used to find the product.')
    abuse_report_email = graphene.String(description='email to send abuse report to for hosting product')
    hosting_plan = graphene.String(description='The ecomm offer plan name')
