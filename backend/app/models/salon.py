from geoalchemy2 import Geography
from sqlalchemy import Column, DateTime, Float, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Salon(Base):
    __tablename__ = "salons"

    id = Column(Integer, primary_key=True, index=True)
    google_place_id = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    address = Column(String(500), nullable=False)
    latitude = Column(Float(precision=10), nullable=False)
    longitude = Column(Float(precision=11), nullable=False)
    phone = Column(String(50))
    rating = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    opening_hours = Column(JSONB, nullable=False)
    photo_reference = Column(Text)
    cached_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # PostGIS geography column for distance queries
    location = Column(Geography('POINT', srid=4326))

    # Add relationship to match Practitioner's back_populates
    practitioners = relationship("Practitioner", back_populates="salon", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_salons_google_place_id', 'google_place_id'),
        Index('idx_salons_rating', rating.desc()),
        # Index('idx_salons_location', location, postgresql_using='gist'),
    )