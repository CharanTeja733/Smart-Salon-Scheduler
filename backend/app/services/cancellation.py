# backend/app/services/cancellation.py
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.repositories import AppointmentRepository, AuditLogRepository
from app.services.payment import PaymentService
from app.services.waitlist import WaitlistService


class CancellationService:
    REFUND_POLICY = [
        (24, 100),
        (2, 50),
        (0, 0)
    ]

    @staticmethod
    async def cancel_appointment(appointment_id: int, reason: str, db: Session, ip_address: Optional[str] = None):
        appointment_repo = AppointmentRepository()
        audit_repo = AuditLogRepository()

        appointment = appointment_repo.get_by_id(db, appointment_id)
        if not appointment:
            return {"success": False, "error": "Appointment not found"}
        if appointment.status in ["completed", "cancelled"]:
            return {"success": False, "error": f"Cannot cancel appointment with status {appointment.status}"}

        # If deposit was never paid, no refund, no fee
        if not appointment.deposit_paid:
            # Just cancel the appointment
            appointment.status = "cancelled"
            appointment.cancelled_at = datetime.now(timezone.utc)
            appointment.cancellation_reason = reason
            db.flush()
            db.commit()
            return {
                "success": True,
                "appointment_id": appointment_id,
                "refund_amount": 0.0,
                "cancellation_fee": 0.0,
                "policy_applied": "No deposit paid – no refund"
            }

        # Only proceed with refund calculation if deposit was paid
        now = datetime.now(timezone.utc)
        hours_until = (appointment.start_time - now).total_seconds() / 3600

        refund_percent = 0
        for threshold, percent in CancellationService.REFUND_POLICY:
            if hours_until >= threshold:
                refund_percent = percent
                break

        refund_amount = (appointment.deposit_amount * refund_percent) / 100
        cancellation_fee = appointment.deposit_amount - refund_amount

        # Process refund via Stripe
        if refund_amount > 0:
            refund_success = await PaymentService.process_refund(
                appointment.deposit_payment_intent_id,
                refund_amount
            )
            if not refund_success:
                return {"success": False, "error": "Refund failed, please contact support"}

        # Update appointment
        appointment.status = "cancelled"
        appointment.cancelled_at = now
        appointment.cancellation_reason = reason
        appointment.cancellation_fee = cancellation_fee
        appointment.refund_amount = refund_amount
        db.flush()

        # Audit log
        audit_repo.log_change(
            db,
            entity_type="appointment",
            entity_id=appointment_id,
            action="cancel",
            old_values={"status": "confirmed" if appointment.deposit_paid else "pending"},
            new_values={"status": "cancelled", "refund_amount": refund_amount},
            ip_address=ip_address
        )
        db.commit()

        # Notify waitlist
        if appointment.practitioner_id:
            await WaitlistService.notify_for_slot(
                db, appointment.practitioner_id, appointment.start_time, appointment.service_type
            )

        policy_text = f"{refund_percent}% refund" if refund_percent > 0 else "No refund"
        return {
            "success": True,
            "appointment_id": appointment_id,
            "refund_amount": refund_amount,
            "cancellation_fee": cancellation_fee,
            "policy_applied": policy_text
        }