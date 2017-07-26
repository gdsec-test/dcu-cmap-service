import suds.client
import suds.sax.text
import logging
import ssl
from suds.sax.element import Element
from enrichment import nutrition_label


class ToolzillaApi(object):
    """
    Uses the AbsGUID interface. Class is used to look up a GUID in the Toolzilla API given a domain name.
    """
    ssl._create_default_https_context = ssl._create_unverified_context

    def __init__(self, settings):
        self.user = settings.TOOLZILLAUSER
        self.pwd = settings.TOOLZILLAPASS
        self.url = settings.TZ_URL
        auth_head = Element('acc:Authentication User="%s" Password="%s"' % (self.user, self.pwd))
        self.client = suds.client.Client(self.url)
        self.client.set_options(soapheaders=auth_head)

    def _hostname_query(self, guid):
        """
        Queries the Toolzilla API for a GUID for a domain name.
        :param domain:
        :return: GUID or None
        """
        try:
            data = self.client.service.getHostNameByGuid(guid)
            # checks to make sure the returned data is not an error
            if data:
                logging.info('guid searched for: %s', guid)
                hostname = data.split('.')[0]
                return hostname

        except Exception as e:
            logging.error(e.message)
            logging.error(self.client.last_received())
        return None

    def guid_query(self, domain):
        """
        Queries the Toolzilla API for a GUID for a domain name.
        :param domain:
        :return: GUID or None
        """
        try:
            data = self.client.service.searchByDomain(domain)
            # checks to make sure the returned data is not an error
            if str(type(data)) != "<class 'suds.sax.text.Text'>":

                logging.info('Domain searched for: %s', domain)
                shopper = str(data[0][0]['ShopperId'][0])
                hosting_guid = str(data[0][0]['AccountUid'][0])
                product = str(data[0][0]['ProductType'][0])
                if product == 'wpaas':
                    return {'guid': hosting_guid, 'shopper': shopper, 'product': product, 'os': 'Linux',
                            'hostname': 'Unable to locate', 'dc': 'Unable to locate'}
                elif product == 'dhs':
                    return {'guid': hosting_guid, 'shopper': shopper, 'product': product, 'os': 'Unable to locate',
                            'hostname': 'Unable to locate', 'dc': 'Unable to locate'}
                else:
                    hostname = self._hostname_query(hosting_guid)
                    extra = nutrition_label(hostname)
                    os = extra[1]
                    dc = extra[0]
                    product = extra[2]
                    return {'guid': hosting_guid, 'shopper': shopper, 'product': product, 'os': os, 'hostname': hostname, 'dc': dc}

        except Exception as e:
            logging.error(e.message)
            logging.error(self.client.last_received())

        return None
