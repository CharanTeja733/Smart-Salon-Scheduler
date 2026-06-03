from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from geoalchemy2 import Geography

Base = declarative_base()

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
    opening_hours = Column(JSON, nullable=False)
    photo_reference = Column(String(255))
    cached_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # PostGIS geography column for distance queries
    location = Column(Geography('POINT', srid=4326))

    __table_args__ = (
        Index('idx_salons_google_place_id', 'google_place_id'),
        Index('idx_salons_rating', rating.desc()),
        Index('idx_salons_location', location, postgresql_using='gist'),
    )