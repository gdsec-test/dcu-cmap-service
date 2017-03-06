"""
Whois client for python
transliteration of:
http://www.opensource.apple.com/source/adv_cmds/adv_cmds-138.1/whois/whois.c
Copyright (c) 2010 Chris Wolf
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
  Last edited by:  $Author$
              on:  $DateTime$
        Revision:  $Revision$
              Id:  $Id$
          Author:  Chris Wolf
"""
import re
import sys
import socket
from classlogger import class_logger


@class_logger
class NICClient(object):

    NICHOST             = "whois.crsnic.net"
    DNICHOST            = "whois.nic.mil"
    GNICHOST            = "whois.nic.gov"
    ANICHOST            = "whois.arin.net"
    LNICHOST            = "whois.lacnic.net"
    RNICHOST            = "whois.ripe.net"
    PNICHOST            = "whois.apnic.net"
    MNICHOST            = "whois.ra.net"
    SNICHOST            = "whois.6bone.net"
    BNICHOST            = "whois.registro.br"
    NORIDHOST           = "whois.norid.no"
    IANAHOST            = "whois.iana.org"
    GERMNICHOST         = "de.whois-servers.net"
    WHOIS_SERVER_ID     = "Whois Server:"
    WHOIS_ORG_SERVER_ID = "Registrant Street1:Whois Server:"

    WHOIS_RECURSE = 0x01

    IP_WHOIS = [LNICHOST, RNICHOST, PNICHOST, BNICHOST]

    def __init__(self):
        self.use_qnichost = False

    @staticmethod
    def findwhois_server(buf, hostname):
        # Search the initial TLD lookup results for the regional-specifc
        # whois server for getting contact details.
        nhost = None
        start = buf.lower().find(NICClient.WHOIS_SERVER_ID)
        if start == -1:
            start = buf.find(NICClient.WHOIS_ORG_SERVER_ID)

        if start > -1:
            end = buf[start:].find('\n')
            whois_line = buf[start:end + start]
            for nichost in NICClient.IP_WHOIS:
                if nichost in whois_line:
                    nhost = nichost
                    break
        elif hostname == NICClient.ANICHOST:
            for nichost in NICClient.IP_WHOIS:
                if buf.find(nichost) != -1:
                    nhost = nichost
                    break
        return nhost

    def whois(self, query, hostname, whois_flags):
        # Perform initial lookup with TLD whois server
        # then, if the quick flag is false, search that result
        # for the region-specifc whois server and do a lookup
        # there for contact details
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((hostname, 43))
        if hostname == NICClient.GERMNICHOST:
            s.send("-T dn,ace -C US-ASCII " + query + "\r\n")
        else:
            s.send(query + "\r\n")
        response = ''
        while True:
            d = s.recv(4096)
            response += d
            if not d:
                break
        s.close()

        nhost = None
        if whois_flags & NICClient.WHOIS_RECURSE and nhost is None:
            nhost = NICClient.findwhois_server(response, hostname)
        if nhost is not None:
            response += self.whois(query, nhost, 0)
        return response

    def whois_lookup(self, query_arg, whoislu_flags):
        """Main entry point: Perform initial lookup on TLD whois server,
        or other server to get region-specific whois server, then if quick
        flag is false, perform a second lookup on the region-specific
        server for contact records"""

        # this would be the case when this function is called by other then main
        whoislu_flags |= NICClient.WHOIS_RECURSE
        whois_result = self.whois(query_arg, NICClient.ANICHOST, whoislu_flags)
        return whois_result

