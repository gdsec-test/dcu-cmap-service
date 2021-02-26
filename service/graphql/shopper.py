import graphene


class APIReseller(graphene.ObjectType):
    parent = graphene.String(description='API Reseller Parent ShopperID')
    child = graphene.String(description='API Reseller Child ShopperID')


class ShopperPortfolio:
    accountRepFirstName = graphene.String(description='Account Rep First Name')
    accountRepLastName = graphene.String(description='Account Rep Last Name')
    accountRepEmail = graphene.String(description='Account Rep Email Address')
    portfolioType = graphene.String(description='Shopper Portfolio Type')
    blacklist = graphene.Boolean(description='Shopper Blacklist Status - Do Not Suspend!', default_value=False)
    shopper_id = graphene.String(description='Shopper ID')


class ShopperProfile(graphene.ObjectType, ShopperPortfolio):
    # The following is a dynamic 'catch-all' method to intercept calls
    #  to any of the resolve_??? methods, instead of having to explicitly
    #  write out however many of them there need to be.  The member variables
    #  will still need to be defined in the ShopperPortfolio class.
    # http://stackoverflow.com/questions/42215848/specifically-named-dynamic-class-methods-in-python
    def __getattribute__(self, attr):
        if attr.startswith('resolve_'):
            if hasattr(self, attr[8:]):
                return lambda: getattr(self, attr[8:])
            return lambda: 'There is no value for {}'.format(attr[8:])
        return super(ShopperProfile, self).__getattribute__(attr)


class Shopper:
    """
    Top level Shopper Info
    """
    shopper_id = graphene.String(description='The oldest shopper_id on record')
    domain_count = graphene.Int(description='Number of domains owned by the shopper')
    # domain_search = graphene.Field(DomainSearch, regex=graphene.String(required=True))
    shopper_create_date = graphene.String(description='The create data of the shopper')
    shopper_email = graphene.String(description='Email Address for Shopper')
    shopper_plid = graphene.String(description='Private Label ID for Shopper')
    shopper_first_name = graphene.String(description='First Name for Shopper')
    shopper_last_name = graphene.String(description='Last Name for Shopper')
    shopper_address_1 = graphene.String(description='Address 1 for Shopper')
    shopper_address_2 = graphene.String(description='Address 2 for Shopper')
    shopper_city = graphene.String(description='City for Shopper')
    shopper_state = graphene.String(description='State for Shopper')
    shopper_postal_code = graphene.String(description='Postal Code for Shopper')
    shopper_country = graphene.String(description='Country for Shopper')
    shopper_phone_mobile = graphene.String(description='Mobile Phone Number for Shopper')
    shopper_phone_home = graphene.String(description='Home Phone Number for Shopper')
    shopper_phone_work = graphene.String(description='Work Phone Number Shopper')
    shopper_phone_work_ext = graphene.String(description='Work Phone Number Ext for Shopper')
    vip = graphene.Field(ShopperProfile, description='Shoppers VIP status')

    def resolve_domain_count(self, info):
        client = info.context.get('regdb')
        return client.get_domain_count_by_shopper_id(self.shopper_id)

    def resolve_vip(self, info):
        query_dict = info.context.get('crm').get_shopper_portfolio_information(self.shopper_id)
        # Query the blacklist, whose entities never get suspended
        query_dict['blacklist'] = info.context.get('vip').is_blacklisted(self.shopper_id)
        return ShopperProfile(**query_dict)


class ShopperQuery(graphene.ObjectType, Shopper):
    pass


class ShopperByDomain(graphene.ObjectType, Shopper):
    """
    Holds Shopper data when only the domain is known
    """
    pass
