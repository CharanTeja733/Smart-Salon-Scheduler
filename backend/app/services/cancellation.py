from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.repositories import AppointmentRepository, AuditLogRepository
from app.services.payment_service import PaymentService
from app.services.waitlist_service import WaitlistService

class CancellationService:
    # Refund tiers: (hours_before, refund_percentage)
    REFUND_POLICY = [
        (24, 100),   # 100% if >=24h
        (2, 50),     # 50% if 2-24h
        (0, 0)       # 0% if <2h
    ]

    @staticmethod
    async def cancel_appointment(appointment_id: int, reason: str, db: Session, ip_address: str = None):
        appointment_repo = AppointmentRepository()
        audit_repo = AuditLogRepository()

        appointment = appointment_repo.get_by_id(db, appointment_id)
        if not appointment:
            return {"success": False, "error": "Appointment not found"}
        if appointment.status in ["completed", "cancelled"]:
            return {"success": False, "error": f"Cannot cancel appointment with status {appointment.status}"}

        # Calculate refund percentage based on time before appointment
        now = datetime.utcnow()
        hours_until = (appointment.start_time - now).total_seconds() / 3600

        refund_percent = 0
        for threshold, percent in CancellationService.REFUND_POLICY:
            if hours_until >= threshold:
                refund_percent = percent
                break

        refund_amount = (appointment.deposit_amount * refund_percent) / 100
        cancellation_fee = appointment.deposit_amount - refund_amount

        # Process refund if deposit was paid
        if refund_amount > 0 and appointment.deposit_paid and appointment.deposit_payment_intent_id:
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

        # Notify waitlist (if slot becomes free)
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