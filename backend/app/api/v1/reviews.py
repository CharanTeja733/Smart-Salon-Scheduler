from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.sentiment_service import SentimentService
from app.repositories.review_repository import ReviewRepository
from app.repositories.appointment_repository import AppointmentRepository
from app.schemas.review import ReviewCreate, ReviewResponse

router = APIRouter()

@router.post("/", response_model=ReviewResponse, status_code=201)
async def create_review(
    review_in: ReviewCreate,
    db: Session = Depends(get_db)
):
    # Verify appointment exists and is completed
    apt_repo = AppointmentRepository()
    appointment = apt_repo.get_by_id(db, review_in.appointment_id)
    if not appointment or appointment.status != "completed":
        raise HTTPException(status_code=400, detail="Can only review completed appointments")
    
    # Create review with sentiment
    review_repo = ReviewRepository()
    review_data = review_in.dict()
    review = review_repo.create_with_sentiment(db, **review_data)
    db.commit()
    
    # Update practitioner's average rating (async in production, sync here)
    avg_rating, total = review_repo.get_average_rating_for_practitioner(db, appointment.practitioner_id)
    from app.repositories.practitioner_repository import PractitionerRepository
    prac_repo = PractitionerRepository()
    prac_repo.update_rating(db, appointment.practitioner_id, avg_rating, total)
    db.commit()
    
    return review