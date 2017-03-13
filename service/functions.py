import re


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
            date_match_regex = r'(\d+' + delimiter + '\d+' + delimiter + '\d+)'
            match = re.search(date_match_regex, just_date)

            if match.group(1):
                # min string should be something like 1/1/1111, which is 8 characters
                if len(match.group(1)) >= 8:
                    date_list = match.group(1).split(delimiter)
                    # zero pad date so the above date looks like 01/01/1111
                    for slice in range(len(date_list)):
                        date_list[slice] = zero_pad_date_slice(date_list[slice])
                    if len(date_list[0]) == 4:
                        good_date = mongo_date_format.format(date_list[0], date_list[1], date_list[2])
                    elif len(date_list[2]) == 4:
                        good_date = mongo_date_format.format(date_list[2], date_list[0], date_list[1])
    return good_date