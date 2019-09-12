import logging.config
import os

import graphene
import tld
import urllib3
import yaml
from flask import Flask, Response, request
from flask_graphql import GraphQLView
from tld.conf import set_setting

from service.connectors.alexa import AlexaWebInformationService
from service.connectors.blacklist import VipClients
from service.connectors.brand_detection import BrandDetectionHelper
from service.connectors.crm import CRMClientAPI
from service.connectors.hosting_resolver import HostingProductResolver
from service.connectors.reg_db import RegDbAPI
from service.connectors.shopper import ShopperAPI
from service.connectors.subscriptions import SubscriptionsAPI
from service.connectors.whois import WhoisQuery
from service.graphql.schema import Query
from service.persist.redis import RedisCache
from settings import config_by_name

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Define a file we have write access to as the definitive tld names file
set_setting('NAMES_LOCAL_PATH', os.path.join(os.path.dirname(__file__), '/tmp/names.dat'))
tld.utils.PROJECT_DIR = lambda x: x

# setup logging
path = 'logging.yaml'
value = os.getenv('LOG_CFG')
if value:
    path = value
if os.path.exists(path):
    with open(path, 'rt') as f:
        lconfig = yaml.safe_load(f.read())
    logging.config.dictConfig(lconfig)
else:
    logging.basicConfig(level=logging.INFO)

config = config_by_name[os.getenv('sysenv', 'dev')]()

redis_obj = RedisCache(config)
app = Flask(__name__)

'''
Instantiate all of the helper classes that will be used by the resolves and pass them via the FlaskGraphQL context.
This makes these variables available to all resolvers that might need to call these objects.
'''
ctx = {'crm': CRMClientAPI(config, redis_obj),
       'vip': VipClients(config, redis_obj),
       'redis': redis_obj,
       'shopper': ShopperAPI(config),
       'ipam': HostingProductResolver(config),
       'regdb': RegDbAPI(config, redis_obj),
       'alexa': AlexaWebInformationService(config.ALEXA_ACCESS_ID, config.ALEXA_ACCESS_KEY),
       'whois': WhoisQuery(),
       'bd': BrandDetectionHelper(config.BRAND_DETECTION_URL),
       'subscriptions': SubscriptionsAPI(config)
       }


@app.route('/health', methods=['GET'])
def health():
    return '', 200


@app.before_request
def return_cached():
    if request.data:
        response = redis_obj.get(request.data)
        if response:
            return Response(response, 200)


@app.after_request
def cache_response(response):
    if request.data:
        redis_obj.set(request.data, response.data)
    return response


schema = graphene.Schema(query=Query)
app.add_url_rule('/graphql',
                 view_func=GraphQLView.as_view('graphql',
                                               schema=schema,
                                               graphiql=True,
                                               get_context=lambda: ctx)
                 )

if __name__ == '__main__':
    app.run()
