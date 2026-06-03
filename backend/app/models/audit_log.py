from sqlalchemy import Column, BigInteger, Integer, String, JSON, DateTime, Index
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.sql import func

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(BigInteger, primary_key=True, index=True)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=False)
    action = Column(String(50), nullable=False)
    old_values = Column(JSON)
    new_values = Column(JSON)
    ip_address = Column(INET)
    user_agent = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_audit_logs_entity', 'entity_type', 'entity_id', created_at.desc()),
    )