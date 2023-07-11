import graphene


class SSLSubscription(graphene.ObjectType):
    cert_common_name = graphene.String(description='The common name of the ssl certificate')
    cert_type = graphene.String(description='The type of the ssl certificate')
    created_at = graphene.String(description='The date when the ssl certificate was created')
    expires_at = graphene.String(description='The date when the ssl certificate expires')
    entitlement_id = graphene.String(description='Entitlement Id')
