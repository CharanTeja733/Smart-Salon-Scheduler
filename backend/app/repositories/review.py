from typing import List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.review import Review

from .base import BaseRepository


class ReviewRepository(BaseRepository[Review]):
    def __init__(self):
        super().__init__(Review)

    def get_by_appointment(self, db: Session, appointment_id: int) -> Optional[Review]:
        return db.query(self.model).filter(self.model.appointment_id == appointment_id).first()

    def get_by_practitioner(self, db: Session, practitioner_id: int, limit: int = 50) -> List[Review]:
        return db.query(self.model).filter(
            self.model.practitioner_id == practitioner_id
        ).order_by(self.model.created_at.desc()).limit(limit).all()

    def get_average_rating_for_practitioner(self, db: Session, practitioner_id: int) -> Tuple[float, int]:
        result = db.query(func.avg(self.model.rating), func.count(self.model.id)).filter(
            self.model.practitioner_id == practitioner_id
        ).first()
        return (float(result[0] or 0.0), result[1] or 0)

    def create_with_sentiment(self, db: Session, **kwargs) -> Review:
        from textblob import TextBlob
        comment = kwargs.get("comment", "")
        if comment:
            sentiment = TextBlob(comment).sentiment.polarity
            kwargs["sentiment_score"] = sentiment
        return self.create(db, **kwargs)
