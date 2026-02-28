"""
Celery application configuration for background tasks
"""
from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "oscp_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
)

# Configure periodic tasks
celery_app.conf.beat_schedule = {
    "auto-release-expired-claims": {
        "task": "app.tasks.claim_tasks.auto_release_expired_claims_task",
        "schedule": crontab(minute=0),  # Run every hour
    },
    "send-expiration-reminders": {
        "task": "app.tasks.claim_tasks.send_expiration_reminders_task",
        "schedule": crontab(hour="*/6"),  # Run every 6 hours
    },
    "sync-all-repositories": {
        "task": "app.tasks.sync_tasks.sync_all_repositories_task",
        "schedule": crontab(hour="*/6"),  # Run every 6 hours
    },
    "check-closed-issues": {
        "task": "app.tasks.sync_tasks.check_closed_issues_task",
        "schedule": crontab(hour="*/3"),  # Run every 3 hours
    },
    "check-all-open-prs": {
        "task": "app.tasks.pr_tasks.check_all_open_prs_task",
        "schedule": crontab(hour="*/12"),  # Run every 12 hours
    },
}

# Auto-discover tasks
celery_app.autodiscover_tasks(["app.tasks"])
