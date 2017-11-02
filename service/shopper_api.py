import json
import logging
import functions

from requests import sessions
from requests.models import Response
from functions import return_expected_dict_due_to_exception


class ShopperAPI(object):
    _URL = 'https://shopper.cmap.proxy.int.godaddy.com/v1/shoppers'
    DATE_STRING = 'createdAt'
    ENCODING = 'utf8'
    REDIS_DATA_KEY = 'result'

    def __init__(self, settings, redis_obj):
        self._logger = logging.getLogger(__name__)
        self._redis = redis_obj
        self._auth = (settings.CMAP_PROXY_USER, settings.CMAP_PROXY_PASS)
        self._cert = (settings.CMAP_PROXY_CERT, settings.CMAP_PROXY_KEY)
        self._params = {'includes': 'contact,preference'}

    def get_shopper_by_shopper_id(self, shopper_id, fields):
        """
        Return fields by shopper id
        :param shopper_id:
        :param fields:
        :return:
        """
        shopper_data = {}
        try:
            if shopper_id is None or shopper_id == '':
                raise ValueError('Blank shopper id was provided')
            redis_record_key = '{}-shopper_info_by_id'.format(shopper_id)
            shopper_data = self._redis.get_value(redis_record_key)
            if shopper_data is None:
                url = self._URL + "/" + shopper_id + "?auditClientIp=cmap.proxy.int.godaddy.com"
                # Added error handling due to Bad Gateway errors observed
                with sessions.Session() as session:
                    req_val = session.get(url, params=self._params, auth=self._auth, cert=self._cert)

                    if type(req_val) is not Response:
                        raise ValueError("Response from cmap proxy was garbled")
                    if req_val.status_code == 502:
                        raise ValueError("Response from cmap proxy: Bad Gateway")
                    if req_val.status_code != 200:
                        raise ValueError("Response from cmap proxy: %s" % req_val.content)

                    shopper_data = json.loads(
                        session.get(url, params=self._params, auth=self._auth, cert=self._cert).text)
                if self.DATE_STRING in shopper_data:
                    # Change the format of the date string
                    shopper_data[self.DATE_STRING] = functions.convert_string_date_to_mongo_format(
                        shopper_data.get(self.DATE_STRING))
                self._redis.set_value(redis_record_key, json.dumps({self.REDIS_DATA_KEY: shopper_data}))
            else:
                shopper_data = json.loads(shopper_data).get(self.REDIS_DATA_KEY)
            return dict(shopper_first_name=shopper_data.get('contact', {}).get('nameFirst'),
                        shopper_email=shopper_data.get('email'),
                        shopper_create_date=shopper_data.get('createdAt'))
        except Exception as e:
            self._logger.error("Error in getting the shopper info for %s : %s", shopper_id, e.message)
            # If exception occurred before query_value had completed assignment, set keys to None
            shopper_data = return_expected_dict_due_to_exception(shopper_data, fields)
        return shopper_data
