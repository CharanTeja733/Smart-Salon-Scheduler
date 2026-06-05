from datetime import datetime, timedelta

from celery import shared_task

from app.database import SessionLocal
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.audit_log_repository import AuditLogRepository


@shared_task
def cleanup_expired_holds():
    """Mark pending appointments with expired hold as cancelled."""
    db = SessionLocal()
    try:
        apt_repo = AppointmentRepository()
        count = apt_repo.release_expired_holds(db)
        db.commit()
        return {"status": "completed", "cancelled_count": count}
    finally:
        db.close()

@shared_task
def cleanup_old_logs(days_to_keep: int = 30):
    """Delete audit logs older than specified days."""
    db = SessionLocal()
    try:
        cutoff = datetime.utcnow() - timedelta(days=days_to_keep)
        audit_repo = AuditLogRepository()
        # Custom delete method
        deleted = db.query(audit_repo.model).filter(audit_repo.model.created_at < cutoff).delete()
        db.commit()
        return {"status": "completed", "deleted_logs": deleted}
    finally:
        db.close()
