from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from typing import List, Optional
from app.database import get_db
from app.services.scheduling_service import SchedulingService
from app.repositories.practitioner_repository import PractitionerRepository
from app.repositories.review_repository import ReviewRepository
from app.schemas.practitioner import PractitionerResponse, AvailabilityResponse

router = APIRouter()

@router.get("/{practitioner_id}", response_model=PractitionerResponse)
async def get_practitioner(
    practitioner_id: int,
    include_reviews: bool = Query(False),
    db: Session = Depends(get_db)
):
    practitioner_repo = PractitionerRepository()
    practitioner = practitioner_repo.get_by_id(db, practitioner_id)
    if not practitioner or not practitioner.is_active:
        raise HTTPException(status_code=404, detail="Practitioner not found")
    
    response = PractitionerResponse.from_orm(practitioner)
    if include_reviews:
        review_repo = ReviewRepository()
        reviews = review_repo.get_by_practitioner(db, practitioner_id, limit=20)
        response.reviews = reviews
    return response

@router.get("/{practitioner_id}/availability", response_model=AvailabilityResponse)
async def get_availability(
    practitioner_id: int,
    date: date = Query(..., description="YYYY-MM-DD"),
    duration: int = Query(30, ge=30, le=120, multiple_of=30),
    db: Session = Depends(get_db)
):
    slots = SchedulingService.generate_available_slots(practitioner_id, date, db, duration)
    return AvailabilityResponse(
        practitioner_id=practitioner_id,
        date=date,
        available_slots=slots
    )