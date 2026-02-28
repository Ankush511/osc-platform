"""
Background tasks package

This package contains all Celery background tasks for the application:
- claim_tasks: Issue claim management and expiration handling
- sync_tasks: GitHub issue synchronization
- pr_tasks: Pull request status tracking
- monitoring: Task monitoring and health checks
"""

# Import all tasks to ensure they're registered with Celery
from app.tasks.claim_tasks import (
    auto_release_expired_claims_task,
    send_expiration_reminders_task,
    release_specific_claim_task
)

from app.tasks.sync_tasks import (
    sync_all_repositories_task,
    sync_specific_repositories_task,
    check_closed_issues_task
)

from app.tasks.pr_tasks import (
    update_pr_status_task,
    check_all_open_prs_task,
    handle_webhook_event_task
)

from app.tasks.monitoring import (
    health_check_task,
    cleanup_old_task_results,
    generate_task_report
)

__all__ = [
    # Claim tasks
    "auto_release_expired_claims_task",
    "send_expiration_reminders_task",
    "release_specific_claim_task",
    # Sync tasks
    "sync_all_repositories_task",
    "sync_specific_repositories_task",
    "check_closed_issues_task",
    # PR tasks
    "update_pr_status_task",
    "check_all_open_prs_task",
    "handle_webhook_event_task",
    # Monitoring tasks
    "health_check_task",
    "cleanup_old_task_results",
    "generate_task_report",
]

