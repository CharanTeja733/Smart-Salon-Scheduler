from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime, CheckConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id", ondelete="CASCADE"), unique=True, nullable=False)
    practitioner_id = Column(Integer, ForeignKey("practitioners.id", ondelete="CASCADE"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text)
    sentiment_score = Column(Float)      # -1 to 1
    punctuality_rating = Column(Integer)
    quality_rating = Column(Integer)
    value_rating = Column(Integer)
    is_verified = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    appointment = relationship("Appointment", back_populates="review")
    practitioner = relationship("Practitioner", back_populates="reviews")
    customer = relationship("Customer", back_populates="reviews")

    __table_args__ = (
        CheckConstraint('rating BETWEEN 1 AND 5', name='check_rating'),
        CheckConstraint('punctuality_rating BETWEEN 1 AND 5', name='check_punctuality'),
        CheckConstraint('quality_rating BETWEEN 1 AND 5', name='check_quality'),
        CheckConstraint('value_rating BETWEEN 1 AND 5', name='check_value'),
        Index('idx_reviews_practitioner', 'practitioner_id', created_at.desc()),
        Index('idx_reviews_customer', 'customer_id'),
    )