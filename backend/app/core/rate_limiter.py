import time
from collections import defaultdict

from fastapi import HTTPException, Request


class RateLimiter:
    """
    Simple in-memory rate limiter.
    For production, replace with Redis-based limiter.
    """
    def __init__(self, requests_per_minute: int = 100):
        self.requests_per_minute = requests_per_minute
        self.window_size = 60  # seconds
        self.records = defaultdict(list)  # key: client_ip, value: list of timestamps

    async def __call__(self, request: Request):
        client_ip = request.client.host
        now = time.time()
        # Clean old entries
        self.records[client_ip] = [t for t in self.records[client_ip] if now - t < self.window_size]
        if len(self.records[client_ip]) >= self.requests_per_minute:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        self.records[client_ip].append(now)
        return True
