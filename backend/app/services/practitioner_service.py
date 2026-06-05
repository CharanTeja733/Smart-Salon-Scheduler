from datetime import date, datetime, timedelta
from typing import Dict, Optional

from sqlalchemy.orm import Session

from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.availability_exception_repository import (
    AvailabilityExceptionRepository,
)
from app.repositories.practitioner_repository import PractitionerRepository
from app.services.payment_service import PaymentService
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

    # @staticmethod
    # async def mark_unavailable(
    #     practitioner_id: int,
    #     start_date: date,
    #     end_date: date,
    #     reason_code: str,  # 'sick', 'emergency', 'other', 'private'
    #     db: Session,
    #     reason_text: str = None
    # ) -> Dict:
    #     """
    #     Mark practitioner unavailable for a date range.
    #     Cancels and refunds appointments on those dates only.
    #     Notifies affected customers.
    #     """
    #     prac_repo = PractitionerRepository()
    #     apt_repo = AppointmentRepository()
    #     exc_repo = AvailabilityExceptionRepository()

    #     # 1. Lock practitioner row
    #     practitioner = prac_repo.lock_for_update(db, practitioner_id)
    #     if not practitioner:
    #         return {"success": False, "error": "Practitioner not found"}

    #     # 2. Get all appointments in the date range (pending/confirmed)
    #     start_dt = datetime.combine(start_date, datetime.min.time())
    #     end_dt = datetime.combine(end_date, datetime.max.time())
    #     appointments = apt_repo.get_by_practitioner_date_range(db, practitioner_id, start_dt, end_dt)

    #     # 3. Process each appointment: refund & cancel
    #     cancelled_count = 0
    #     refund_errors = []
    #     for apt in appointments:
    #         # Refund deposit if paid
    #         if apt.deposit_paid and apt.deposit_payment_intent_id:
    #             success = await PaymentService.process_refund(apt.deposit_payment_intent_id, apt.deposit_amount)
    #             if not success:
    #                 refund_errors.append(apt.id)
    #         # If final payment captured, refund that too
    #         if apt.status == "confirmed" and apt.final_payment_intent_id:
    #             final_amount = apt.price - apt.deposit_amount
    #             if final_amount > 0:
    #                 await PaymentService.process_refund(apt.final_payment_intent_id, final_amount)
    #         # Cancel appointment
    #         apt.status = "cancelled"
    #         apt.cancelled_at = datetime.utcnow()
    #         apt.cancellation_reason = f"Practitioner unavailable: {reason_code}"
    #         apt.refund_amount = apt.deposit_amount
    #         cancelled_count += 1

    #     # 4. Insert availability exceptions for each date in range
    #     current_date = start_date
    #     while current_date <= end_date:
    #         exc_repo.add_exception(db, practitioner_id, current_date, reason_code, reason_text)
    #         current_date += timedelta(days=1)

    #     db.commit()

    #     # 5. Notify customers (SMS + email)
    #     from app.tasks.reminders import send_cancellation_notifications
    #     send_cancellation_notifications.delay(appointment_ids, reason_code)

    #     return {
    #         "success": True,
    #         "practitioner_id": practitioner_id,
    #         "affected_dates": [start_date.isoformat(), end_date.isoformat()],
    #         "cancelled_count": cancelled_count,
    #         "refund_errors": refund_errors,
    #         "message": f"Cancelled {cancelled_count} appointments between {start_date} and {end_date}."
    #     }


    @staticmethod
    async def mark_unavailable(
        practitioner_id: int,
        start_date: date,
        end_date: date,
        reason_code: str,  # 'sick', 'emergency', 'other', 'private'
        db: Session,
        reason_text: Optional[str] = None
    ) -> Dict:
        """
        Mark practitioner unavailable for a date range.
        Cancels and refunds appointments on those dates only.
        Notifies affected customers asynchronously via Celery.
        """
        prac_repo = PractitionerRepository()
        apt_repo = AppointmentRepository()
        exc_repo = AvailabilityExceptionRepository()

        # 1. Lock practitioner row
        practitioner = prac_repo.lock_for_update(db, practitioner_id)
        if not practitioner:
            return {"success": False, "error": "Practitioner not found"}

        # 2. Fetch appointments in date range
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.max.time())
        appointments = apt_repo.get_by_practitioner_date_range(db, practitioner_id, start_dt, end_dt)

        # 3. Process each appointment: refund & cancel
        cancelled_count = 0
        refund_errors = []
        appointment_ids = []  # collect for Celery task

        for apt in appointments:
            appointment_ids.append(apt.id)

            # Refund deposit if paid
            if apt.deposit_paid and apt.deposit_payment_intent_id:
                success = await PaymentService.process_refund(apt.deposit_payment_intent_id, apt.deposit_amount)
                if not success:
                    refund_errors.append(apt.id)
                    # Continue to cancel anyway

            # Refund final payment if already captured
            if apt.status == "confirmed" and apt.final_payment_intent_id:
                final_amount = apt.price - apt.deposit_amount
                if final_amount > 0:
                    await PaymentService.process_refund(apt.final_payment_intent_id, final_amount)

            # Cancel the appointment
            apt.status = "cancelled"
            apt.cancelled_at = datetime.utcnow()
            apt.cancellation_reason = f"Practitioner unavailable: {reason_code}"
            apt.refund_amount = apt.deposit_amount
            cancelled_count += 1

        # 4. Insert availability exceptions for each date in range
        current_date = start_date
        while current_date <= end_date:
            exc_repo.add_exception(db, practitioner_id, current_date, reason_code, reason_text)
            current_date += timedelta(days=1)

        # 5. Commit all changes
        db.commit()

        # 6. Send async notifications via Celery (if any appointments were cancelled)
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
