from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.repositories import (
    AppointmentRepository,
    AuditLogRepository,
    CustomerRepository,
    PractitionerRepository,
)
from app.schemas.appointment import CustomerInfo
from app.services.payment import PaymentService

from app.tasks.reminders import schedule_reminder, send_booking_confirmation_task  

class BookingService:
    HOLD_MINUTES = 10

    @staticmethod
    async def create_booking(
        practitioner_id: int,
        start_time: datetime,
        customer_info: CustomerInfo,
        service_type: str,
        duration_minutes: int,
        db: Session,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        practitioner_repo = PractitionerRepository()
        appointment_repo = AppointmentRepository()
        customer_repo = CustomerRepository()
        audit_repo = AuditLogRepository()

        # Ensure start_time is timezone‑aware (assume UTC if naive)
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=timezone.utc)

        # 1. Lock practitioner row
        practitioner = practitioner_repo.lock_for_update(db, practitioner_id)
        if not practitioner or not practitioner.is_active:
            return {"success": False, "error": "Practitioner not available"}

        # 2. Double‑check slot availability
        existing = appointment_repo.get_by_practitioner_and_slot(
            db, practitioner_id, start_time, for_update=True
        )
        if existing:
            return {"success": False, "error": "Slot already booked"}

        # 3. Check overlapping appointments
        end_time = start_time + timedelta(minutes=duration_minutes)
        overlapping = appointment_repo.get_overlapping(
            db, practitioner_id, start_time, end_time, for_update=True
        )
        if overlapping:
            return {"success": False, "error": "Time slot conflicts with existing booking"}

        # 4. Business rules (use aware datetime)
        now = datetime.now(timezone.utc)
        if start_time < now + timedelta(hours=1):
            return {"success": False, "error": "Bookings must be at least 1 hour in advance"}
        if start_time > now + timedelta(days=90):
            return {"success": False, "error": "Cannot book more than 90 days in advance"}

        # 5. Get or create customer
        customer = customer_repo.get_or_create(
            db,
            phone=customer_info.phone,
            name=customer_info.name,
            email=customer_info.email
        )

        # 6. Calculate price
        base = practitioner.service_prices.get(service_type, practitioner.base_price)
        price = base * (duration_minutes / 30)
        deposit = price * 0.20  # 20% deposit

        # 7. Create appointment (status = 'pending')
        appointment_data = {
            "practitioner_id": practitioner_id,
            "customer_id": customer.id,
            "start_time": start_time,
            "end_time": end_time,
            "service_duration": duration_minutes,
            "service_type": service_type,
            "status": "pending",
            "price": price,
            "deposit_amount": deposit,
            "customer_notes": customer_info.notes,
            "hold_expires_at": now + timedelta(minutes=BookingService.HOLD_MINUTES)
        }
        appointment = appointment_repo.create(db, **appointment_data)

        # 8. Create JSON‑serializable copy for audit log (convert datetime to ISO strings)
        def prepare_for_json(obj):
            if isinstance(obj, dict):
                return {k: prepare_for_json(v) for k, v in obj.items()}
            elif isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, list):
                return [prepare_for_json(item) for item in obj]
            else:
                return obj

        audit_data = prepare_for_json(appointment_data)

        # 9. Create Stripe PaymentIntent for deposit
        payment_intent = await PaymentService.create_deposit_intent(
            appointment_id=appointment.id,
            amount=deposit,
            customer_email=customer.email,
            customer_name=customer.name
        )

        # 10. Audit log
        audit_repo.log_change(
            db,
            entity_type="appointment",
            entity_id=appointment.id,
            action="create",
            new_values=audit_data,
            ip_address=ip_address,
            user_agent=user_agent
        )

        # 11. Update customer stats
        customer_repo.increment_appointment_count(db, customer.id, amount_spent=0)

        db.commit()

        return {
            "success": True,
            "appointment_id": appointment.id,
            "price": price,
            "deposit_amount": deposit,
            "client_secret": payment_intent.client_secret,
            "hold_expires_at": appointment.hold_expires_at
        }

    @staticmethod
    async def confirm_booking(appointment_id: int, payment_intent_id: str, db: Session):
        appointment_repo = AppointmentRepository()
        payment_service = PaymentService

        verified = await payment_service.verify_deposit(payment_intent_id)
        if not verified:
            return {"success": False, "error": "Payment verification failed"}

        appointment = appointment_repo.update_status(db, appointment_id, "confirmed")
        if not appointment:
            return {"success": False, "error": "Appointment not found"}

        appointment.deposit_paid = True
        appointment.deposit_payment_intent_id = payment_intent_id
        db.flush()
        db.commit()

        # Schedule the 24h reminder
        schedule_reminder.delay(appointment_id)

        # Send immediate confirmation notification (email + SMS)
        customer = appointment.customer
        practitioner = appointment.practitioner
        salon = practitioner.salon
        details = {
            "appointment_id": appointment.id,
            "practitioner_name": practitioner.name,
            "salon_name": salon.name if salon else "",
            "start_time": appointment.start_time.isoformat(),
            "service_type": appointment.service_type
        }
        send_booking_confirmation_task.delay(
            appointment_id=appointment.id,
            customer_email=customer.email,
            customer_name=customer.name,
            details=details
        )

        return {"success": True, "appointment_id": appointment_id, "status": "confirmed"}
    @staticmethod
    async def reschedule_appointment(appointment_id: int, new_start_time: datetime, db: Session):
        appointment_repo = AppointmentRepository()
        practitioner_repo = PractitionerRepository()
        audit_repo = AuditLogRepository()

        appointment = appointment_repo.get_by_id(db, appointment_id)
        if not appointment:
            return {"success": False, "error": "Appointment not found"}
        if appointment.status not in ["pending", "confirmed"]:
            return {"success": False, "error": "Cannot reschedule completed or cancelled appointment"}

        if new_start_time.tzinfo is None:
            new_start_time = new_start_time.replace(tzinfo=timezone.utc)

        practitioner = practitioner_repo.lock_for_update(db, appointment.practitioner_id)
        if not practitioner:
            return {"success": False, "error": "Practitioner unavailable"}

        new_end = new_start_time + timedelta(minutes=appointment.service_duration)
        overlapping = appointment_repo.get_overlapping(
            db, appointment.practitioner_id, new_start_time, new_end, for_update=True
        )
        if overlapping:
            return {"success": False, "error": "New time slot not available"}

        old_start = appointment.start_time
        appointment.start_time = new_start_time
        appointment.end_time = new_end
        db.flush()

        audit_repo.log_change(
            db,
            entity_type="appointment",
            entity_id=appointment_id,
            action="reschedule",
            old_values={"start_time": old_start.isoformat() if old_start else None},
            new_values={"start_time": new_start_time.isoformat()}
        )
        db.commit()

        return {"success": True, "appointment_id": appointment_id, "new_start_time": new_start_time}