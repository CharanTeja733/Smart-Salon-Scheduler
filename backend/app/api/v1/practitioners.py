from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.practitioner import PractitionerRepository
from app.repositories.review import ReviewRepository
from app.schemas.practitioner import (
    AvailabilityResponse,
    DeactivateRequest,
    PractitionerResponse,
    UnavailableRequest,
)
from app.services.practitioner import PractitionerService
from app.services.scheduling import SchedulingService

router = APIRouter()

@router.get("/{practitioner_id}", response_model=PractitionerResponse)
async def get_practitioner(
    practitioner_id: int,
    include_reviews: bool = Query(False),
    db: Session = Depends(get_db)
):
    practitioner_repo = PractitionerRepository()
    practitioner = practitioner_repo.get_by_id_with_salon(db, practitioner_id)
    if not practitioner or not practitioner.is_active:
        raise HTTPException(status_code=404, detail="Practitioner not found")

    # Convert ORM to Pydantic model
    response = PractitionerResponse.from_orm(practitioner)
    # Manually set salon_name from the eager-loaded relationship
    response.salon_name = practitioner.salon.name if practitioner.salon else ""

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


@router.post("/{practitioner_id}/deactivate")
async def deactivate_practitioner(
    practitioner_id: int,
    req: DeactivateRequest,
    db: Session = Depends(get_db)
):
    """
    Mark a practitioner as inactive (sick day / leave).
    Cancels all future appointments and notifies affected customers.
    """
    result = await PractitionerService.deactivate_practitioner(
        practitioner_id, req.reason, db
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/{practitioner_id}/unavailable")
async def mark_practitioner_unavailable(
    practitioner_id: int,
    req: UnavailableRequest,
    # current_user = Depends(get_current_user),  # from JWT
    db: Session = Depends(get_db)
):
    #  Only allow if:
    #  - current_user.role == "admin", OR
    #  - current_user.practitioner_id == practitioner_id
    # if current_user.role != "admin" and current_user.practitioner_id != practitioner_id:
    #     raise HTTPException(status_code=403, detail="Not authorized")

    result = await PractitionerService.mark_unavailable(
        practitioner_id=practitioner_id,
        start_date=req.start_date,
        end_date=req.end_date,
        reason_code=req.reason_code,
        db=db,
        reason_text=req.reason_text
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
