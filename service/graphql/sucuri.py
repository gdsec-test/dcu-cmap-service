import graphene


class SecuritySubscription(graphene.ObjectType):
    sucuri_product = graphene.List(graphene.String, description='Sucuri Product(s)')
