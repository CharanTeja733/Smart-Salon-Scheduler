from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    practitioner_id = Column(Integer, ForeignKey("practitioners.id", ondelete="RESTRICT"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    service_duration = Column(Integer, nullable=False, default=30)
    service_type = Column(String(100))
    status = Column(String(20), nullable=False, default="pending")
    price = Column(Float, nullable=False)
    deposit_amount = Column(Float, nullable=False)
    deposit_paid = Column(Boolean, default=False)
    deposit_payment_intent_id = Column(String(255))
    final_payment_intent_id = Column(String(255))
    cancellation_fee = Column(Float, default=0.0)
    refund_amount = Column(Float, default=0.0)
    customer_notes = Column(Text)
    internal_notes = Column(Text)
    cancelled_at = Column(DateTime(timezone=True))
    cancellation_reason = Column(String(500))
    reminder_sent = Column(Boolean, default=False)
    hold_expires_at = Column(DateTime(timezone=True))
    booked_at = Column(DateTime(timezone=True), server_default=func.now())
    confirmed_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))

    # Relationships
    practitioner = relationship("Practitioner", back_populates="appointments")
    customer = relationship("Customer", back_populates="appointments")
    review = relationship("Review", back_populates="appointment", uselist=False)

    __table_args__ = (
        # Critical: prevents double booking at database level
        UniqueConstraint('practitioner_id', 'start_time', name='unique_practitioner_slot'),
        CheckConstraint('service_duration IN (30,60,90,120)', name='check_duration'),
        CheckConstraint("status IN ('pending','confirmed','completed','cancelled','no_show')", name='check_status'),
        Index('idx_appointments_customer_status', 'customer_id', 'status', 'start_time'),
        Index('idx_appointments_reminder', 'reminder_sent', 'start_time', postgresql_where=("status = 'confirmed'")),
        Index('idx_appointments_hold', 'hold_expires_at', postgresql_where=("status = 'pending'")),
    )
