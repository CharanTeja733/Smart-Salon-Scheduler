# backend/app/api/v1/dependencies.py
from typing import Optional

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.rate_limiter import RateLimiter
from app.database import get_db


# ============ IDEMPOTENCY ============
async def get_idempotency_key(idempotency_key: str = Header(..., alias="Idempotency-Key")):
    return idempotency_key

# ============ RATE LIMITING ============
def rate_limiter(requests_per_minute: int = 100):
    """
    Factory to create a rate limiter dependency with specific limit.
    Usage: rate_limit: bool = Depends(rate_limiter(50))
    """
    return RateLimiter(requests_per_minute)

# ============ AUTH (placeholder for future) ============
async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Placeholder for authentication.
    For now returns None (guest user).
    Later: decode JWT, fetch user from DB.
    """
    if authorization and authorization.startswith("Bearer "):
        #token = authorization.split(" ")[1]
        # TODO: decode token and return user
        pass
    return None

# ============ COMMON DEPENDENCIES ============
async def get_guest_or_user(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Returns user if authenticated, else None (guest).
    """
    return current_user
