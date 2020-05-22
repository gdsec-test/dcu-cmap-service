import json
import logging

import requests
from requests.models import Response

import service.utils.functions


class ShopperAPI(object):
    _url = 'https://shopper.api.int.godaddy.com/v1/shoppers/{}'
    _created_key = 'createdAt'  # Key into the Shopper Response for shopper create date.
    _params = {'includes': 'contact,preference', 'auditClientIp': 'cmap.service.int.godaddy.com'}

    def __init__(self, settings):
        self._logger = logging.getLogger(__name__)
        self._cert = (settings.CMAP_API_CERT, settings.CMAP_API_KEY)

    def get_shopper_by_shopper_id(self, shopper_id, fields):
        """
        Given a ShopperID, retrieve additional information about that shopper, such as the shopper creation date,
        their email address, etc.
        :param shopper_id:
        :param fields:
        :return:
        """
        shopper_data = {}

        try:
            if not shopper_id:
                raise ValueError('Blank shopper id was provided')

            self._logger.info('Retrieving additional info for shopper {} from Shopper API'.format(shopper_id))
            req_val = requests.get(self._url.format(shopper_id), params=self._params, cert=self._cert)

            if type(req_val) is not Response:
                raise ValueError('Response from cmap proxy was garbled')
            if req_val.status_code == 502:
                raise ValueError('Response from cmap proxy: Bad Gateway')
            if req_val.status_code != 200:
                raise ValueError('Response from cmap proxy: {}'.format(req_val.content))

            shopper_data = json.loads(req_val.text)

            if self._created_key in shopper_data:
                # Change the format of the date string
                shopper_data[self._created_key] = service.utils.functions.convert_string_date_to_mongo_format(shopper_data.get(self._created_key))

            return dict(shopper_first_name=shopper_data.get('contact', {}).get('nameFirst'),
                        shopper_last_name=shopper_data.get('contact', {}).get('nameLast'),
                        shopper_phone_work=shopper_data.get('contact', {}).get('phoneWork'),
                        shopper_phone_work_ext=shopper_data.get('contact', {}).get('phoneWorkExtension'),
                        shopper_phone_home=shopper_data.get('contact', {}).get('phoneHome'),
                        shopper_phone_mobile=shopper_data.get('contact', {}).get('phoneMobile'),
                        shopper_email=shopper_data.get('email'),
                        shopper_address_1=shopper_data.get('contact', {}).get('address', {}).get('address1'),
                        shopper_address_2=shopper_data.get('contact', {}).get('address', {}).get('address2'),
                        shopper_city=shopper_data.get('contact', {}).get('address', {}).get('city'),
                        shopper_state=shopper_data.get('contact', {}).get('address', {}).get('state'),
                        shopper_postal_code=shopper_data.get('contact', {}).get('address', {}).get('postalCode'),
                        shopper_country=shopper_data.get('contact', {}).get('address', {}).get('country'),
                        shopper_create_date=shopper_data.get('createdAt'))

        except Exception as e:
            self._logger.error('Error in getting the shopper info for {} : {}'.format(shopper_id, e))
            shopper_data = service.utils.functions.return_expected_dict_due_to_exception(shopper_data, fields)
        return shopper_data
