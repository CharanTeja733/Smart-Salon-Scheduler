from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.customer_repository import CustomerRepository
from app.schemas.appointment import AppointmentStatusResponse
from app.schemas.customer import CustomerResponse, CustomerUpdate

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
    status: str = Query(None, regex="^(upcoming|past|cancelled)$"),
    db: Session = Depends(get_db)
):
    customer_repo = CustomerRepository()
    customer = customer_repo.get_by_phone(db, phone)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    apt_repo = AppointmentRepository()
    if status == "upcoming":
        appointments = apt_repo.get_upcoming_for_customer(db, customer.id)
    elif status == "past":
        appointments = apt_repo.get_past_for_customer(db, customer.id)
    else:
        # all
        appointments = apt_repo.get_all(db, skip=0, limit=50)  # simplified
    return appointments
