from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Time,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Practitioner(Base):
    __tablename__ = "practitioners"

    id = Column(Integer, primary_key=True, index=True)
    salon_id = Column(Integer, ForeignKey("salons.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True)
    phone = Column(String(50))
    specialty = Column(String(100))
    experience_years = Column(Integer, default=0)
    bio = Column(String(500))
    photo_url = Column(String(500))
    base_price = Column(Float, default=50.0)
    service_prices = Column(JSON, default=dict)
    specializations = Column(JSON, default=list)
    rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)
    default_opening_hours = Column(JSON)
    lunch_break_start = Column(Time)
    lunch_break_end = Column(Time)
    off_days = Column(JSON, default=list)          # e.g., ["sunday", "2024-12-25"]
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    salon = relationship("Salon", backref="practitioners")
    appointments = relationship("Appointment", back_populates="practitioner", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="practitioner", cascade="all, delete-orphan")
    waitlist_entries = relationship("WaitlistEntry", back_populates="practitioner")

    __table_args__ = (
        Index('idx_practitioners_salon_id', 'salon_id'),
        Index('idx_practitioners_rating', rating.desc()),
        Index('idx_practitioners_specializations', specializations, postgresql_using='gin'),
    )
