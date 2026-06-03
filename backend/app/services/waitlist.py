from datetime import datetime
from sqlalchemy.orm import Session
from app.repositories import WaitlistRepository, CustomerRepository
from app.services.notification_service import NotificationService

class WaitlistService:
    @staticmethod
    async def add_to_waitlist(
        db: Session,
        practitioner_id: int,
        customer_phone: str,
        preferred_date_start: datetime = None,
        preferred_date_end: datetime = None,
        service_type: str = None
    ):
        customer_repo = CustomerRepository()
        waitlist_repo = WaitlistRepository()

        customer = customer_repo.get_by_phone(db, customer_phone)
        if not customer:
            return {"success": False, "error": "Customer not found"}

        entry = waitlist_repo.create(
            db,
            practitioner_id=practitioner_id,
            customer_id=customer.id,
            preferred_date_start=preferred_date_start,
            preferred_date_end=preferred_date_end,
            preferred_service_type=service_type,
            status="active",
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        db.commit()

        # Calculate position
        position = waitlist_repo.count(db, practitioner_id=practitioner_id, status="active")
        return {"success": True, "waitlist_id": entry.id, "position": position}

    @staticmethod
    async def notify_for_slot(db: Session, practitioner_id: int, slot_time: datetime, service_type: str = None):
        waitlist_repo = WaitlistRepository()
        entries = waitlist_repo.get_matching_for_slot(db, practitioner_id, slot_time, service_type)
        for entry in entries:
            customer = entry.customer
            message = f"Good news! A slot just opened up with your preferred stylist at {slot_time.strftime('%I:%M %p')}. Book now before it's gone!"
            await NotificationService.send_sms(customer.phone, message)
            waitlist_repo.mark_notified(db, entry.id)
        db.commit()