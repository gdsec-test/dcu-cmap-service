from nose.tools import assert_equals

from service.enrichment import nutrition_label


class TestNutritionLabel:
    def __init__(self):
        pass

    def test_bh_p3(self):
        hostname = 'P3PLPCS427'
        dc, os, product = nutrition_label(hostname)
        assert_equals(dc, 'P3')
        assert_equals(os, 'Linux')
        assert_equals(product, 'Diablo')

    def test_bh_n3(self):
        hostname = 'n3plvcpnl165093'
        dc, os, product = nutrition_label(hostname)
        assert_equals(dc, 'N3')
        assert_equals(os, 'Linux')
        assert_equals(product, 'Diablo')

    def test_bh_sg3(self):
        hostname = 'SG3PLPCS112'
        dc, os, product = nutrition_label(hostname)
        assert_equals(dc, 'SG2')
        assert_equals(os, 'Linux')
        assert_equals(product, 'Diablo')

    def test_diablo_p3(self):
        hostname = 'p3plcpnl0851'
        dc, os, product = nutrition_label(hostname)
        assert_equals(dc, 'P3')
        assert_equals(os, 'Linux')
        assert_equals(product, 'Diablo')

    def test_diablo_sg2(self):
        hostname = 'sg2plcpnl0178'
        dc, os, product = nutrition_label(hostname)
        assert_equals(dc, 'SG2')
        assert_equals(os, 'Linux')
        assert_equals(product, 'Diablo')

    def test_diablo_sg3(self):
        hostname = 'sg3plcpnl0178'
        dc, os, product = nutrition_label(hostname)
        assert_equals(dc, 'SG2')
        assert_equals(os, 'Linux')
        assert_equals(product, 'Diablo')

    def test_diablo_n1(self):
        hostname = 'n1plcpnl0089'
        dc, os, product = nutrition_label(hostname)
        assert_equals(dc, 'N1')
        assert_equals(os, 'Linux')
        assert_equals(product, 'Diablo')

    def test_diablo_n3(self):
        hostname = 'n3plcpnl0152'
        dc, os, product = nutrition_label(hostname)
        assert_equals(dc, 'N3')
        assert_equals(os, 'Linux')
        assert_equals(product, 'Diablo')

    def test_diablo_a2(self):
        hostname = 'a2plcpnl0223'
        dc, os, product = nutrition_label(hostname)
        assert_equals(dc, 'A2')
        assert_equals(os, 'Linux')
        assert_equals(product, 'Diablo')

    def test_4ghl(self):
        hostname = 'p3nlhg390c1390'
        dc, os, product = nutrition_label(hostname)
        assert_equals(dc, 'P3')
        assert_equals(os, 'Linux')
        assert_equals(product, '4GH')

    def test_4ghw(self):
        hostname = 'SG2NW8SHG121'
        dc, os, product = nutrition_label(hostname)
        assert_equals(dc, 'SG2')
        assert_equals(os, 'Windows')
        assert_equals(product, '4GH')

    def test_2ghl(self):
        hostname = 'P3SLH027'
        dc, os, product = nutrition_label(hostname)
        assert_equals(dc, 'P3')
        assert_equals(os, 'Linux')
        assert_equals(product, '2GH')

    def test_2ghw(self):
        hostname = 'P3NW8SH352'
        dc, os, product = nutrition_label(hostname)
        assert_equals(dc, 'P3')
        assert_equals(os, 'Windows')
        assert_equals(product, '2GH')

    def test_angelo_a2(self):
        hostname = 'A2NWVPWEB100'
        dc, os, product = nutrition_label(hostname)
        assert_equals(dc, 'A2')
        assert_equals(os, 'Windows')
        assert_equals(product, 'Angelo')

    def test_angelo_n1(self):
        hostname = 'N1NWVPWEB063'
        dc, os, product = nutrition_label(hostname)
        assert_equals(dc, 'N1')
        assert_equals(os, 'Windows')
        assert_equals(product, 'Angelo')

    def test_angelo_p3(self):
        hostname = 'P3NWVPWEB082'
        dc, os, product = nutrition_label(hostname)
        assert_equals(dc, 'P3')
        assert_equals(os, 'Windows')
        assert_equals(product, 'Angelo')

    def test_angelo_sg2_called_plesk_why(self):
        hostname = 'SG2NWVPWEB022'
        dc, os, product = nutrition_label(hostname)
        assert_equals(dc, 'SG2')
        assert_equals(os, 'Windows')
        assert_equals(product, 'Plesk')

    def test_vph_n1(self):
        hostname = 'n1plvph2-055'
        dc, os, product = nutrition_label(hostname)
        assert_equals(dc, 'N1')
        assert_equals(os, 'Linux')
        assert_equals(product, 'VPS')

    def test_vph_sg2(self):
        hostname = 'sg2plvph2-116'
        dc, os, product = nutrition_label(hostname)
        assert_equals(dc, 'SG2')
        assert_equals(os, 'Linux')
        assert_equals(product, 'VPS')

    def test_vertigo(self):
        hostname = 'vertigo-86545-primary'
        dc, os, product = nutrition_label(hostname)
        assert_equals(dc, 'vert')
        assert_equals(os, '')
        assert_equals(product, 'Vertigo')

    def test_os_fail(self):
        hostname = 'p3nxhg390c1390'
        dc, os, product = nutrition_label(hostname)
        assert_equals(dc, 'P3')
        assert_equals(os, None)
        assert_equals(product, '4GH')

    def test_vph(self):
        hostname = 'VPHL390c1390'
        dc, os, product = nutrition_label(hostname)
        assert_equals(dc, 'VPH')
        assert_equals(os, '')
        assert_equals(product, 'VPH')
