from datetime import date, datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class StylistMatchRequest(BaseModel):
    service_type: str
    customer_phone: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    preferred_date: Optional[date] = None
    limit: int = Field(3, ge=1, le=10)

class MatchBreakdown(BaseModel):
    expertise_match: float
    rating: float
    review_sentiment: float
    workload_balance: float
    distance: Optional[float] = None

class StylistMatch(BaseModel):
    practitioner_id: int
    name: str
    salon_name: str
    distance_meters: Optional[float] = None
    rating: float
    price: float
    available_slots: List[datetime]
    match_score: float
    match_breakdown: MatchBreakdown
    explanation: str

class StylistMatchResponse(BaseModel):
    service_type: str
    matches: List[StylistMatch]

class SentimentResponse(BaseModel):
    text: str
    sentiment_score: float  # -1 to 1
    sentiment_label: str  # positive, negative, neutral
    confidence: float

class DailyPrediction(BaseModel):
    date: date
    expected_bookings: int
    peak_hours: List[str]

class DemandPredictionResponse(BaseModel):
    practitioner_id: int
    predictions: List[DailyPrediction]
    peak_day_of_week: str
    recommended_dynamic_pricing: Dict[str, str]
