from cmap_service.service.whois_query import WhoisQuery
from mockredis import MockRedis
from collections import namedtuple
from nose.tools import assert_true, assert_false


class TestWhois:

    @classmethod
    def setup_class(cls):
        config = namedtuple('config', 'DATE_FORMAT')('%Y-%m-%d')
        cls.whois = WhoisQuery(config, MockRedis())
