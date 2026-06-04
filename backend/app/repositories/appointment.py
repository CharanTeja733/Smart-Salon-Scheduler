from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
from typing import List, Optional
from .base import BaseRepository
from app.models.appointment import Appointment

class AppointmentRepository(BaseRepository[Appointment]):
    def __init__(self):
        super().__init__(Appointment)

    def get_by_practitioner_and_slot(
        self, db: Session, practitioner_id: int, start_time: datetime, for_update: bool = False
    ) -> Optional[Appointment]:
        query = db.query(self.model).filter(
            self.model.practitioner_id == practitioner_id,
            self.model.start_time == start_time,
            self.model.status.in_(["pending", "confirmed"])
        )
        if for_update:
            query = query.with_for_update()
        return query.first()

    def get_overlapping(
        self, db: Session, practitioner_id: int, start_time: datetime, end_time: datetime, for_update: bool = False
    ) -> List[Appointment]:
        query = db.query(self.model).filter(
            self.model.practitioner_id == practitioner_id,
            or_(
                and_(self.model.start_time >= start_time, self.model.start_time < end_time),
                and_(self.model.end_time > start_time, self.model.end_time <= end_time),
                and_(self.model.start_time <= start_time, self.model.end_time >= end_time)
            ),
            self.model.status.in_(["pending", "confirmed"])
        )
        if for_update:
            query = query.with_for_update()
        return query.all()

    def get_upcoming_for_customer(self, db: Session, customer_id: int, limit: int = 10) -> List[Appointment]:
        now = datetime.utcnow()
        return db.query(self.model).filter(
            self.model.customer_id == customer_id,
            self.model.start_time > now,
            self.model.status.in_(["confirmed", "pending"])
        ).order_by(self.model.start_time).limit(limit).all()

    def get_past_for_customer(self, db: Session, customer_id: int, limit: int = 20) -> List[Appointment]:
        now = datetime.utcnow()
        return db.query(self.model).filter(
            self.model.customer_id == customer_id,
            self.model.start_time <= now
        ).order_by(self.model.start_time.desc()).limit(limit).all()

    def get_for_reminder(self, db: Session) -> List[Appointment]:
        now = datetime.utcnow()
        reminder_window_start = now + timedelta(hours=23)
        reminder_window_end = now + timedelta(hours=25)
        return db.query(self.model).filter(
            self.model.status == "confirmed",
            self.model.reminder_sent == False,
            self.model.start_time >= reminder_window_start,
            self.model.start_time <= reminder_window_end
        ).all()

    def update_status(self, db: Session, appointment_id: int, status: str) -> Optional[Appointment]:
        appointment = self.get_by_id(db, appointment_id)
        if appointment:
            appointment.status = status
            if status == "confirmed":
                appointment.confirmed_at = datetime.utcnow()
            elif status == "completed":
                appointment.completed_at = datetime.utcnow()
            elif status == "cancelled":
                appointment.cancelled_at = datetime.utcnow()
            db.flush()
        return appointment

    def release_expired_holds(self, db: Session) -> int:
        now = datetime.utcnow()
        expired = db.query(self.model).filter(
            self.model.status == "pending",
            self.model.hold_expires_at < now
        ).all()
        for apt in expired:
            apt.status = "cancelled"
            apt.cancelled_at = now
            apt.cancellation_reason = "Hold expired without payment"
        db.flush()
        return len(expired)

    def get_future_for_practitioner(self, db: Session, practitioner_id: int) -> List[Appointment]:
        """Return all pending/confirmed appointments from now onwards for a practitioner."""
        now = datetime.utcnow()
        return db.query(self.model).filter(
            self.model.practitioner_id == practitioner_id,
            self.model.start_time >= now,
            self.model.status.in_(["pending", "confirmed"])
        ).order_by(self.model.start_time).all()

    def cancel_bulk(self, db: Session, appointment_ids: List[int], reason: str) -> int:
        """Cancel multiple appointments at once (used for sick day)."""
        count = db.query(self.model).filter(self.model.id.in_(appointment_ids)).update(
            {
                "status": "cancelled",
                "cancelled_at": datetime.utcnow(),
                "cancellation_reason": reason
            },
            synchronize_session=False
        )
        db.flush()
        return count    