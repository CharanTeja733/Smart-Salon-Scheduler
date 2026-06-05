from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.ai import SentimentResponse, StylistMatchResponse
from app.services.ai_matching_service import AIStylistMatcherService
from app.services.sentiment_service import SentimentService

router = APIRouter()

@router.get("/match-stylist", response_model=StylistMatchResponse)
async def match_stylist(
    service_type: str = Query(..., regex="^(haircut|color|blowout|nails|makeup|waxing|facial)$"),
    customer_phone: Optional[str] = None,
    lat: Optional[float] = Query(None, ge=-90, le=90),
    lng: Optional[float] = Query(None, ge=-180, le=180),
    preferred_date: Optional[str] = None,
    limit: int = Query(3, ge=1, le=10),
    db: Session = Depends(get_db)
):
    from datetime import date
    preferred_date_obj = date.fromisoformat(preferred_date) if preferred_date else None
    matches = await AIStylistMatcherService.find_best_matches(
        service_type=service_type,
        db=db,
        customer_phone=customer_phone,
        lat=lat,
        lng=lng,
        preferred_date=preferred_date_obj,
        limit=limit
    )
    return StylistMatchResponse(service_type=service_type, matches=matches)

@router.get("/sentiment", response_model=SentimentResponse)
async def analyze_sentiment(
    text: str = Query(..., min_length=3, max_length=1000)
):
    result = SentimentService.analyze(text)
    return SentimentResponse(
        text=text,
        sentiment_score=result["sentiment_score"],
        sentiment_label=result["sentiment_label"],
        confidence=result["confidence"]
    )
