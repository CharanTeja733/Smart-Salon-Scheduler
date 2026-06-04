SERVICE_TYPES = ["haircut", "color", "blowout", "nails", "makeup", "waxing", "facial"]

DURATION_OPTIONS = [30, 60, 90, 120]

BOOKING_RULES = {
    "min_advance_hours": 1,
    "max_advance_days": 90,
    "hold_minutes": 10,
    "deposit_percentage": 20,
    "slot_duration_minutes": 30,
}

REFUND_POLICY = [
    {"hours_before": 24, "refund_percentage": 100},
    {"hours_before": 2, "refund_percentage": 50},
    {"hours_before": 0, "refund_percentage": 0},
]

DAYS_OF_WEEK = [
    "monday", "tuesday", "wednesday", "thursday",
    "friday", "saturday", "sunday"
]

MAX_RADIUS_METERS = 50000
DEFAULT_RADIUS_METERS = 5000
DEFAULT_SEARCH_LIMIT = 20
MAX_SEARCH_LIMIT = 100

STATUS_APPOINTMENT = ["pending", "confirmed", "completed", "cancelled", "no_show"]
STATUS_WAITLIST = ["active", "notified", "booked", "expired"]