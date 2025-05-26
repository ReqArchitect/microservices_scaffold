import os
import redis

def get_redis():
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    return redis.Redis.from_url(redis_url, decode_responses=True)

def cache_set(key, value, ex=60):
    r = get_redis()
    r.set(key, value, ex=ex)

def cache_get(key):
    r = get_redis()
    return r.get(key) 