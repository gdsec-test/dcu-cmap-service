import logging

from pymongo import MongoClient


class VipClients(object):
    MONGO_INSTANCE_KEY = 'entity'  # The key name used in the mongodb blacklist record

    def __init__(self, settings, redis_obj):
        self._logger = logging.getLogger(__name__)
        client = MongoClient(settings.DBURL)
        db = client[settings.DB]
        self._collection = db[settings.COLLECTION]
        self._redis = redis_obj

    def query_entity(self, entity_id):
        try:
            redis_record_key = u'{}-blacklist_status'.format(entity_id)
            blacklist_status = self._redis.get_value(redis_record_key)
            if blacklist_status is None:
                result = self._collection.find_one({self.MONGO_INSTANCE_KEY: entity_id})
                # If the shopper id exists, they are VIP
                blacklist_status = True
                if result is None:
                    blacklist_status = False
                self._redis.set_value(redis_record_key, blacklist_status)
                # Works regardless if blacklist_status is a bool or a string
            return blacklist_status if isinstance(blacklist_status, bool) else 'True' in blacklist_status
        except Exception as e:
            self._logger.error("Error in getting the blacklist status for %s : %s", entity_id, e.message)
            # Error on the safe side.  If we cant get a definitive answer from the db, assume they are blacklist
            return True
