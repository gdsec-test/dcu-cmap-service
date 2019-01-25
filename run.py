import logging.config
import os

import graphene
import tld
import yaml
from flask import Flask
from tld.conf import set_setting

from service.alexa import CallAwis
from service.brand_detection_helper import BrandDetectionHelper
from service.crm_client_api import CrmClientApi
from service.graph_ql import GraphQLViewWithCaching, Query
from service.hostenv_helper import Ipam
from service.redis_cache import RedisCache
from service.reg_db_api import RegDbAPI
from service.shopper_api import ShopperAPI
from service.subscriptions_api import SubscriptionsAPI
from service.vip_clients import VipClients
from service.whois_query import WhoisQuery
from settings import config_by_name

# Define a file we have write access to as the definitive tld names file
set_setting('NAMES_LOCAL_PATH', os.path.join(os.path.dirname(__file__), '/tmp/names.dat'))
tld.utils.PROJECT_DIR = lambda x: x

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
       'vip': VipClients(config, redis_obj),
       'redis': redis_obj,
       'shopper': ShopperAPI(config, redis_obj),
       'ipam': Ipam(config),
       'regdb': RegDbAPI(config, redis_obj),
       'alexa': CallAwis(config),
       'whois': WhoisQuery(),
       'bd': BrandDetectionHelper(config),
       'subscriptions': SubscriptionsAPI(config)
       }


@app.route('/health', methods=['GET'])
def health():
    return '', 200


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
