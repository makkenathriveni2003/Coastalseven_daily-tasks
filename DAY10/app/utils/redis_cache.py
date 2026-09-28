import json

from app.redis_client import safe_delete, safe_get, safe_set


def set_cache(key: str, value):
    payload = json.dumps(value)
    return safe_set(key, payload)


def get_cache(key: str):
    data = safe_get(key)
    if data is None:
        return None
    try:
        return json.loads(data)
    except (TypeError, ValueError):
        return None


def delete_cache(key: str):
    return safe_delete(key)
