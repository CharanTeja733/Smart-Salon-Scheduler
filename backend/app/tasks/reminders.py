from datetime import datetime, timedelta
from celery import shared_task
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.repositories.appointment_repository import AppointmentRepository
from app.services.notification_service import NotificationService

@shared_task
def send_reminder(appointment_id: int):
    """Send SMS reminder 24 hours before appointment."""
    db = SessionLocal()
    try:
        apt_repo = AppointmentRepository()
        appointment = apt_repo.get_by_id(db, appointment_id)
        if not appointment or appointment.status != "confirmed":
            return {"status": "skipped", "reason": "appointment not confirmed"}
        
        # Check if reminder already sent
        if appointment.reminder_sent:
            return {"status": "skipped", "reason": "already sent"}
        
        # Calculate time until appointment
        now = datetime.utcnow()
        hours_until = (appointment.start_time - now).total_seconds() / 3600
        
        # Only send if within 24-2 hours range
        if 2 <= hours_until <= 24:
            customer = appointment.customer
            practitioner = appointment.practitioner
            message = f"Reminder: Your appointment with {practitioner.name} at {practitioner.salon.name} is tomorrow at {appointment.start_time.strftime('%I:%M %p')}. Reply CANCEL to cancel."
            await NotificationService.send_sms(customer.phone, message)
            
            # Mark reminder as sent
            appointment.reminder_sent = True
            db.commit()
            return {"status": "sent", "appointment_id": appointment_id}
        else:
            return {"status": "skipped", "reason": f"hours_until={hours_until}"}
    finally:
        db.close()

@shared_task
def send_booking_confirmation_task(appointment_id: int, customer_email: str, customer_name: str, details: dict):
    """Send booking confirmation email (async)."""
    # Import inside to avoid circular import
    from app.services.notification_service import NotificationService
    await NotificationService.send_booking_confirmation(customer_email, customer_name, details)

@shared_task
def schedule_reminder(appointment_id: int):
    """Schedule a reminder to be sent 24 hours before appointment."""
    db = SessionLocal()
    try:
        apt_repo = AppointmentRepository()
        appointment = apt_repo.get_by_id(db, appointment_id)
        if appointment and appointment.start_time:
            # Calculate delay until 24 hours before
            now = datetime.utcnow()
            reminder_time = appointment.start_time - timedelta(hours=24)
            delay_seconds = (reminder_time - now).total_seconds()
            if delay_seconds > 0:
                send_reminder.apply_async(args=[appointment_id], countdown=delay_seconds)
                return {"status": "scheduled", "delay_seconds": delay_seconds}
            else:
                # Too close, send immediately
                send_reminder.delay(appointment_id)
                return {"status": "sent_immediately"}
    finally:
        db.close()