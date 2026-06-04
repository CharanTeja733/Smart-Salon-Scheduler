from .base import BaseRepository
from app.models.audit_log import AuditLog

class AuditLogRepository(BaseRepository[AuditLog]):
    def __init__(self):
        super().__init__(AuditLog)

    def log_change(
        self, db, entity_type: str, entity_id: int, action: str,
        old_values: dict = None, new_values: dict = None,
        ip_address: str = None, user_agent: str = None
    ) -> AuditLog:
        return self.create(
            db,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent
        )