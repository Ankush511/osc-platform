"""
Background tasks for issue claim management.
Called directly as functions (no Celery).
"""
import logging
from app.db.base import SessionLocal
from app.services.issue_service import IssueService
from app.core.config import settings

logger = logging.getLogger(__name__)


def auto_release_expired_claims_task():
    """Release expired claims and send notifications."""
    logger.info("Starting auto-release of expired claims")
    db = SessionLocal()
    try:
        issue_service = IssueService(db=db)
        result = issue_service.auto_release_expired_claims()
        logger.info(f"Auto-release completed: {result.released_count} issues released")
        return {"released_count": result.released_count, "issue_ids": result.issue_ids, "errors": result.errors}
    except Exception as e:
        logger.error(f"Auto-release task failed: {str(e)}")
        raise
    finally:
        db.close()


def send_expiration_reminders_task():
    """Send reminders for expiring claims."""
    logger.info("Starting expiration reminder check")
    db = SessionLocal()
    try:
        issue_service = IssueService(db=db)
        expiring_issues = issue_service.get_expiring_claims(hours_threshold=settings.CLAIM_GRACE_PERIOD_HOURS)
        logger.info(f"Found {len(expiring_issues)} claims expiring soon")
        return {"expiring_count": len(expiring_issues), "issue_ids": [i.id for i in expiring_issues]}
    except Exception as e:
        logger.error(f"Expiration reminder task failed: {str(e)}")
        raise
    finally:
        db.close()
