from sqlalchemy.orm import Session
from typing import Dict, List
from app.repositories.practitioner_repository import PractitionerRepository
from app.repositories.appointment_repository import AppointmentRepository
from app.services.notification_service import NotificationService

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

        # 7. Send notifications (SMS + email) – do this asynchronously (Celery) or fire-and-forget
        for apt in future_appointments:
            customer = apt.customer
            if customer.phone:
                message = f"Dear {customer.name}, your appointment with {practitioner.name} on {apt.start_time.strftime('%Y-%m-%d %H:%M')} has been cancelled due to practitioner unavailability. Please rebook. We apologize for the inconvenience."
                await NotificationService.send_sms(customer.phone, message)
            if customer.email:
                subject = "Appointment Cancelled"
                body = f"<p>Your appointment with {practitioner.name} on {apt.start_time.strftime('%Y-%m-%d %H:%M')} has been cancelled. Please visit our site to rebook.</p>"
                await NotificationService.send_email(customer.email, subject, body)

        return {
            "success": True,
            "practitioner_id": practitioner_id,
            "cancelled_count": cancelled,
            "message": f"Practitioner deactivated and {cancelled} appointments cancelled. Customers notified."
        }