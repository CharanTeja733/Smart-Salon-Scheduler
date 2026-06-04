from typing import Any, Optional
from app.core.cache import cache

class Idempotency:
    """
    Stores responses for idempotency keys using cache.
    Keys expire after 24 hours.
    """
    TTL_SECONDS = 86400  # 24 hours
    
    @classmethod
    async def get(cls, key: str) -> Optional[Any]:
        return await cache.get(f"idempotency:{key}")
    
    @classmethod
    async def set(cls, key: str, response: Any):
        await cache.set(f"idempotency:{key}", response, ttl_seconds=cls.TTL_SECONDS)
    
    @classmethod
    async def delete(cls, key: str):
        await cache.delete(f"idempotency:{key}")

idempotency = Idempotency()