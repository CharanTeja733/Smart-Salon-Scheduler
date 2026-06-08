from datetime import datetime
from typing import Optional

from pydantic import BaseModel, validator

from .common import validate_phone


class WaitlistCreate(BaseModel):
    practitioner_id: int
    customer_phone: str
    preferred_date_start: Optional[datetime] = None
    preferred_date_end: Optional[datetime] = None
    preferred_service_type: Optional[str] = None

    @validator('customer_phone')
    def validate_phone(cls, v):
        return validate_phone(v)

    @validator('preferred_date_end')
    def date_range(cls, v, values):
        if v and values.get('preferred_date_start') and v < values['preferred_date_start']:
            raise ValueError("end date must be after start date")
        return v

class WaitlistResponse(BaseModel):
    waitlist_id: int
    position: int
    estimated_wait_days: Optional[int] = None

class WaitlistStatusResponse(BaseModel):
    id: int
    status: str
    position: int
    notified_at: Optional[datetime] = None
    practitioner_id: int
    practitioner_name: str
    preferred_date_start: Optional[datetime] = None
    preferred_date_end: Optional[datetime] = None
    preferred_service_type: Optional[str] = None
