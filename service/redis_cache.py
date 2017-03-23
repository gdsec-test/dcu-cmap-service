import logging
from redis import Redis


class RedisCache(object):
    def __init__(self, settings):
        try:
            self.redis = Redis(settings.REDIS)
            self.redis_ttl = settings.REDIS_TTL
        except Exception as e:
            logging.fatal("Error in creating redis connection: %s", e.message)

    def get_value(self, redis_key):
        try:
            redis_value = self.redis.get(redis_key)
        except Exception:
            redis_value = None
        return redis_value

    def set_value(self, redis_key, redis_value):
        try:
            self.redis.set(redis_key, redis_value)
            self.redis.expire(redis_key, self.redis_ttl)
        except Exception as e:
            logging.error("Error in setting the redis value for %s : %s", redis_key, e.message)
