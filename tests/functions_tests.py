from nose.tools import assert_equals
import service.functions


class TestZeroPadDateSlice:
    def __init__(self):
        pass

    def test_zero_pad_date_slice_ok(self):
        date_slice = '05'
        response = service.functions.zero_pad_date_slice(date_slice)
        assert_equals(response, '05')

    def test_zero_pad_date_slice_fixed(self):
        date_slice = '5'
        response = service.functions.zero_pad_date_slice(date_slice)
        assert_equals(response, '05')


class TestConvertStringDateToMongoFormat:
    def __init__(self):
        pass

    def test_convert_string_date_to_mongo_format_ok(self):
        old_date = '2016-05-18'
        response = service.functions.convert_string_date_to_mongo_format(old_date)
        assert_equals(response, '2016-05-18')

    def test_convert_string_date_to_mongo_format_fixed1(self):
        old_date = '05-18-2016'
        response = service.functions.convert_string_date_to_mongo_format(old_date)
        assert_equals(response, '2016-05-18')

    def test_convert_string_date_to_mongo_format_fixed2(self):
        old_date = '2016/05/18'
        response = service.functions.convert_string_date_to_mongo_format(old_date)
        assert_equals(response, '2016-05-18')

    def test_return_expected_dict_due_to_exception_list(self):
        the_container = ['one', 'two', 3]
        the_keys = [1, 2, 'three']
        response = service.functions.return_expected_dict_due_to_exception(the_container, the_keys)
        assert_equals(response, ['one', 'two', 3])

    def test_return_expected_dict_due_to_exception_empty_list(self):
        the_container = []
        the_keys = ''
        response = service.functions.return_expected_dict_due_to_exception(the_container, the_keys)
        assert_equals(response, [{}])

    def test_return_expected_dict_due_to_exception_empty_dict(self):
        the_container = {}
        the_keys = ''
        response = service.functions.return_expected_dict_due_to_exception(the_container, the_keys)
        assert_equals(response, {})


class TestGetTLDbyDomainName:
    def __init__(self):
        pass

    def test_get_tld_by_domain_name_protocol(self):
        domain_name = 'http://this.should.pass.com'
        response = service.functions.get_tld_by_domain_name(domain_name)
        assert_equals(response, 'pass.com')

    def test_get_tld_by_domain_name_no_protocol(self):
        domain_name = 'another.test.com'
        response = service.functions.get_tld_by_domain_name(domain_name)
        assert_equals(response, 'test.com')

    def test_get_tld_by_domain_name_bad(self):
        domain_name = 'fake.tld.ccc'
        response = service.functions.get_tld_by_domain_name(domain_name)
        assert_equals(response, None)
