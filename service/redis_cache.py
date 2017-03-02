from redis import Redis


class RedisCache(object):
    def __init__(self, redis_host='redis', redis_ttl=86400):
        self.redis = Redis(redis_host)
        self.redis_ttl = redis_ttl

    def get_value(self, redis_key):
        try:
            redis_value = self.redis.get(redis_key)
        except Exception:
            redis_value = None
        return redis_value

    def set_value(self, redis_key, redis_value):
        self.redis.set(redis_key, redis_value)
        self.redis.expire(redis_key, self.redis_ttl)
