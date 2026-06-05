from datetime import date, datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator

from .common import validate_email, validate_phone


class PractitionerBrief(BaseModel):
    id: int
    name: str
    specialty: Optional[str] = None
    rating: float = 0.0
    photo_url: Optional[str] = None

class PractitionerBase(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    specialty: Optional[str] = None
    experience_years: int = Field(0, ge=0, le=50)
    bio: Optional[str] = None
    photo_url: Optional[str] = None
    base_price: float = Field(50.0, ge=0)
    service_prices: Dict[str, float] = {}
    specializations: List[str] = []
    lunch_break_start: Optional[str] = None  # "13:00:00"
    lunch_break_end: Optional[str] = None
    off_days: List[str] = []
    is_active: bool = True

    @validator('email')
    def validate_email(cls, v):
        return validate_email(v)

    @validator('phone')
    def validate_phone(cls, v):
        if v:
            return validate_phone(v)
        return v

class Practitioner(PractitionerBase):
    id: int
    salon_id: int
    rating: float = 0.0
    total_reviews: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PractitionerResponse(PractitionerBase):
    id: int
    salon_name: str
    rating: float
    total_reviews: int
    reviews: Optional[List['ReviewBrief']] = None

    class Config:
        from_attributes = True

class PractitionerBrief(PractitionerBrief):
    pass

class AvailabilityRequest(BaseModel):
    date: date
    duration: int = Field(30, ge=30, le=120, multiple_of=30)

class AvailabilityResponse(BaseModel):
    practitioner_id: int
    date: date
    available_slots: List[datetime]  # UTC datetimes

class DeactivateRequest(BaseModel):
    reason: str

class UnavailableRequest(BaseModel):
    start_date: date
    end_date: date
    reason_code: str  # 'sick', 'emergency', 'other', 'private'
    reason_text: Optional[str] = None


# Forward reference for ReviewBrief
from .review import ReviewBrief

PractitionerResponse.model_rebuild()
