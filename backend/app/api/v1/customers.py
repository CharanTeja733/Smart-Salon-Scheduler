from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.appointment import AppointmentRepository
from app.repositories.customer import CustomerRepository
from app.schemas.appointment import AppointmentStatusResponse
from app.schemas.customer import CustomerResponse, CustomerUpdate
from sqlalchemy.orm import joinedload
from app.models.appointment import Appointment
from app.models.practitioner import Practitioner
from app.models.salon import Salon

from datetime import datetime, timezone

router = APIRouter()

@router.get("/{phone}", response_model=CustomerResponse)
async def get_customer(
    phone: str,
    db: Session = Depends(get_db)
):
    customer_repo = CustomerRepository()
    customer = customer_repo.get_by_phone(db, phone)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.patch("/{phone}", response_model=CustomerResponse)
async def update_customer(
    phone: str,
    update: CustomerUpdate,
    db: Session = Depends(get_db)
):
    customer_repo = CustomerRepository()
    customer = customer_repo.get_by_phone(db, phone)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    update_data = update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(customer, key, value)
    db.flush()
    db.commit()
    return customer

@router.get("/{phone}/appointments", response_model=List[AppointmentStatusResponse])
async def get_customer_appointments(
    phone: str,
    status: Optional[str] = Query(None, regex="^(upcoming|past|cancelled)$"),
    db: Session = Depends(get_db)
):
    customer_repo = CustomerRepository()
    customer = customer_repo.get_by_phone(db, phone)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Base query with eager loading of practitioner and salon
    query = db.query(Appointment).filter(Appointment.customer_id == customer.id).options(
        joinedload(Appointment.practitioner).joinedload(Practitioner.salon)
    )
    
    now = datetime.now(timezone.utc)
    if status == "upcoming":
        query = query.filter(Appointment.start_time > now, Appointment.status != "cancelled")
    elif status == "past":
        query = query.filter(Appointment.start_time <= now)
    elif status == "cancelled":
        query = query.filter(Appointment.status == "cancelled")
    
    appointments = query.order_by(Appointment.start_time.desc()).all()
    
    # Map to response schema
    return [
        AppointmentStatusResponse(
            id=apt.id,
            practitioner_id=apt.practitioner_id,  
            practitioner_name=apt.practitioner.name,
            salon_name=apt.practitioner.salon.name,
            start_time=apt.start_time,
            status=apt.status,
            price=apt.price,
            deposit_paid=apt.deposit_paid
        )
        for apt in appointments
    ]