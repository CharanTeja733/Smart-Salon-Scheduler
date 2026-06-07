from datetime import date, datetime, timedelta
from typing import Dict, Optional

from sqlalchemy.orm import Session

from app.repositories.appointment import AppointmentRepository
from app.repositories.availability_exception import (
    AvailabilityExceptionRepository,
)
from app.repositories.practitioner import PractitionerRepository
from app.services.payment import PaymentService
from app.tasks.reminders import send_cancellation_notifications


class PractitionerService:
    @staticmethod
    async def deactivate_practitioner(
        practitioner_id: int,
        reason: str,
        db: Session
    ) -> Dict:
        """
        Mark practitioner as inactive, cancel all future appointments,
        and notify affected customers.
        """
        prac_repo = PractitionerRepository()
        apt_repo = AppointmentRepository()

        # 1. Lock practitioner row to prevent concurrent changes
        practitioner = prac_repo.lock_for_update(db, practitioner_id)
        if not practitioner:
            return {"success": False, "error": "Practitioner not found"}

        # 2. Already inactive?
        if not practitioner.is_active:
            return {"success": False, "error": "Practitioner already inactive"}

        # 3. Fetch future appointments
        future_appointments = apt_repo.get_future_for_practitioner(db, practitioner_id)
        if not future_appointments:
            # No appointments – just deactivate
            practitioner.is_active = False
            db.commit()
            return {"success": True, "cancelled_count": 0, "message": "Practitioner deactivated (no appointments)"}

        # 4. Prepare notification details for each customer
        appointment_ids = [apt.id for apt in future_appointments]
        cancel_reason = f"Sick day / unavailability: {reason}"

        # 5. Cancel all appointments
        cancelled = apt_repo.cancel_bulk(db, appointment_ids, cancel_reason)

        # 6. Mark practitioner inactive
        practitioner.is_active = False
        db.commit()

        # 7. Send notifications (SMS + email) – do this asynchronously (Celery)
        # Dispatch Celery task for notifications
        send_cancellation_notifications.delay(appointment_ids, reason)

        return {
            "success": True,
            "practitioner_id": practitioner_id,
            "cancelled_count": cancelled,
            "message": f"Practitioner deactivated and {cancelled} appointments cancelled. Customers will be notified asynchronously."
        }


    @staticmethod
    async def mark_unavailable(
        practitioner_id: int,
        start_date: date,
        end_date: date,
        reason_code: str,
        db: Session,
        reason_text: Optional[str] = None
    ) -> Dict:
        prac_repo = PractitionerRepository()
        apt_repo = AppointmentRepository()
        exc_repo = AvailabilityExceptionRepository()

        # Lock practitioner row
        practitioner = prac_repo.lock_for_update(db, practitioner_id)
        if not practitioner:
            return {"success": False, "error": "Practitioner not found"}

        # Fetch appointments in date range (only pending/confirmed)
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.max.time())
        appointments = apt_repo.get_by_practitioner_date_range(db, practitioner_id, start_dt, end_dt)

        # Process appointments (refund & cancel)
        cancelled_count = 0
        refund_errors = []
        appointment_ids = []

        for apt in appointments:
            appointment_ids.append(apt.id)
            # Refund deposit if paid
            if apt.deposit_paid and apt.deposit_payment_intent_id:
                success = await PaymentService.process_refund(apt.deposit_payment_intent_id, apt.deposit_amount)
                if not success:
                    refund_errors.append(apt.id)
            # Refund final payment if already captured
            if apt.status == "confirmed" and apt.final_payment_intent_id:
                final_amount = apt.price - apt.deposit_amount
                if final_amount > 0:
                    await PaymentService.process_refund(apt.final_payment_intent_id, final_amount)
            # Cancel appointment
            apt.status = "cancelled"
            apt.cancelled_at = datetime.utcnow()
            apt.cancellation_reason = f"Practitioner unavailable: {reason_code}"
            apt.refund_amount = apt.deposit_amount
            cancelled_count += 1

        # Insert availability exceptions for each date, but skip if already exists
        current_date = start_date
        inserted_count = 0
        while current_date <= end_date:
            existing = exc_repo.get_by_practitioner_and_date(db, practitioner_id, current_date)
            if not existing:
                exc_repo.add_exception(db, practitioner_id, current_date, reason_code, reason_text)
                inserted_count += 1
            current_date += timedelta(days=1)

        # Commit only if something changed
        if cancelled_count > 0 or inserted_count > 0:
            db.commit()
        else:
            # No changes – already marked unavailable
            return {
                "success": True,
                "practitioner_id": practitioner_id,
                "message": "Practitioner already marked unavailable for the specified date range.",
                "already_processed": True
            }

        # Send async notifications if any appointments were cancelled
        if appointment_ids:
            from app.tasks.reminders import send_cancellation_notifications
            send_cancellation_notifications.delay(appointment_ids, reason_code, reason_text)

        return {
            "success": True,
            "practitioner_id": practitioner_id,
            "affected_dates": [start_date.isoformat(), end_date.isoformat()],
            "cancelled_count": cancelled_count,
            "refund_errors": refund_errors,
            "message": f"Cancelled {cancelled_count} appointments between {start_date} and {end_date}. Notifications queued."
        }