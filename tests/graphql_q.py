import graphene


class DomainName(graphene.Interface):
    name = graphene.String()
    domain = ''


class HostInfo(graphene.ObjectType):
    class Meta:
        interfaces = (DomainName,)

    def resolve_name(self, args, context, info):
        # Code to get the hosting provider
        return 'The Host for {}'.format(self.domain)


class RegistrarInfo(graphene.ObjectType):
    class Meta:
        interfaces = (DomainName,)

    def resolve_name(self, args, context, info):
        # Code to get the registrar
        return 'The Registrar for {}'.format(self.domain)


class DomainQuery(graphene.ObjectType):
    host = graphene.Field(HostInfo)
    registrar = graphene.Field(RegistrarInfo)
    domain = graphene.String()

    def resolve_host(self, args, context, info):
        domain = HostInfo()
        domain.domain = self.domain
        return domain

    def resolve_registrar(self, args, context, info):
        domain = RegistrarInfo()
        domain.domain = self.domain
        return domain


class Query(graphene.ObjectType):
    domain_query = graphene.Field(DomainQuery, domain=graphene.String(required=True))

    def resolve_domain_query(self, args, context, info):
        return DomainQuery(domain=args.get('domain'))


if __name__ == '__main__':
    di = graphene.Schema(query=Query)
    query = '''
        query{
            domainQuery(domain: "a.com") {
                domain
                host {
                    name
                }
                registrar {
                    name
                }
            }
        }
    '''
    result = di.execute(query)

    print result.data
