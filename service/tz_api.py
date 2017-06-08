import suds.client
import suds.sax.text
import logging
import ssl
from suds.sax.element import Element


class ToolzillaApi(object):
    """
    Uses the AbsGUID interface. Class is used to look up a GUID in the Toolzilla API given a domain name.
    """
    url = 'https://toolzilla.int.godaddy.com/webservice.php/AccountSearchService/WSDL'
    ssl._create_default_https_context = ssl._create_unverified_context

    def __init__(self, settings):
        self.user = settings.TOOLZILLAUSER
        self.pwd = settings.TOOLZILLAPASS
        auth_head = Element('acc:Authentication User="' + self.user + '" Password="' + self.pwd + '"')
        self.client = suds.client.Client(self.url)
        self.client.set_options(soapheaders=auth_head)

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
                hosting_guid = str(data[0][0][2][0])
                return hosting_guid

            return None

        except Exception as e:
            logging.error(e.message)
            logging.error(self.client.last_received())
            return None