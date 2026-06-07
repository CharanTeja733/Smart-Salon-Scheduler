from typing import List, Optional

from sqlalchemy.orm import Session,joinedload

from app.models.practitioner import Practitioner

from .base import BaseRepository


class PractitionerRepository(BaseRepository[Practitioner]):
    def __init__(self):
        super().__init__(Practitioner)

    def get_by_salon(self, db: Session, salon_id: int, is_active: Optional[bool] = True) -> List[Practitioner]:
        query = db.query(self.model).filter(self.model.salon_id == salon_id)
        if is_active is not None:
            query = query.filter(self.model.is_active == is_active)
        return query.all()

    def get_by_specialty(self, db: Session, specialty: str, limit: int = 20) -> List[Practitioner]:
        return db.query(self.model).filter(
            self.model.specialty.ilike(f"%{specialty}%"),
            self.model.is_active is True
        ).limit(limit).all()

    def get_by_service_type(self, db: Session, service_type: str, limit: int = 50) -> List[Practitioner]:
        return db.query(self.model).filter(
            self.model.specializations.contains([service_type]),
            self.model.is_active is True
        ).limit(limit).all()

    def lock_for_update(self, db: Session, practitioner_id: int) -> Optional[Practitioner]:
        return db.query(self.model).filter(self.model.id == practitioner_id).with_for_update().first()

    def update_rating(self, db: Session, practitioner_id: int, new_avg_rating: float, total_reviews: int):
        db.query(self.model).filter(self.model.id == practitioner_id).update({
            "rating": new_avg_rating,
            "total_reviews": total_reviews
        })
        db.flush()

    def get_by_id_with_salon(self, db: Session, practitioner_id: int) -> Optional[Practitioner]:
        return db.query(self.model).options(joinedload(self.model.salon)).filter(self.model.id == practitioner_id).first()