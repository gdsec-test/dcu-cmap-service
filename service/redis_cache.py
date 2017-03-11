from redis import Redis


class RedisCache(object):
    def __init__(self, settings):
        self.redis = Redis(settings.REDIS_HOST)
        self.redis_ttl = settings.REDIS_TTL

    def get_value(self, redis_key):
        try:
            redis_value = self.redis.get(redis_key)
        except Exception:
            redis_value = None
        return redis_value

    def set_value(self, redis_key, redis_value):
        self.redis.set(redis_key, redis_value)
        self.redis.expire(redis_key, self.redis_ttl)
