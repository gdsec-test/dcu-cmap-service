import json
import os

import graphene
import tld
import urllib3
from dcustructuredloggingflask.flasklogger import add_request_logging
from flask import Flask, Response, request
from flask_graphql import GraphQLView
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_flask_exporter.multiprocess import UWsgiPrometheusMetrics
from tld.conf import set_setting

from service.connectors.alexa import AlexaWebInformationService
from service.connectors.blacklist import VipClients
from service.connectors.brand_detection import BrandDetectionHelper
from service.connectors.crm import CRMClientAPI
from service.connectors.hosting_resolver import HostingProductResolver
from service.connectors.reg_db import RegDbAPI
from service.connectors.shopper import ShopperAPI
from service.connectors.subscriptions import SubscriptionsAPI
from service.connectors.valuation import ValuationAPI
from service.connectors.whois import WhoisQuery
from service.graphql.schema import Query
from service.persist.redis import RedisCache
from service.utils.sso_helper import do_login
from settings import config_by_name

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Define a file we have write access to as the definitive tld names file
set_setting('NAMES_LOCAL_PATH', os.path.join(os.path.dirname(__file__), '/tmp/names.dat'))
tld.utils.PROJECT_DIR = lambda x: x

config = config_by_name[os.getenv('sysenv', 'dev')]()

redis_obj = RedisCache(config)
app = Flask(__name__)

add_request_logging(app, 'cmap_service', sso=config.SSO_URL[8:], excluded_paths=[
    '/doc/',
    '/health'
], min_status_code=300)

# Set the secret key in Flask to be able to access the Session object
app.config['SECRET_KEY'] = os.urandom(12).hex()

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
       'subscriptions': SubscriptionsAPI(config),
       'valuation': ValuationAPI(config)
       }


@app.route('/health', methods=['GET'])
def health():
    return '', 200


@app.before_request
@do_login
def return_cached():
    if request.data:
        response = redis_obj.get(request.data)
        if response:
            return Response(response, 200)


@app.after_request
def cache_response(response):
    if response.status_code in [403, 401]:
        return response
    elif request.data:
        redis_obj.set(request.data, response.data)
    return response


@app.route('/v1/hosted/lookup', methods=['POST'])
def lookup_product():
    data = request.get_json()
    domain = data.get('domain', None)
    guid = data.get('guid', None)
    ip = data.get('ip', None)
    product = data.get('product', None)
    if domain is None or guid is None or ip is None or product is None:
        return '{"message": "Invalid parameters"}', 400

    resolver: HostingProductResolver = ctx['ipam']
    result = resolver.locate_product(domain, guid, ip, product)
    return json.dumps(result), 200


@app.route('/v1/shopper/lookup', methods=['POST'])
def lookup_shopper():
    data = request.get_json()
    shopper_id = data.get('shopper_id', None)
    if shopper_id is None:
        return '{"message": "Invalid parameters"}', 400

    crm: CRMClientAPI = ctx['crm']
    vip_client: VipClients = ctx['vip']
    shopper_client: ShopperAPI = ctx['shopper']

    shopper_data = {}
    extra_data = shopper_client.get_shopper_by_shopper_id(shopper_id, ['shopper_create_date'])
    shopper_data['shopper_create_date'] = extra_data.get('shopper_create_date')

    if shopper_data['shopper_create_date']:
        shopper_data['shopperId'] = shopper_id
        shopper_data['vip'] = crm.get_shopper_portfolio_information(shopper_id)
        shopper_data['vip']['blacklist'] = vip_client.is_blacklisted(shopper_id)
    else:
        shopper_data['shopperId'] = None
        shopper_data['vip'] = {
            'blacklist': False,
            'portfolioType': None,
            'shopperId': None
        }

    return json.dumps(shopper_data), 200


schema = graphene.Schema(query=Query)
app.add_url_rule('/graphql',
                 view_func=GraphQLView.as_view('graphql',
                                               schema=schema,
                                               graphiql=True,
                                               get_context=lambda: ctx)
                 )

# Need to use the special server for multiprocess apps. This only works
# when spawned within a UWSGI env. Otherwise use the default interface
# for local development.
if 'prometheus_multiproc_dir' in os.environ:
    metrics = UWsgiPrometheusMetrics(app, group_by='url_rule')
else:
    metrics = PrometheusMetrics(app, group_by='url_rule')
metrics.start_http_server(config.METRICS_PORT)

if __name__ == '__main__':
    app.run()
