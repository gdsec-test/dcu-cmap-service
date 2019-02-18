import graphene


class RegistrarInfo(graphene.ObjectType):
    brand = graphene.String(description='Registrar brand detected by Brand Detection')
    domain_create_date = graphene.String(description='Date domain was registered')
    domain_id = graphene.String(description='ID of domain name')
    registrar_abuse_email = graphene.List(graphene.String, description='Email contact(s)')
    registrar_name = graphene.String(description='Name of registrar or hosting provider')
