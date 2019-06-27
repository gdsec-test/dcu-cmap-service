from nose.tools import assert_equals, assert_is_none

from service.utils.hostname_parser import parse_hostname


class TestNutritionLabel:

    def test_bh_p3(self):
        hostname = 'P3PLPCS427'
        dc, os, product = parse_hostname(hostname)
        assert_equals(dc, 'P3')
        assert_equals(os, 'Linux')
        assert_equals(product, 'Diablo')

    def test_bh_n3(self):
        hostname = 'n3plvcpnl165093'
        dc, os, product = parse_hostname(hostname)
        assert_equals(dc, 'N3')
        assert_equals(os, 'Linux')
        assert_equals(product, 'Diablo')

    def test_bh_sg3(self):
        hostname = 'SG3PLPCS112'
        dc, os, product = parse_hostname(hostname)
        assert_equals(dc, 'SG2')
        assert_equals(os, 'Linux')
        assert_equals(product, 'Diablo')

    def test_diablo_p3(self):
        hostname = 'p3plcpnl0851'
        dc, os, product = parse_hostname(hostname)
        assert_equals(dc, 'P3')
        assert_equals(os, 'Linux')
        assert_equals(product, 'Diablo')

    def test_diablo_sg2(self):
        hostname = 'sg2plcpnl0178'
        dc, os, product = parse_hostname(hostname)
        assert_equals(dc, 'SG2')
        assert_equals(os, 'Linux')
        assert_equals(product, 'Diablo')

    def test_diablo_sg3(self):
        hostname = 'sg3plcpnl0178'
        dc, os, product = parse_hostname(hostname)
        assert_equals(dc, 'SG2')
        assert_equals(os, 'Linux')
        assert_equals(product, 'Diablo')

    def test_diablo_n1(self):
        hostname = 'n1plcpnl0089'
        dc, os, product = parse_hostname(hostname)
        assert_equals(dc, 'N1')
        assert_equals(os, 'Linux')
        assert_equals(product, 'Diablo')

    def test_diablo_n3(self):
        hostname = 'n3plcpnl0152'
        dc, os, product = parse_hostname(hostname)
        assert_equals(dc, 'N3')
        assert_equals(os, 'Linux')
        assert_equals(product, 'Diablo')

    def test_diablo_a2(self):
        hostname = 'a2plcpnl0223'
        dc, os, product = parse_hostname(hostname)
        assert_equals(dc, 'A2')
        assert_equals(os, 'Linux')
        assert_equals(product, 'Diablo')

    def test_4ghl(self):
        hostname = 'p3nlhg390c1390'
        dc, os, product = parse_hostname(hostname)
        assert_equals(dc, 'P3')
        assert_equals(os, 'Linux')
        assert_equals(product, '4GH')

    def test_4ghw(self):
        hostname = 'SG2NW8SHG121'
        dc, os, product = parse_hostname(hostname)
        assert_equals(dc, 'SG2')
        assert_equals(os, 'Windows')
        assert_equals(product, '4GH')

    def test_2ghl(self):
        hostname = 'P3SLH027'
        dc, os, product = parse_hostname(hostname)
        assert_equals(dc, 'P3')
        assert_equals(os, 'Linux')
        assert_equals(product, '2GH')

    def test_2ghw(self):
        hostname = 'P3NW8SH352'
        dc, os, product = parse_hostname(hostname)
        assert_equals(dc, 'P3')
        assert_equals(os, 'Windows')
        assert_equals(product, '2GH')

    def test_plesk_a2(self):
        hostname = 'A2NWVPWEB100'
        dc, os, product = parse_hostname(hostname)
        assert_equals(dc, 'A2')
        assert_equals(os, 'Windows')
        assert_equals(product, 'Plesk')

    def test_plesk_n1(self):
        hostname = 'N1NWVPWEB063'
        dc, os, product = parse_hostname(hostname)
        assert_equals(dc, 'N1')
        assert_equals(os, 'Windows')
        assert_equals(product, 'Plesk')

    def test_plesk_p3(self):
        hostname = 'P3NWVPWEB082'
        dc, os, product = parse_hostname(hostname)
        assert_equals(dc, 'P3')
        assert_equals(os, 'Windows')
        assert_equals(product, 'Plesk')

    def test_plesk_sg2(self):
        hostname = 'SG2NWVPWEB022'
        dc, os, product = parse_hostname(hostname)
        assert_equals(dc, 'SG2')
        assert_equals(os, 'Windows')
        assert_equals(product, 'Plesk')

    def test_vph_n1(self):
        hostname = 'n1plvph2-055'
        dc, os, product = parse_hostname(hostname)
        assert_equals(dc, 'N1')
        assert_equals(os, 'Linux')
        assert_equals(product, 'VPH')

    def test_vph_sg2(self):
        hostname = 'sg2plvph2-116'
        dc, os, product = parse_hostname(hostname)
        assert_equals(dc, 'SG2')
        assert_equals(os, 'Linux')
        assert_equals(product, 'VPH')

    def test_vertigo(self):
        hostname = 'vertigo-86545-primary'
        dc, os, product = parse_hostname(hostname)
        assert_equals(dc, 'vert')
        assert_is_none(os)
        assert_equals(product, 'Vertigo')

    def test_os_fail(self):
        hostname = 'p3nxhg390c1390'
        dc, os, product = parse_hostname(hostname)
        assert_equals(dc, 'P3')
        assert_is_none(os)
        assert_is_none(product)

    def test_vph(self):
        hostname = 'VPHL390c1390'
        dc, os, product = parse_hostname(hostname)
        assert_equals(dc, 'VPH')
        assert_is_none(os)
        assert_equals(product, 'VPH')

    def test_mwp1(self):
        hostname = 'ec2.3d3.myftpupload.com'
        dc, os, product = parse_hostname(hostname)
        assert_is_none(dc)
        assert_equals(os, 'Linux')
        assert_equals(product, 'MWP 1.0')

    def test_gocentral(self):
        hostname = 'A2MHLDPSWEB-01-VS'
        dc, os, product = parse_hostname(hostname)
        assert_equals(dc, 'A2')
        assert_is_none(os)
        assert_equals(product, 'GoCentral')

    def test_openstack(self):
        hostname = 'OpenStack floating IPs floating-iad-public-mah-public'
        dc, os, product = parse_hostname(hostname)
        assert_is_none(dc)
        assert_is_none(os)
        assert_equals(product, 'OpenStack')

    def test_url_shortener1(self):
        hostname = 'p3plshortapp-01-vs'
        dc, os, product = parse_hostname(hostname)
        assert_equals(dc, 'P3')
        assert_is_none(os)
        assert_equals(product, 'Shortener')

    def test_url_shortener2(self):
        hostname = 'url-shortenerfip01-vs'
        dc, os, product = parse_hostname(hostname)
        assert_is_none(dc)
        assert_is_none(os)
        assert_equals(product, 'Shortener')

    def test_untruthy_hostname(self):
        hostname = ''
        dc, os, product = parse_hostname(hostname)
        assert_is_none(dc)
        assert_is_none(os)
        assert_is_none(product)

    def test_unstringy_hostname(self):
        hostname = 8
        dc, os, product = parse_hostname(hostname)
        assert_is_none(dc)
        assert_is_none(os)
        assert_is_none(product)
