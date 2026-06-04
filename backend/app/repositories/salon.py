from sqlalchemy.orm import Session
from sqlalchemy import func
from geoalchemy2.functions import ST_DistanceSphere
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
from .base import BaseRepository
from app.models.salon import Salon

class SalonRepository(BaseRepository[Salon]):
    def __init__(self):
        super().__init__(Salon)

    def search_by_location(
        self,
        db: Session,
        lat: float,
        lng: float,
        radius_meters: int = 5000,
        min_rating: float = 0.0,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Salon]:
        """Return salons within radius, ordered by distance."""
        point = f'POINT({lng} {lat})'
        query = db.query(self.model).filter(
            ST_DistanceSphere(self.model.location, func.ST_GeogFromText(point)) <= radius_meters,
            self.model.rating >= min_rating
        ).order_by(ST_DistanceSphere(self.model.location, func.ST_GeogFromText(point))).offset(offset).limit(limit)
        return query.all()

    def get_cached_by_location(
        self, db: Session, lat: float, lng: float, radius: int, max_age_days: int = 7
    ) -> Tuple[List[Salon], bool]:
        """
        Returns (salons, is_fresh) where is_fresh=True if data is within max_age_days.
        Uses search_by_location and checks cached_at of the first salon.
        """
        salons = self.search_by_location(db, lat, lng, radius, min_rating=0, limit=1000, offset=0)
        if not salons:
            return [], False
        cutoff = datetime.utcnow() - timedelta(days=max_age_days)
        is_fresh = any(s.cached_at and s.cached_at > cutoff for s in salons)
        return salons, is_fresh

    def get_by_google_place_id(self, db: Session, google_place_id: str) -> Optional[Salon]:
        return db.query(self.model).filter(self.model.google_place_id == google_place_id).first()

    def upsert_from_google(self, db: Session, salon_data: dict) -> Salon:
        existing = self.get_by_google_place_id(db, salon_data["google_place_id"])
        if existing:
            for key, value in salon_data.items():
                setattr(existing, key, value)
            existing.cached_at = datetime.utcnow()
            db.flush()
            return existing
        else:
            return self.create(db, **salon_data)

    def update_rating(self, db: Session, salon_id: int, new_avg_rating: float, new_count: int):
        db.query(self.model).filter(self.model.id == salon_id).update({
            "rating": new_avg_rating,
            "rating_count": new_count
        })
        db.flush()