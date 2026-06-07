from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import or_, and_

from sqlalchemy.orm import Session

from app.repositories import CustomerRepository, WaitlistRepository
from app.services.notification import NotificationService
from app.models.waitlist import WaitlistEntry

class WaitlistService:
    @staticmethod
    async def notify_for_slot(db: Session, practitioner_id: int, slot_time: datetime, service_type: Optional[str] = None):
        waitlist_repo = WaitlistRepository()
        entries = waitlist_repo.get_matching_for_slot(db, practitioner_id, slot_time, service_type)
        for entry in entries:
            customer = entry.customer
            message = f"Good news! A slot just opened up with your preferred stylist at {slot_time.strftime('%I:%M %p')}. Book now before it's gone!"
            await NotificationService.send_sms(customer.phone, message)
            waitlist_repo.mark_notified(db, entry.id)
        db.commit()


    @staticmethod
    async def add_to_waitlist(
        db: Session,
        practitioner_id: int,
        customer_phone: str,
        preferred_date_start: Optional[datetime] = None,
        preferred_date_end: Optional[datetime] = None,
        service_type: Optional[str] = None
    ):
        customer_repo = CustomerRepository()
        waitlist_repo = WaitlistRepository()

        customer = customer_repo.get_by_phone(db, customer_phone)
        if not customer:
            return {"success": False, "error": "Customer not found"}

        # Check for existing active entry with overlapping date range
        query = db.query(WaitlistEntry).filter(
            WaitlistEntry.practitioner_id == practitioner_id,
            WaitlistEntry.customer_id == customer.id,
            WaitlistEntry.status == "active"
        )
        # If date ranges are provided, check overlap
        if preferred_date_start and preferred_date_end:
            # Overlap condition: existing.start < new.end AND existing.end > new.start
            query = query.filter(
                or_(
                    # No date range in existing entry? Then treat as always overlapping? 
                # For simplicity, only compare when both have ranges.
                and_(
                    WaitlistEntry.preferred_date_start.isnot(None),
                    WaitlistEntry.preferred_date_end.isnot(None),
                    WaitlistEntry.preferred_date_start < preferred_date_end,
                    WaitlistEntry.preferred_date_end > preferred_date_start
                ),
                # If existing entry has no date range, treat as conflict (since it's for any time)
                and_(
                    WaitlistEntry.preferred_date_start.is_(None),
                    WaitlistEntry.preferred_date_end.is_(None)
                )
            )
        )

        existing = query.first()
        if existing:
            return {
                "success": False,
                "error": "You are already on the waitlist for this practitioner with overlapping date range.",
                "waitlist_id": existing.id
            }

        # Otherwise create new entry
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

        position = waitlist_repo.count(db, practitioner_id=practitioner_id, status="active")
        return {"success": True, "waitlist_id": entry.id, "position": position}