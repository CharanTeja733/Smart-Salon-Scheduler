from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class WaitlistEntry(Base):
    __tablename__ = "waitlist"

    id = Column(Integer, primary_key=True, index=True)
    practitioner_id = Column(Integer, ForeignKey("practitioners.id", ondelete="CASCADE"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    preferred_date_start = Column(DateTime(timezone=True))
    preferred_date_end = Column(DateTime(timezone=True))
    preferred_service_type = Column(String(100))
    status = Column(String(20), nullable=False, default="active")
    notified_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    practitioner = relationship("Practitioner", back_populates="waitlist_entries")
    customer = relationship("Customer", back_populates="waitlist_entries")

    __table_args__ = (
        CheckConstraint("status IN ('active','notified','booked','expired')", name='check_waitlist_status'),
        Index('idx_waitlist_practitioner_active', 'practitioner_id', 'status', 'preferred_date_start'),
    )
