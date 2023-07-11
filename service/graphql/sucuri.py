import graphene


class SucuriProductDetails(graphene.ObjectType):
    sucuri_product = graphene.String(description='Sucuri Product')
    entitlement_id = graphene.String(description='Entitlement Id')
    created_date = graphene.String(description='Subscription created date')


class SecuritySubscription(graphene.ObjectType):
    sucuri_product = graphene.List(graphene.String, description='Sucuri Product(s)')
    products = graphene.List(SucuriProductDetails, description='Sucuri Product(s)')
