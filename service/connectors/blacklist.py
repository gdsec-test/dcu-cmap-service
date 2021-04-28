from dcustructuredloggingflask.flasklogger import get_logging
from pymongo import MongoClient


class VipClients(object):
    _blacklist_mongo_key = 'entity'  # The key used in the mongodb blacklist record

    def __init__(self, settings, redis_obj):
        self._logger = get_logging()
        client = MongoClient(settings.DBURL)
        db = client[settings.DB]
        self._collection = db[settings.COLLECTION]
        self._redis = redis_obj

    def is_blacklisted(self, entity_id):
        """
        Given an entity ID such as a domain name or a shopperID, check whether or not a blacklist entry exists
        in Mongo for that entity. If we encounter an error, assume all entries are blacklisted.
        :param entity_id:
        :return:
        """
        redis_record_key = '{}-blacklist_status'.format(entity_id)

        try:
            blacklist_status = self._redis.get(redis_record_key)
            if blacklist_status is None:
                result = self._collection.find_one({self._blacklist_mongo_key: entity_id})

                # If the shopper id exists in the blacklist collection, they are VIP
                blacklist_status = False if result is None else True

                self._redis.set(redis_record_key, str(blacklist_status))
                # Works regardless if blacklist_status is a bool or a string
            else:
                blacklist_status = blacklist_status.decode()
            return blacklist_status if isinstance(blacklist_status, bool) else 'True' in blacklist_status
        except Exception as e:
            self._logger.error('Error in getting the blacklist status for {} : {}'.format(entity_id, e))
            # Error on the safe side.  If we cant get a definitive answer from the db, assume they are blacklist
            return True
