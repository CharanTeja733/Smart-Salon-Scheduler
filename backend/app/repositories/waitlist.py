from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
from .base import BaseRepository
from app.models.waitlist import WaitlistEntry

class WaitlistRepository(BaseRepository[WaitlistEntry]):
    def __init__(self):
        super().__init__(WaitlistEntry)

    def get_active_for_practitioner(self, db: Session, practitioner_id: int) -> List[WaitlistEntry]:
        return db.query(self.model).filter(
            self.model.practitioner_id == practitioner_id,
            self.model.status == "active"
        ).order_by(self.model.created_at).all()

    def get_matching_for_slot(
        self, db: Session, practitioner_id: int, slot_time: datetime, service_type: str = None
    ) -> List[WaitlistEntry]:
        query = db.query(self.model).filter(
            self.model.practitioner_id == practitioner_id,
            self.model.status == "active"
        )
        if service_type:
            query = query.filter(self.model.preferred_service_type == service_type)
        query = query.filter(
            (self.model.preferred_date_start <= slot_time) | (self.model.preferred_date_start.is_(None)),
            (self.model.preferred_date_end >= slot_time) | (self.model.preferred_date_end.is_(None))
        )
        return query.order_by(self.model.created_at).all()

    def mark_notified(self, db: Session, waitlist_id: int):
        self.update(db, waitlist_id, status="notified", notified_at=datetime.utcnow())

    def mark_booked(self, db: Session, waitlist_id: int):
        self.update(db, waitlist_id, status="booked")

    def expire_old(self, db: Session, days: int = 7) -> int:
        cutoff = datetime.utcnow() - timedelta(days=days)
        old = db.query(self.model).filter(
            self.model.created_at < cutoff,
            self.model.status == "active"
        ).all()
        for entry in old:
            entry.status = "expired"
        db.flush()
        return len(old)