from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class SalonBase(BaseModel):
    google_place_id: str
    name: str
    address: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    phone: Optional[str] = None
    rating: float = Field(0.0, ge=0, le=5)
    rating_count: int = Field(0, ge=0)
    opening_hours: Dict[str, str]

class Salon(SalonBase):
    id: int
    photo_reference: Optional[str] = None
    cached_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SalonSearchParams(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    radius: int = Field(5000, ge=100, le=50000)
    min_rating: float = Field(0.0, ge=0, le=5)
    service_type: Optional[str] = None
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)

class SalonResponse(SalonBase):
    id: int
    distance_meters: Optional[float] = None
    photo_reference: Optional[str] = None
    practitioners: Optional[List['PractitionerBrief']] = None

    class Config:
        from_attributes = True

# Forward reference for PractitionerBrief
from .practitioner import PractitionerBrief

SalonResponse.model_rebuild()
