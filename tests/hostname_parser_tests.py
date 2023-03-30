from unittest import TestCase

from service.utils.hostname_parser import parse_hostname


class TestNutritionLabel(TestCase):

    def test_bh_p3(self):
        hostname = 'P3PLPCS427'
        dc, os, product = parse_hostname(hostname)
        self.assertEquals(dc, 'P3')
        self.assertEquals(os, 'Linux')
        self.assertEquals(product, 'Diablo')

    def test_5gh(self):
        hostname = 'PHX3 ARS2 SHR 5GH'
        dc, os, product = parse_hostname(hostname)
        self.assertEquals(os, 'Linux')
        self.assertEquals(product, 'Diablo')

    def test_bh_n3(self):
        hostname = 'n3plvcpnl165093'
        dc, os, product = parse_hostname(hostname)
        self.assertEquals(dc, 'N3')
        self.assertEquals(os, 'Linux')
        self.assertEquals(product, 'Diablo')

    def test_bh_sg3(self):
        hostname = 'SG3PLPCS112'
        dc, os, product = parse_hostname(hostname)
        self.assertEquals(dc, 'SG2')
        self.assertEquals(os, 'Linux')
        self.assertEquals(product, 'Diablo')

    def test_diablo_p3(self):
        hostname = 'p3plcpnl0851'
        dc, os, product = parse_hostname(hostname)
        self.assertEquals(dc, 'P3')
        self.assertEquals(os, 'Linux')
        self.assertEquals(product, 'Diablo')

    def test_diablo_sg2(self):
        hostname = 'sg2plcpnl0178'
        dc, os, product = parse_hostname(hostname)
        self.assertEquals(dc, 'SG2')
        self.assertEquals(os, 'Linux')
        self.assertEquals(product, 'Diablo')

    def test_diablo_sg3(self):
        hostname = 'sg3plcpnl0178'
        dc, os, product = parse_hostname(hostname)
        self.assertEquals(dc, 'SG2')
        self.assertEquals(os, 'Linux')
        self.assertEquals(product, 'Diablo')

    def test_diablo_n1(self):
        hostname = 'n1plcpnl0089'
        dc, os, product = parse_hostname(hostname)
        self.assertEquals(dc, 'N1')
        self.assertEquals(os, 'Linux')
        self.assertEquals(product, 'Diablo')

    def test_diablo_n3(self):
        hostname = 'n3plcpnl0152'
        dc, os, product = parse_hostname(hostname)
        self.assertEquals(dc, 'N3')
        self.assertEquals(os, 'Linux')
        self.assertEquals(product, 'Diablo')

    def test_diablo_a2(self):
        hostname = 'a2plcpnl0223'
        dc, os, product = parse_hostname(hostname)
        self.assertEquals(dc, 'A2')
        self.assertEquals(os, 'Linux')
        self.assertEquals(product, 'Diablo')

    def test_4ghl(self):
        hostname = 'p3nlhg390c1390'
        dc, os, product = parse_hostname(hostname)
        self.assertEquals(dc, 'P3')
        self.assertEquals(os, 'Linux')
        self.assertEquals(product, '4GH')

    def test_4ghw(self):
        hostname = 'SG2NW8SHG121'
        dc, os, product = parse_hostname(hostname)
        self.assertEquals(dc, 'SG2')
        self.assertEquals(os, 'Windows')
        self.assertEquals(product, '4GH')

    def test_2ghl(self):
        hostname = 'P3SLH027'
        dc, os, product = parse_hostname(hostname)
        self.assertEquals(dc, 'P3')
        self.assertEquals(os, 'Linux')
        self.assertEquals(product, '2GH')

    def test_2ghw(self):
        hostname = 'P3NW8SH352'
        dc, os, product = parse_hostname(hostname)
        self.assertEquals(dc, 'P3')
        self.assertEquals(os, 'Windows')
        self.assertEquals(product, '2GH')

    def test_plesk_a2(self):
        hostname = 'A2NWVPWEB100'
        dc, os, product = parse_hostname(hostname)
        self.assertEquals(dc, 'A2')
        self.assertEquals(os, 'Windows')
        self.assertEquals(product, 'Plesk')

    def test_plesk_n1(self):
        hostname = 'N1NWVPWEB063'
        dc, os, product = parse_hostname(hostname)
        self.assertEquals(dc, 'N1')
        self.assertEquals(os, 'Windows')
        self.assertEquals(product, 'Plesk')

    def test_plesk_p3(self):
        hostname = 'P3NWVPWEB082'
        dc, os, product = parse_hostname(hostname)
        self.assertEquals(dc, 'P3')
        self.assertEquals(os, 'Windows')
        self.assertEquals(product, 'Plesk')

    def test_plesk_sg2(self):
        hostname = 'SG2NWVPWEB022'
        dc, os, product = parse_hostname(hostname)
        self.assertEquals(dc, 'SG2')
        self.assertEquals(os, 'Windows')
        self.assertEquals(product, 'Plesk')

    def test_vph_n1(self):
        hostname = 'n1plvph2-055'
        dc, os, product = parse_hostname(hostname)
        self.assertEquals(dc, 'N1')
        self.assertEquals(os, 'Linux')
        self.assertEquals(product, 'VPH')

    def test_vph_sg2(self):
        hostname = 'sg2plvph2-116'
        dc, os, product = parse_hostname(hostname)
        self.assertEquals(dc, 'SG2')
        self.assertEquals(os, 'Linux')
        self.assertEquals(product, 'VPH')

    def test_vertigo(self):
        hostname = 'vertigo-86545-primary'
        dc, os, product = parse_hostname(hostname)
        self.assertEquals(dc, 'vert')
        self.assertIsNone(os)
        self.assertEquals(product, 'Vertigo')

    def test_os_fail(self):
        hostname = 'p3nxhg390c1390'
        dc, os, product = parse_hostname(hostname)
        self.assertEquals(dc, 'P3')
        self.assertIsNone(os)
        self.assertIsNone(product)

    def test_vph(self):
        hostname = 'VPHL390c1390'
        dc, os, product = parse_hostname(hostname)
        self.assertEquals(dc, 'VPH')
        self.assertIsNone(os)
        self.assertEquals(product, 'VPH')

    def test_mwp1(self):
        hostname = 'ec2.3d3.myftpupload.com'
        dc, os, product = parse_hostname(hostname)
        self.assertIsNone(dc)
        self.assertEquals(os, 'Linux')
        self.assertEquals(product, 'MWP 1.0')

    def test_gocentral(self):
        hostname1 = 'A2MHLDPSWEB-01-VS'
        hostname2 = 'A2STARKGATE-01-VS'
        hostname3 = 'P3PWSSWEB-01-VS'
        dc1, os1, product1 = parse_hostname(hostname1)
        dc2, os2, product2 = parse_hostname(hostname2)
        dc3, os3, product3 = parse_hostname(hostname3)
        self.assertEquals(dc1, 'A2')
        self.assertIsNone(os1)
        self.assertEquals(product1, 'GoCentral')
        self.assertEquals(dc2, 'A2')
        self.assertIsNone(os2)
        self.assertEquals(product2, 'GoCentral')
        self.assertEquals(dc3, 'P3')
        self.assertIsNone(os3)
        self.assertEquals(product3, 'GoCentral')

    def test_openstack(self):
        hostname = 'OpenStack floating IPs floating-iad-public-mah-public'
        dc, os, product = parse_hostname(hostname)
        self.assertIsNone(dc)
        self.assertIsNone(os)
        self.assertEquals(product, 'OpenStack')

    def test_url_shortener1(self):
        hostname = 'p3plshortapp-01-vs'
        dc, os, product = parse_hostname(hostname)
        self.assertEquals(dc, 'P3')
        self.assertIsNone(os)
        self.assertEquals(product, 'Shortener')

    def test_url_shortener2(self):
        hostname = 'url-shortenerfip01-vs'
        dc, os, product = parse_hostname(hostname)
        self.assertIsNone(dc)
        self.assertIsNone(os)
        self.assertEquals(product, 'Shortener')

    def test_untruthy_hostname(self):
        hostname = ''
        dc, os, product = parse_hostname(hostname)
        self.assertIsNone(dc)
        self.assertIsNone(os)
        self.assertIsNone(product)

    def test_unstringy_hostname(self):
        hostname = 8
        dc, os, product = parse_hostname(hostname)
        self.assertIsNone(dc)
        self.assertIsNone(os)
        self.assertIsNone(product)

    def test_gem(self):
        hostname1 = 'P3PLGEMWBEB01'
        hostname2 = 'P3PLWBEOUTDB01'
        dc1, os1, product1 = parse_hostname(hostname1)
        dc2, os2, product2 = parse_hostname(hostname2)
        self.assertEquals(dc1, 'P3')
        self.assertIsNone(os1)
        self.assertEquals(product1, 'GEM')
        self.assertEquals(dc2, 'P3')
        self.assertIsNone(os2)
        self.assertEquals(product2, 'GEM')

    def test_redir(self):
        hostname = 'P3REDIRB01'
        dc, os, product = parse_hostname(hostname)
        self.assertEquals(dc, 'P3')
        self.assertIsNone(os)
        self.assertEquals(product, 'EOL')

    def test_vnext_store(self):
        hostname = 'P3PLNEMOATS001'
        dc, os, product = parse_hostname(hostname)
        self.assertEquals(dc, 'P3')
        self.assertIsNone(os)
        self.assertEquals(product, 'vNext Store')

    def test_mwp1_not_matching(self):
        hostname = 'testmyftpupload.com'
        dc, os, product = parse_hostname(hostname)
        self.assertIsNone(dc)
        self.assertIsNone(os)
        self.assertIsNone(product)
