import json
from typing import Any, Optional

import redis

from app.config import settings


class Cache:
    """Simple cache wrapper. Uses Redis if available, else falls back to in-memory dict."""

    _memory_store = {}
    _redis_client = None

    def __init__(self):
        try:
            self._redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
            self._redis_client.ping()
            self._use_redis = True
        except Exception:
            self._use_redis = False

    async def get(self, key: str) -> Optional[Any]:
        if self._use_redis:
            val = self._redis_client.get(key)
            return json.loads(val) if val else None
        else:
            return self._memory_store.get(key)

    async def set(self, key: str, value: Any, ttl_seconds: int = 60):
        if self._use_redis:
            self._redis_client.setex(key, ttl_seconds, json.dumps(value))
        else:
            self._memory_store[key] = value

    async def delete(self, key: str):
        if self._use_redis:
            self._redis_client.delete(key)
        else:
            self._memory_store.pop(key, None)

    async def exists(self, key: str) -> bool:
        if self._use_redis:
            return self._redis_client.exists(key) > 0
        else:
            return key in self._memory_store

cache = Cache()
