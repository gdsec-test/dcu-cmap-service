from csetutils.flask.logging import get_logging
from redis import Redis


class RedisCache(object):
    def __init__(self, host, ttl):
        self._logger = get_logging()
        try:
            self.redis = Redis(host)
            self.redis_ttl = ttl
        except Exception as e:
            self._logger.fatal('Error in creating redis connection: {}'.format(e))

    def get(self, redis_key):
        try:
            redis_value = self.redis.get(redis_key)
        except Exception:
            redis_value = None
        return redis_value

    def set(self, redis_key, redis_value, ttl=None):
        if ttl is None:
            ttl = self.redis_ttl
        try:
            self.redis.set(redis_key, redis_value)
            self.redis.expire(redis_key, ttl)
        except Exception as e:
            self._logger.error('Error in setting the redis value for {} : {}'.format(redis_key, e))
