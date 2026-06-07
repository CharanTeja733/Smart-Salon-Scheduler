from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_idempotency_key
from app.database import get_db
from app.schemas.appointment import (
    AppointmentStatusResponse,
    BookingRequest,
    BookingResponse,
    CancelRequest,
    CancelResponse,
    ConfirmRequest,
    RescheduleRequest,
)
from app.services.booking import BookingService
from app.services.cancellation import CancellationService
from app.repositories.appointment import AppointmentRepository

router = APIRouter()

@router.post("/", response_model=BookingResponse, status_code=201)
async def create_booking(
    booking: BookingRequest,
    background_tasks: BackgroundTasks,
    idempotency_key: str = Depends(get_idempotency_key),
    db: Session = Depends(get_db)
):
    # Idempotency check would be implemented here using Redis
    result = await BookingService.create_booking(
        practitioner_id=booking.practitioner_id,
        start_time=booking.start_time,
        customer_info=booking.customer,
        service_type=booking.service_type.value,
        duration_minutes=booking.duration_minutes,
        db=db
    )
    if not result["success"]:
        raise HTTPException(status_code=409, detail=result["error"])

    # Return response
    return BookingResponse(
        appointment_id=result["appointment_id"],
        status="pending",
        price=result["price"],
        deposit_amount=result["deposit_amount"],
        client_secret=result["client_secret"],
        hold_expires_at=result["hold_expires_at"]
    )

@router.post("/{appointment_id}/confirm")
async def confirm_booking(
    appointment_id: int,
    confirm: ConfirmRequest,
    db: Session = Depends(get_db)
):
    result = await BookingService.confirm_booking(appointment_id, confirm.payment_intent_id, db)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/{appointment_id}/cancel", response_model=CancelResponse)
async def cancel_booking(
    appointment_id: int,
    cancel: CancelRequest,
    db: Session = Depends(get_db)
):
    result = await CancellationService.cancel_appointment(appointment_id, cancel.reason, db)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return CancelResponse(
        appointment_id=appointment_id,
        status="cancelled",
        refund_amount=result["refund_amount"],
        cancellation_fee=result["cancellation_fee"],
        policy_applied=result["policy_applied"]
    )

@router.post("/{appointment_id}/reschedule")
async def reschedule_booking(
    appointment_id: int,
    reschedule: RescheduleRequest,
    db: Session = Depends(get_db)
):
    result = await BookingService.reschedule_appointment(appointment_id, reschedule.new_start_time, db)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.get("/{appointment_id}", response_model=AppointmentStatusResponse)
async def get_appointment_status(
    appointment_id: int,
    db: Session = Depends(get_db)
):

    repo = AppointmentRepository()
    apt = repo.get_by_id(db, appointment_id)
    if not apt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return AppointmentStatusResponse(
        id=apt.id,
        practitioner_id=apt.practitioner_id,
        practitioner_name=apt.practitioner.name,
        salon_name=apt.practitioner.salon.name,
        start_time=apt.start_time,
        status=apt.status,
        price=apt.price,
        deposit_paid=apt.deposit_paid
    )
