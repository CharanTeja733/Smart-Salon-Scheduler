from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.repositories import (
    PractitionerRepository,
    AppointmentRepository,
    CustomerRepository,
    AuditLogRepository
)
from app.services.payment_service import PaymentService
from app.services.scheduling_service import SchedulingService
from app.schemas.appointment import CustomerInfo

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
        ip_address: str = None,
        user_agent: str = None
    ):
        practitioner_repo = PractitionerRepository()
        appointment_repo = AppointmentRepository()
        customer_repo = CustomerRepository()
        audit_repo = AuditLogRepository()

        # 1. Lock practitioner row to prevent concurrent modifications
        practitioner = practitioner_repo.lock_for_update(db, practitioner_id)
        if not practitioner or not practitioner.is_active:
            return {"success": False, "error": "Practitioner not available"}

        # 2. Double-check slot availability within transaction
        existing = appointment_repo.get_by_practitioner_and_slot(
            db, practitioner_id, start_time, for_update=True
        )
        if existing:
            return {"success": False, "error": "Slot already booked"}

        # 3. Check for longer overlapping appointments
        end_time = start_time + timedelta(minutes=duration_minutes)
        overlapping = appointment_repo.get_overlapping(
            db, practitioner_id, start_time, end_time, for_update=True
        )
        if overlapping:
            return {"success": False, "error": "Time slot conflicts with existing booking"}

        # 4. Business rule: min 1h advance, max 90 days (already validated in schema, but double-check)
        now = datetime.utcnow()
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

        # 8. Create Stripe PaymentIntent for deposit
        payment_intent = await PaymentService.create_deposit_intent(
            appointment_id=appointment.id,
            amount=deposit,
            customer_email=customer.email,
            customer_name=customer.name
        )

        # 9. Audit log
        audit_repo.log_change(
            db,
            entity_type="appointment",
            entity_id=appointment.id,
            action="create",
            new_values=appointment_data,
            ip_address=ip_address,
            user_agent=user_agent
        )

        # 10. Update customer stats
        customer_repo.increment_appointment_count(db, customer.id, amount_spent=0)  # spent added later

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

        # Verify payment with Stripe
        verified = await payment_service.verify_deposit(payment_intent_id)
        if not verified:
            return {"success": False, "error": "Payment verification failed"}

        appointment = appointment_repo.update_status(db, appointment_id, "confirmed")
        if not appointment:
            return {"success": False, "error": "Appointment not found"}

        # Update deposit paid flag
        appointment.deposit_paid = True
        appointment.deposit_payment_intent_id = payment_intent_id
        db.flush()
        db.commit()

        # Schedule reminder (background task) - will be handled by Celery later
        from app.tasks.reminders import schedule_reminder
        schedule_reminder.delay(appointment_id)

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

        # Lock practitioner
        practitioner = practitioner_repo.lock_for_update(db, appointment.practitioner_id)
        if not practitioner:
            return {"success": False, "error": "Practitioner unavailable"}

        # Check availability of new slot
        new_end = new_start_time + timedelta(minutes=appointment.service_duration)
        overlapping = appointment_repo.get_overlapping(
            db, appointment.practitioner_id, new_start_time, new_end, for_update=True
        )
        if overlapping:
            return {"success": False, "error": "New time slot not available"}

        # Atomic: update appointment time
        old_start = appointment.start_time
        appointment.start_time = new_start_time
        appointment.end_time = new_end
        db.flush()

        audit_repo.log_change(
            db,
            entity_type="appointment",
            entity_id=appointment_id,
            action="reschedule",
            old_values={"start_time": old_start},
            new_values={"start_time": new_start_time}
        )
        db.commit()

        return {"success": True, "appointment_id": appointment_id, "new_start_time": new_start_time}