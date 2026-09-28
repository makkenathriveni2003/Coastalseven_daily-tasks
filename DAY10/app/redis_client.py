import redis
from redis.exceptions import RedisError

from app.config import REDIS_URL

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
_FALLBACK_STORE: dict[str, str] = {}


def get_redis():
    return redis_client


def safe_get(key: str):
    try:
        return redis_client.get(key)
    except RedisError:
        return _FALLBACK_STORE.get(key)


def safe_set(key: str, value, *args, **kwargs):
    try:
        return redis_client.set(key, value, *args, **kwargs)
    except RedisError:
        _FALLBACK_STORE[key] = value
        return True


def safe_delete(*keys):
    try:
        return redis_client.delete(*keys)
    except RedisError:
        for key in keys:
            _FALLBACK_STORE.pop(key, None)
        return 1
