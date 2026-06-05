from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, validator

from .common import validate_future_datetime, validate_phone


class ServiceType(str, Enum):
    HAIRCUT = "haircut"
    COLOR = "color"
    BLOWOUT = "blowout"
    NAILS = "nails"
    MAKEUP = "makeup"
    WAXING = "waxing"
    FACIAL = "facial"

class AppointmentStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class CustomerInfo(BaseModel):
    phone: str
    name: str
    email: Optional[str] = None
    notes: Optional[str] = None

    @validator('phone')
    def validate_phone(cls, v):
        return validate_phone(v)

class BookingRequest(BaseModel):
    practitioner_id: int
    start_time: datetime
    service_type: ServiceType
    duration_minutes: int = Field(30, ge=30, le=120, multiple_of=30)
    customer: CustomerInfo

    @validator('start_time')
    def validate_start_time(cls, v):
        # Use defaults from config later, but for schema we use 1h min, 90d max
        return validate_future_datetime(v, min_hours=1, max_days=90)

class BookingResponse(BaseModel):
    appointment_id: int
    status: AppointmentStatus
    price: float
    deposit_amount: float
    client_secret: str
    hold_expires_at: datetime

class ConfirmRequest(BaseModel):
    payment_intent_id: str

class CancelRequest(BaseModel):
    reason: Optional[str] = None

class CancelResponse(BaseModel):
    appointment_id: int
    status: AppointmentStatus
    refund_amount: float
    cancellation_fee: float
    policy_applied: str

class RescheduleRequest(BaseModel):
    new_start_time: datetime

    @validator('new_start_time')
    def validate_new_time(cls, v):
        # Reschedule must be at least 2 hours notice
        now = datetime.utcnow()
        if v < now + timedelta(hours=2):
            raise ValueError("Rescheduling requires at least 2 hours notice")
        if v > now + timedelta(days=90):
            raise ValueError("Cannot reschedule more than 90 days in advance")
        if v.minute not in [0, 30]:
            raise ValueError("Appointments must start at :00 or :30")
        return v

class AppointmentStatusResponse(BaseModel):
    id: int
    practitioner_id: int
    practitioner_name: str
    salon_name: str
    start_time: datetime
    status: AppointmentStatus
    price: float
    deposit_paid: bool
