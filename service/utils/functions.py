import logging
import re

import tld

_logger = logging.getLogger(__name__)


# Functions to convert random date strings into a mongo date format
def zero_pad_date_slice(date_slice):
    if len(date_slice) == 1:
        date_slice = '0{}'.format(date_slice)
    return date_slice


def convert_string_date_to_mongo_format(old_date):
    good_date = old_date
    mongo_date_format = '{}-{}-{}'

    if good_date is not None:
        # Get rid of time, if a datetime
        date_list = old_date.split(' ')
        just_date = date_list[0]

        delimiter = None

        if '/' in just_date:
            delimiter = '/'
        elif '-' in just_date:
            delimiter = '-'

        if delimiter is not None:
            # We assume only dates yyyy/mm/dd or mm/dd/yyyy, using a delimiter of / or -
            date_match_regex = r'(\d+' + delimiter + r'\d+' + delimiter + r'\d+)'
            match = re.search(date_match_regex, just_date)

            if match.group(1):
                # min string should be something like 1/1/1111, which is 8 characters
                if len(match.group(1)) >= 8:
                    date_list = match.group(1).split(delimiter)
                    # zero pad date so the above date looks like 01/01/1111
                    for dl_slice in range(len(date_list)):
                        date_list[dl_slice] = zero_pad_date_slice(date_list[dl_slice])
                    if len(date_list[0]) == 4:
                        good_date = mongo_date_format.format(date_list[0], date_list[1], date_list[2])
                    elif len(date_list[2]) == 4:
                        good_date = mongo_date_format.format(date_list[2], date_list[0], date_list[1])
    return good_date


def return_populated_dictionary(the_dict, the_keys):
    if the_dict is None:
        the_dict = {}
    for key in the_keys:
        the_dict[key] = the_dict.get(key)
    return the_dict


def return_expected_dict_due_to_exception(the_container, the_keys):
    # If exception occurred before query_value had completed assignment, set keys to None
    if type(the_container) == list:
        if len(the_container) == 0:
            new_dict = return_populated_dictionary(None, the_keys)
            return [new_dict]
        for slice_element in range(len(the_container)):
            if type(the_container[slice_element]) == dict:
                the_container[slice_element] = return_populated_dictionary(the_container[slice_element])
        return the_container
    elif type(the_container) == dict or the_container is None:
        return return_populated_dictionary(the_container, the_keys)
    # We werent provided a list or dictionary, so just return what we were provided, as we dont know how to handle it
    return the_container


def get_fld_by_domain_name(domain_name):
    """
    Returns the free level domain given a domain name or subdomain name.
    ie: example.com will return example.com AND subdomain.example.co.uk will return example.co.uk
    :param domain_name: string representing domain or subdomain
    :return: string representing the free level domain
    """
    if isinstance(domain_name, bytes):
        domain_name = domain_name.decode()

    # In the event that we were provided a sub-domain name as opposed to a tld
    if domain_name:
        try:
            # TLD expects to work on a domain name starting with http://
            domain_name = 'http://' + domain_name if domain_name[:7] != 'http://' else domain_name
            fld = tld.get_tld(domain_name, as_object=True).fld
        except Exception as e:
            # Try again
            try:
                _logger.warning('Error updating TLD file for domain {} : {}. Retrying'.format(domain_name, e))
                tld.update_tld_names()

                # Clearing out the global tld_names variable from tld to force it to update
                tld.utils.tld_names = {}
                fld = tld.get_tld(domain_name).fld
            except Exception as e:
                _logger.warning('Retry Error updating TLD file for domain {} : {}.'.format(domain_name, e))
                return None

        return fld
