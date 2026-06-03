# backend/app/models/customer.py
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255))
    name = Column(String(100), nullable=False)
    preferred_stylist_id = Column(Integer, ForeignKey("practitioners.id"), nullable=True)
    preferred_service_types = Column(JSON, default=list)
    total_appointments = Column(Integer, default=0)
    total_spent = Column(Float, default=0.0)
    no_show_count = Column(Integer, default=0)
    last_booking_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    appointments = relationship("Appointment", back_populates="customer")
    reviews = relationship("Review", back_populates="customer")
    waitlist_entries = relationship("WaitlistEntry", back_populates="customer")

    __table_args__ = (
        Index('idx_customers_phone', 'phone'),
        Index('idx_customers_preferred_stylist', 'preferred_stylist_id'),
    )