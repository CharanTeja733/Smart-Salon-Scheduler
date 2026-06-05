from datetime import date, datetime, time, timedelta
from typing import List, Optional


def get_utc_now() -> datetime:
    """Return current UTC datetime."""
    return datetime.utcnow()

def parse_date(date_str: str) -> Optional[date]:
    """Parse YYYY-MM-DD to date object."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None

def parse_datetime(dt_str: str) -> Optional[datetime]:
    """Parse ISO datetime string to UTC datetime."""
    try:
        # Handle with and without timezone
        if dt_str.endswith('Z'):
            dt_str = dt_str[:-1] + '+00:00'
        return datetime.fromisoformat(dt_str)
    except ValueError:
        return None

def format_datetime_iso(dt: datetime) -> str:
    """Convert datetime to ISO format string with Zulu timezone."""
    return dt.isoformat() + 'Z'

def get_weekday_from_date(target_date: date) -> str:
    """Return lowercase weekday name (e.g., 'monday')."""
    return target_date.strftime("%A").lower()

def add_days(dt: datetime, days: int) -> datetime:
    """Add days to datetime."""
    return dt + timedelta(days=days)

def subtract_hours(dt: datetime, hours: int) -> datetime:
    """Subtract hours from datetime."""
    return dt - timedelta(hours=hours)

def is_valid_future_slot(start_time: datetime, min_hours: int = 1, max_days: int = 90) -> bool:
    """Check if booking time is within allowed window."""
    now = get_utc_now()
    if start_time < now + timedelta(hours=min_hours):
        return False
    if start_time > now + timedelta(days=max_days):
        return False
    return True

def generate_time_slots(start_hour: int = 9, end_hour: int = 18, slot_minutes: int = 30) -> List[time]:
    """Generate list of time objects for a day (e.g., 09:00, 09:30...)."""
    slots = []
    current = time(start_hour, 0)
    end = time(end_hour, 0)
    while current < end:
        slots.append(current)
        # Add slot_minutes
        minutes = current.minute + slot_minutes
        hour = current.hour + minutes // 60
        minute = minutes % 60
        if hour >= end_hour:
            break
        current = time(hour, minute)
    return slots
