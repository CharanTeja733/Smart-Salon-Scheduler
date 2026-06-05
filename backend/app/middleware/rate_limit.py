import time
from collections import defaultdict
from typing import Optional

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.cache import cache


class GlobalRateLimitMiddleware(BaseHTTPMiddleware):
    """
    Global rate limiter that applies to all requests.
    Uses Redis if available, otherwise in‑memory dict.
    Limits: requests per minute per IP.
    """
    def __init__(self, app, requests_per_minute: int = 100, skip_paths: Optional[list] = None):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.skip_paths = skip_paths or ["/health", "/docs", "/openapi.json", "/redoc"]
        self.window_size = 60  # seconds
        self.memory_store = defaultdict(list)  # fallback when Redis down

    async def dispatch(self, request: Request, call_next):
        # Skip certain paths
        if request.url.path in self.skip_paths:
            return await call_next(request)

        client_ip = request.client.host
        now = time.time()

        # Try Redis first
        try:
            key = f"rate_limit:global:{client_ip}"
            requests = await cache.get(key)
            if requests is None:
                await cache.set(key, 1, ttl_seconds=self.window_size)
            else:
                if requests >= self.requests_per_minute:
                    raise HTTPException(status_code=429, detail="Rate limit exceeded")
                await cache.set(key, requests + 1, ttl_seconds=self.window_size)
        except Exception:
            # Fallback to in‑memory
            self.memory_store[client_ip] = [t for t in self.memory_store[client_ip] if now - t < self.window_size]
            if len(self.memory_store[client_ip]) >= self.requests_per_minute:
                raise HTTPException(status_code=429, detail="Rate limit exceeded") from None
            self.memory_store[client_ip].append(now)

        return await call_next(request)
