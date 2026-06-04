from sqlalchemy.orm import Session
from datetime import date
from typing import List, Optional
from app.models.availability_exception import AvailabilityException
from app.repositories.base import BaseRepository

class AvailabilityExceptionRepository(BaseRepository[AvailabilityException]):
    def __init__(self):
        super().__init__(AvailabilityException)

    def get_for_practitioner(self, db: Session, practitioner_id: int, start_date: date, end_date: date) -> List[AvailabilityException]:
        return db.query(self.model).filter(
            self.model.practitioner_id == practitioner_id,
            self.model.exception_date >= start_date,
            self.model.exception_date <= end_date
        ).all()

    def add_exception(self, db: Session, practitioner_id: int, exception_date: date, reason_code: str, reason_text: str = None) -> AvailabilityException:
        return self.create(
            db,
            practitioner_id=practitioner_id,
            exception_date=exception_date,
            is_working=False,
            reason_code=reason_code,
            reason_text=reason_text
        )