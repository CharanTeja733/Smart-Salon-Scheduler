from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from .common import validate_phone, validate_email

class CustomerBase(BaseModel):
    phone: str
    name: str
    email: Optional[str] = None
    preferred_stylist_id: Optional[int] = None
    preferred_service_types: List[str] = []

    @validator('phone')
    def validate_phone(cls, v):
        return validate_phone(v)

    @validator('email')
    def validate_email(cls, v):
        return validate_email(v)

class Customer(CustomerBase):
    id: int
    total_appointments: int = 0
    total_spent: float = 0.0
    no_show_count: int = 0
    last_booking_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CustomerResponse(CustomerBase):
    id: int
    total_appointments: int
    total_spent: float

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    preferred_stylist_id: Optional[int] = None
    preferred_service_types: Optional[List[str]] = None