from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.sql import func

from app.database import Base


class AvailabilityException(Base):
    __tablename__ = "availability_exceptions"

    id = Column(Integer, primary_key=True, index=True)
    practitioner_id = Column(Integer, ForeignKey("practitioners.id", ondelete="CASCADE"), nullable=False)
    exception_date = Column(Date, nullable=False)
    is_working = Column(Boolean, default=False)   # False = unavailable (sick/leave)
    reason_code = Column(String(50))  # 'sick', 'emergency', 'other', 'private'
    reason_text = Column(String(255))  # Optional custom reason
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('practitioner_id', 'exception_date', name='unique_practitioner_exception'),
    )
