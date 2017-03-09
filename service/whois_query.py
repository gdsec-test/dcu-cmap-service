import pythonwhois

import re
import socket

from ipwhois import IPWhois
from whois.parser import PywhoisError
from nic_client import NICClient

from classlogger import class_logger

class WhoisQuery(object):

    def get_registrar_abuse(self, domain):
        domain_query = pythonwhois.get_whois(domain)
        email_list = domain_query.get('emails')
        abuse_string = ",".join(email_list)
        return abuse_string

    def get_domain_create_date(self, domain_name):
        """
        Returns the date the domain name was created or None if not found
        :param domain_name:
        :return:
        """
        domain_name = domain_name[4:] if domain_name[:4] == 'www.' else domain_name
        domain_query = pythonwhois.get_whois(domain_name)
        if "No match" not in domain_query:
            creation_date_query = domain_query.get('creation_date')
            creation_date = creation_date_query[0].strftime('%Y/%m/%d')
            return creation_date
        return None


    #for host lookup, refer to dmv code
class Host(object):

    ABUSE = 'abuse'

    def __init__(self):
        self._host = None
        self._ip = None
        self._abuse_email = None

    # Internal method needed by _get_abuse_email_from_ip()
    #  for when the whois info cannot be extracted via domain name
    def _get_ip_from_host(self, my_host=None):
        ret_bool = False
        if my_host is None:
            if self._host is None:
                self._logger.fatal('FATAL: No host provided')
                return
        else:
            self._host = my_host

        self._ip = None
        try:
            ip = socket.gethostbyname(self._host)
            if ip is not None:
                self._ip = ip
                ret_bool = True
            else:
                self._logger.fatal('FATAL: Cannot resolve host: {} into an IP'.format(self._host))

        except socket.gaierror:
            # Ignore this, as it means the host name is invalid
            self._logger.warn('WARNING: Unknown host name provided: {}'.format(self._host))
        except Exception as e:
            self._logger.fatal(e.message)
        finally:
            return ret_bool

    # Internal method needed when the whois info cannot be extracted
    #  via domain name in get_abuse_email_from_host()
    def _get_abuse_email_from_ip(self, my_ip=None):
        if my_ip is None:
            if self._ip is None:
                self._logger.fatal('FATAL: No IP address provided')
                return
        else:
            self._ip = my_ip

        self._abuse_email = None
        try:
            ipw = IPWhois(self._ip)
            w = ipw.lookup_rdap()   # <-- Takes a long time to run

            for contact in w['objects']:
                if str(contact).lower().find(self.ABUSE) == 0:
                    self._abuse_email = w['objects'][contact]['contact']['email'][0]['value']
        except Exception as e:
            self._logger.fatal(e.message)
        finally:
            return self._abuse_email

    # If the whois package cant extract the abuse@ email, then try the old fashioned way
    #  of a regex'ing the return of a system call
    def _get_abuse_email_from_ip_regex(self):
        self._abuse_email = None
        try:
            nic_client = NICClient()
            result = nic_client.whois_lookup(self._ip, 0)
            # matches any string starting with 'abuse@', in attempt to extract email address like: abuse@godaddy.com
            # underscore must precede dash in regex, for some reason
            m = re.findall("(abuse[a-zA-Z0-9._-]*@[a-zA-Z0-9._-]*)", result)
            if not m:
                # matches any string which is preceded by the string '*AbuseEmail: '
                # underscore must precede dash in regex, for some reason
                m = re.findall("[Aa]buse[Ee]mail:\s+([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+)", result)
                if not m:
                    self._logger.warn('Cant find abuse@ for {} - {}'.format(self._host, self._ip))
                    return
            # An abuse email has been found, make sure its not a top level whois address
            for nichost in nic_client.IP_WHOIS:
                # remove the 'whois.' from the beginning of the string
                nichost = nichost[6:]
                if nichost in m[-1]:
                    # Its a top level whois address, so return None
                    return
            self._abuse_email = m[-1]
        except Exception as e:
            self._logger.fatal(e.message)
        finally:
            return self._abuse_email

    # Attempt to extract an abuse email address from a string or list
    def _extract_abuse_email_address(self, email_info):
        self._abuse_email = None

        try:
            # If we are passed a list
            if isinstance(email_info, list):
                for email in email_info:
                    if str(email).lower().find(self.ABUSE) == 0:
                        self._abuse_email = email
                        break
            # If we are passed a string
            elif isinstance(email_info, str):
                if(str(email_info).lower().find(self.ABUSE)) == 0:
                    self._abuse_email = email_info

        except Exception as e:
            self._logger.fatal(e.message)
        finally:
            return self._abuse_email

    @staticmethod
    def _is_ip_address(my_input):
        if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", my_input):
            return True
        return False

    def get_ip_address(self):
        return self._ip

    # External method used to extract whois info from just a host name
    def get_abuse_email(self, my_input):
        self._abuse_email = None

        try:
            if my_input is None:
                self._logger.fatal('FATAL: User did not provide a Host or IP')
                return

            if not Host._is_ip_address(my_input):
                # the method must have been passed a hostname, so try to get the ip
                self._host = my_input
                if not self._get_ip_from_host():
                    self._logger.warn('WARNING Cant extract ip address for host: {}'.format(my_input))
                    return
            else:
                self._ip = my_input

            # we have an ip, try the regex approach
            self._abuse_email = self._get_abuse_email_from_ip_regex()
            if self._abuse_email is None:
                # first attempt failed, try to get the abuse@ email from self._ip
                self._abuse_email = self._get_abuse_email_from_ip()
                if self._abuse_email is None:
                    # give up, we didnt find an abuse@ email
                    self._logger.warn('WARNING Cant extract abuse email for {} ({})'.format(my_input, self._ip))
                    return

            # we found an abuse@ email
            self._logger.info('Host: {} , Ip: {} , Email: {}'.format(self._host, self._ip, self._abuse_email))
            return self._abuse_email

        except PywhoisError:
            self._logger.warn('WARNING: Unknown host name provided: {}'.format(self._host))
        except Exception as e:
            self._logger.fatal(e.message)
        finally:
            return self._abuse_email