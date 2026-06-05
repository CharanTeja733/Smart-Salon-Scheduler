from celery import Celery

from app.config import settings

celery_app = Celery(
    "salon_scheduler",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.reminders",
        "app.tasks.payments",
        "app.tasks.cleanup",
        "app.tasks.refresh_data",
    ]
)

# Optional: configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,
    worker_prefetch_multiplier=1,
    result_expires=3600,  # 1 hour
)

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    "cleanup-expired-holds": {
        "task": "app.tasks.cleanup.cleanup_expired_holds",
        "schedule": 300.0,  # every 5 minutes
    },
    "cleanup-old-logs": {
        "task": "app.tasks.cleanup.cleanup_old_logs",
        "schedule": 86400.0,  # daily
    },
    "refresh-salon-cache": {
        "task": "app.tasks.refresh_data.refresh_salon_cache",
        "schedule": 604800.0,  # weekly
    },
}
