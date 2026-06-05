import re
from typing import Optional


def validate_phone(phone: str) -> bool:
    """
    Validate phone number in E.164 format.
    e.g., +1234567890 (1-15 digits after '+')
    """
    pattern = r'^\+\d{1,15}$'
    return bool(re.match(pattern, phone))

def validate_email(email: Optional[str]) -> bool:
    """Basic email validation."""
    if not email:
        return True  # email is optional
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_price(price: float) -> bool:
    """Price must be >= 0."""
    return price >= 0

def validate_rating(rating: float) -> bool:
    """Rating must be between 0 and 5."""
    return 0 <= rating <= 5

def validate_service_type(service_type: str, allowed_types: list) -> bool:
    """Check if service type is allowed."""
    return service_type in allowed_types

def validate_duration(duration: int, allowed_durations: Optional[list] = None) -> bool:
    """Check if duration is allowed (30,60,90,120)."""
    allowed = allowed_durations or [30, 60, 90, 120]
    return duration in allowed

def validate_opening_hours(hours_dict: dict) -> bool:
    """
    Validate opening hours format: {"monday": "09:00-18:00", ...}
    """
    for _day, hours in hours_dict.items():
        if hours == "closed":
            continue
        if not re.match(r'^\d{2}:\d{2}-\d{2}:\d{2}$', hours):
            return False
    return True
