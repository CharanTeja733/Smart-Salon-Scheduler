from pydantic import BaseModel, Field, validator
from datetime import datetime, date, time, timedelta
from typing import Optional, List, Dict, Any
import re

class Address(BaseModel):
    street: str
    city: str
    state: Optional[str] = None
    postal_code: str
    country: str = "USA"

class OpeningHours(BaseModel):
    monday: str = "closed"
    tuesday: str = "closed"
    wednesday: str = "closed"
    thursday: str = "closed"
    friday: str = "closed"
    saturday: str = "closed"
    sunday: str = "closed"

    @validator('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday')
    def validate_hours(cls, v):
        if v == "closed":
            return v
        pattern = r"^\d{2}:\d{2}-\d{2}:\d{2}$"
        if not re.match(pattern, v):
            raise ValueError(f"Invalid hours format, expected 'HH:MM-HH:MM' or 'closed', got {v}")
        return v

def validate_phone(v: str) -> str:
    """Basic phone validation (E.164 format recommended)"""
    if not re.match(r"^\+[1-9]\d{1,14}$", v):
        raise ValueError("Phone must be in E.164 format (e.g., +1234567890)")
    return v

def validate_email(v: str) -> str:
    if v and "@" not in v:
        raise ValueError("Invalid email address")
    return v

def validate_future_datetime(v: datetime, min_hours: int = 1, max_days: int = 90) -> datetime:
    now = datetime.utcnow()
    if v < now + timedelta(hours=min_hours):
        raise ValueError(f"Booking must be at least {min_hours} hour(s) in advance")
    if v > now + timedelta(days=max_days):
        raise ValueError(f"Cannot book more than {max_days} days in advance")
    return v