import graphene


class SSLSubscription(graphene.ObjectType):
    ssl_product = graphene.List(graphene.String, description='SSL Product(s)')
