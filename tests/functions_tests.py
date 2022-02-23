from nose.tools import assert_equals, assert_false, assert_is_none, assert_true

import service.utils.functions


class TestZeroPadDateSlice:
    def test_zero_pad_date_slice_ok(self):
        date_slice = '05'
        response = service.utils.functions.zero_pad_date_slice(date_slice)
        assert_equals(response, '05')

    def test_zero_pad_date_slice_fixed(self):
        date_slice = '5'
        response = service.utils.functions.zero_pad_date_slice(date_slice)
        assert_equals(response, '05')


class TestConvertStringDateToMongoFormat:
    def test_convert_string_date_to_mongo_format_ok(self):
        old_date = '2016-05-28'
        response = service.utils.functions.convert_string_date_to_mongo_format(old_date)
        assert_equals(response, '2016-05-28')

    def test_convert_string_date_to_mongo_format_fixed1(self):
        old_date = '05-28-2016'
        response = service.utils.functions.convert_string_date_to_mongo_format(old_date)
        assert_equals(response, '2016-05-28')

    def test_convert_string_date_to_mongo_format_fixed2(self):
        old_date = '2016/05/28'
        response = service.utils.functions.convert_string_date_to_mongo_format(old_date)
        assert_equals(response, '2016-05-28')

    def test_return_expected_dict_due_to_exception_list(self):
        the_container = ['one', 'two', 3]
        the_keys = [1, 2, 'three']
        response = service.utils.functions.return_expected_dict_due_to_exception(the_container, the_keys)
        assert_equals(response, ['one', 'two', 3])

    def test_return_expected_dict_due_to_exception_empty_list(self):
        the_container = []
        the_keys = ''
        response = service.utils.functions.return_expected_dict_due_to_exception(the_container, the_keys)
        assert_equals(response, [{}])

    def test_return_expected_dict_due_to_exception_empty_dict(self):
        the_container = {}
        the_keys = ''
        response = service.utils.functions.return_expected_dict_due_to_exception(the_container, the_keys)
        assert_equals(response, {})


class TestGetTLDbyDomainName:
    def test_get_tld_by_domain_name_protocol(self):
        domain_name = 'http://this.should.pass.com'
        response = service.utils.functions.get_fld_by_domain_name(domain_name)
        assert_equals(response, 'pass.com')

    def test_get_tld_by_domain_name_no_protocol(self):
        domain_name = 'this.should.pass.com'
        response = service.utils.functions.get_fld_by_domain_name(domain_name)
        assert_equals(response, 'pass.com')

    def test_get_tld_by_domain_name_bad(self):
        domain_name = 'fake.tld.ccc'
        response = service.utils.functions.get_fld_by_domain_name(domain_name)
        assert_is_none(response)


class TestIpIsParked:
    def test_ip_is_parked_gd(self):
        assert_true(service.utils.functions.ip_is_parked('34.102.136.180'))

    def test_ip_is_parked_reseller(self):
        assert_true(service.utils.functions.ip_is_parked('34.98.99.30'))

    def test_ip_is_parked_not(self):
        assert_false(service.utils.functions.ip_is_parked('76.76.21.21'))


class TestConvertStrToNone:
    def test_convert_str_to_none(self):
        test_dict = {"key1": "None",
                     "list_key": ["valid str", "None"],
                     "dict_key": {"blacklist": "valid str", "portfolioType": "None"}}
        expected_dict = {"key1": None,
                         "list_key": ["valid str", None],
                         "dict_key": {"blacklist": "valid str", "portfolioType": None}}
        assert_equals(service.utils.functions.convert_str_to_none(test_dict), expected_dict)
