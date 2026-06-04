from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.core.rate_limiter import RateLimiter  # we'll create this later

# Placeholder for future auth
async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    # For now, return None (guest)
    # Later: verify JWT and return user object
    return None

# Simple idempotency key header
def get_idempotency_key(idempotency_key: str = Header(..., alias="Idempotency-Key")):
    return idempotency_key

# Rate limiter dependency (example)
def rate_limit_endpoint(request):
    # Implement rate limiting logic
    pass


# backend/app/api/v1/dependencies.py
from fastapi import Header, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.core.rate_limiter import RateLimiter
from app.core.idempotency import idempotency

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
        token = authorization.split(" ")[1]
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