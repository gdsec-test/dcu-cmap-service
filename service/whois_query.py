import logging
import re
from dns import resolver, reversename


class WhoisQuery(object):

    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def is_ip(self, source_domain_or_ip):
        """
        Returns whether the given sourceDomainOrIp is an ip address
        :param source_domain_or_ip:
        :return:
        """
        pattern = re.compile(r"((([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])[ (\[]?(\.|dot)[ )\]]?){3}[0-9]{1,3})")
        return pattern.match(source_domain_or_ip) is not None

    def get_domain_from_ip(self, ip):
        dnsresolver = resolver.Resolver()
        addr = reversename.from_address(ip)
        dnsresolver.timeout = 1
        dnsresolver.lifetime = 1
        try:
            return dnsresolver.query(addr, 'PTR')[0].to_text().rstrip('.').encode('idna')
        except Exception as e:
            self._logger.error("Unable to get domain for %s : %s", ip, e.message)
