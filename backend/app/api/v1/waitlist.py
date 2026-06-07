from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.waitlist import (
    WaitlistCreate,
    WaitlistResponse,
    WaitlistStatusResponse,
)
from app.repositories.waitlist import WaitlistRepository
from app.services.waitlist import WaitlistService

router = APIRouter()

@router.post("/", response_model=WaitlistResponse, status_code=201)
async def add_to_waitlist(
    entry: WaitlistCreate,
    db: Session = Depends(get_db)
):
    result = await WaitlistService.add_to_waitlist(
        db,
        practitioner_id=entry.practitioner_id,
        customer_phone=entry.customer_phone,
        preferred_date_start=entry.preferred_date_start,
        preferred_date_end=entry.preferred_date_end,
        service_type=entry.preferred_service_type
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return WaitlistResponse(
        waitlist_id=result["waitlist_id"],
        position=result["position"]
    )

@router.get("/{waitlist_id}", response_model=WaitlistStatusResponse)
async def get_waitlist_status(
    waitlist_id: int,
    db: Session = Depends(get_db)
):
    repo = WaitlistRepository()
    entry = repo.get_by_id(db, waitlist_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Waitlist entry not found")
    # Calculate position (simple count)
    position = repo.count(db, practitioner_id=entry.practitioner_id, status="active")
    return WaitlistStatusResponse(
        id=entry.id,
        status=entry.status,
        position=position,
        notified_at=entry.notified_at
    )
