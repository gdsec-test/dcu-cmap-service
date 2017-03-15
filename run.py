import os
import yaml
import graphene

import logging.config

from flask import Flask

from service.graph_ql import GraphQLViewWithCaching, Query
from service.reg_db_api import RegDbAPI
from service.redis_cache import RedisCache
from service.vip_clients import VipClients
from service.crm_client_api import CrmClientApi
from service.shopper_api import ShopperAPI
from service.whois_query import WhoisQuery

from settings import config_by_name


# setup logging
path = 'logging.yml'
value = os.getenv('LOG_CFG', None)
if value:
    path = value
if os.path.exists(path):
    with open(path, 'rt') as f:
        lconfig = yaml.safe_load(f.read())
    logging.config.dictConfig(lconfig)
else:
    logging.basicConfig(level=logging.INFO)

# Import appropriate settings for running environment
env = os.getenv('sysenv') or 'dev'
config = config_by_name[env]()
redis_obj = RedisCache(config)

app = Flask(__name__)
app.debug = True

# Only instantiate the helper classes once, and attach it to the context, which is available
#  to all the other classes which need to use them
ctx = {'crm': CrmClientApi(config, redis_obj),
       'regdb': RegDbAPI(config, redis_obj),
       'vip': VipClients(config, redis_obj),
       'redis': redis_obj,
       'shopper': ShopperAPI(config, redis_obj),
       'whois': WhoisQuery(config, redis_obj)}

schema = graphene.Schema(query=Query)
app.add_url_rule(
    '/graphql',
    view_func=GraphQLViewWithCaching.as_view(
        'graphql',
        schema=schema,
        graphiql=True,  # for having the GraphiQL interface
        context=ctx
    )
)

if __name__ == '__main__':
    app.run()
