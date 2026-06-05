from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None
    punctuality_rating: Optional[int] = Field(None, ge=1, le=5)
    quality_rating: Optional[int] = Field(None, ge=1, le=5)
    value_rating: Optional[int] = Field(None, ge=1, le=5)

class ReviewCreate(ReviewBase):
    appointment_id: int

class ReviewResponse(ReviewBase):
    id: int
    appointment_id: int
    practitioner_id: int
    customer_id: int
    sentiment_score: Optional[float] = None
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ReviewBrief(BaseModel):
    id: int
    rating: int
    comment: Optional[str] = None
    created_at: datetime
    customer_name: Optional[str] = None
