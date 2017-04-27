from cmap_service.service.whois_query import WhoisQuery
from mockredis import MockRedis
from collections import namedtuple
from nose.tools import assert_true, assert_false


class TestWhois:

    @classmethod
    def setup_class(cls):
        config = namedtuple('config', 'DATE_FORMAT')('%Y-%m-%d')
        cls.whois = WhoisQuery(config, MockRedis())

    def test_get_networks_for_ip(self):
        for domain in ['theaaronbean.com', 'comicsn.beer', 'impcat.com', 'mondoproibito.com']:
            assert_true(self.whois._check_hosted_here(self.whois.get_ip_from_domain(domain)))

        for domain in ['google.com', 'www-xn--kuvveyttrk-heb-com.usrfiles.com', 'tdvalidate.com']:
            assert_false(self.whois._check_hosted_here(self.whois.get_ip_from_domain(domain)))
