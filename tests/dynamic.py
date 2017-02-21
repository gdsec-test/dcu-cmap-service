import graphene


class ApiObj(object):
    @staticmethod
    def get_values_as_dictionary():
        return {'dog': 'pound', 'cat': 'nip', 'horse': 'fly', 'bear': 'down'}


class ReturnKeys(graphene.Interface):
    dog = graphene.String()
    cat = graphene.String()
    horse = graphene.String()
    bear = graphene.String()


class ReturnValue(graphene.ObjectType):
    class Meta:
        interfaces = (ReturnKeys,)

    def __getattribute__(self, attr):
        if attr.startswith('resolve_'):
            if hasattr(self, attr[8:]):
                return lambda: getattr(self, attr[8:])
            return lambda: 'There is no value for {}'.format(attr[8:])
        return super(ReturnValue, self).__getattribute__(attr)


api = ApiObj()
value_dict = api.get_values_as_dictionary()
rv = ReturnValue(**value_dict)

print rv.resolve_nut()
print rv.resolve_cat()
print rv.resolve_dog()
print rv.resolve_horse()
print rv.resolve_bear()
print rv.resolve_animals()
print rv.resolve_paddy()
