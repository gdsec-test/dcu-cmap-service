from csetutils.flask.logging import get_logging
from redis import Redis


class RedisCache(object):
    def __init__(self, settings):
        self._logger = get_logging()
        try:
            self.redis = Redis(settings.REDIS)
            self.redis_ttl = settings.REDIS_TTL
        except Exception as e:
            self._logger.fatal('Error in creating redis connection: {}'.format(e))

    def get(self, redis_key):
        try:
            redis_value = self.redis.get(redis_key)
        except Exception:
            redis_value = None
        return redis_value

    def set(self, redis_key, redis_value):
        try:
            self.redis.set(redis_key, redis_value)
            self.redis.expire(redis_key, self.redis_ttl)
        except Exception as e:
            self._logger.error('Error in setting the redis value for {} : {}'.format(redis_key, e))
