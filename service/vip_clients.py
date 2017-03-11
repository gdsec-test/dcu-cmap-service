import logging
from pymongo import MongoClient


class VipClients(object):

    REDIS_KEY = 'blacklist' # The key name we will use in redis
    MONGO_INSTANCE_KEY = 'entity' # The key name used in the mongodb blacklist record

    def __init__(self, settings, redis_obj):
        client = MongoClient(settings.DBURL)
        db = client[settings.DB]
        self._collection = db[settings.COLLECTION]
        self._redis = redis_obj

    def query_entity(self, entity_id):
        try:
            redis_key = '{}-blacklist_status'.format(entity_id)
            blacklist_status = self._redis.get_value(redis_key)
            if blacklist_status is None:
                result = self._collection.find_one({self.MONGO_INSTANCE_KEY: str(entity_id)})
                # If the shopper id exists, they are VIP
                blacklist_status = True
                if result is None:
                    blacklist_status = False
                self._redis.set_value(redis_key, blacklist_status)
            return blacklist_status if isinstance(blacklist_status, bool) else 'True' in blacklist_status
        except Exception as e:
            logging.warning("Error in getting the blacklist status for %s : %s", entity_id, e.message)
