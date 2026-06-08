from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.schemas.waitlist import (
    WaitlistCreate,
    WaitlistResponse,
    WaitlistStatusResponse,
)
from app.repositories.waitlist import WaitlistRepository
from app.services.waitlist import WaitlistService
from typing import List
from app.repositories.customer import CustomerRepository
from app.models.waitlist import WaitlistEntry

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
    entry = db.query(WaitlistEntry).options(
        joinedload(WaitlistEntry.practitioner)
    ).filter(WaitlistEntry.id == waitlist_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Waitlist entry not found")
    
    position = db.query(WaitlistEntry).filter(
        WaitlistEntry.practitioner_id == entry.practitioner_id,
        WaitlistEntry.status == "active",
        WaitlistEntry.created_at < entry.created_at
    ).count() + 1
    
    return WaitlistStatusResponse(
        id=entry.id,
        status=entry.status,
        position=position,
        notified_at=entry.notified_at,
        practitioner_id=entry.practitioner.id,
        practitioner_name=entry.practitioner.name,
        preferred_date_start=entry.preferred_date_start,
        preferred_date_end=entry.preferred_date_end,
        preferred_service_type=entry.preferred_service_type
    )


@router.get("/", response_model=List[WaitlistStatusResponse])
async def get_waitlist_by_customer(
    customer_phone: str = Query(..., description="Customer phone in E.164 format"),
    db: Session = Depends(get_db)
):
    customer_repo = CustomerRepository()
    customer = customer_repo.get_by_phone(db, customer_phone)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Query with joined load to get practitioner details
    entries = db.query(WaitlistEntry).options(
        joinedload(WaitlistEntry.practitioner)
    ).filter(
        WaitlistEntry.customer_id == customer.id,
        WaitlistEntry.status == "active"
    ).order_by(WaitlistEntry.created_at).all()
    
    result = []
    for entry in entries:
        # Calculate position for this practitioner
        position = db.query(WaitlistEntry).filter(
            WaitlistEntry.practitioner_id == entry.practitioner_id,
            WaitlistEntry.status == "active",
            WaitlistEntry.created_at < entry.created_at
        ).count() + 1
        
        result.append(WaitlistStatusResponse(
            id=entry.id,
            status=entry.status,
            position=position,
            notified_at=entry.notified_at,
            practitioner_id=entry.practitioner.id,
            practitioner_name=entry.practitioner.name,
            preferred_date_start=entry.preferred_date_start,
            preferred_date_end=entry.preferred_date_end,
            preferred_service_type=entry.preferred_service_type
        ))
    return result