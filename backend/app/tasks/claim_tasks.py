"""
Celery tasks for issue claim management
"""
import logging
from app.celery_app import celery_app
from app.db.base import SessionLocal
from app.services.issue_service import IssueService
from app.core.config import settings

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.claim_tasks.auto_release_expired_claims_task")
def auto_release_expired_claims_task():
    """
    Background task to automatically release expired claims.
    
    Runs every hour to check for and release claims that have exceeded
    their deadline. Sends email notifications to affected users.
    """
    logger.info("Starting auto-release of expired claims")
    
    db = SessionLocal()
    try:
        from app.services.email_service import EmailService
        from app.models.user import User
        
        issue_service = IssueService(db=db)
        email_service = EmailService()
        
        # Get issues before releasing to send notifications
        from app.models.issue import Issue, IssueStatus
        from datetime import datetime
        
        now = datetime.utcnow()
        expired_issues = db.query(Issue).filter(
            Issue.status == IssueStatus.CLAIMED,
            Issue.claim_expires_at.isnot(None),
            Issue.claim_expires_at < now
        ).all()
        
        # Store user-issue mapping for notifications
        notifications = []
        for issue in expired_issues:
            if issue.claimed_by:
                user = db.query(User).filter(User.id == issue.claimed_by).first()
                if user and user.email:
                    notifications.append({
                        "user_email": user.email,
                        "user_name": user.full_name or user.github_username,
                        "issue_title": issue.title,
                        "issue_url": issue.github_url
                    })
        
        # Release expired claims
        result = issue_service.auto_release_expired_claims()
        
        logger.info(
            f"Auto-release completed: {result.released_count} issues released. "
            f"Errors: {len(result.errors)}"
        )
        
        # Send notifications
        emails_sent = 0
        email_errors = []
        
        for notification in notifications:
            try:
                success = email_service.send_claim_released_notification(**notification)
                if success:
                    emails_sent += 1
                else:
                    email_errors.append(f"Failed to send to {notification['user_email']}")
            except Exception as e:
                error_msg = f"Email error for {notification['user_email']}: {str(e)}"
                logger.error(error_msg)
                email_errors.append(error_msg)
        
        if result.errors:
            for error in result.errors:
                logger.error(f"Auto-release error: {error}")
        
        return {
            "released_count": result.released_count,
            "issue_ids": result.issue_ids,
            "emails_sent": emails_sent,
            "email_errors": email_errors,
            "errors": result.errors
        }
        
    except Exception as e:
        logger.error(f"Auto-release task failed: {str(e)}")
        raise
    finally:
        db.close()


@celery_app.task(name="app.tasks.claim_tasks.send_expiration_reminders_task")
def send_expiration_reminders_task():
    """
    Background task to send reminders for expiring claims.
    
    Runs every 6 hours to notify users about claims expiring within
    the grace period (24 hours by default).
    """
    logger.info("Starting expiration reminder check")
    
    db = SessionLocal()
    try:
        from app.services.email_service import EmailService
        from app.models.user import User
        from datetime import datetime
        
        issue_service = IssueService(db=db)
        email_service = EmailService()
        
        expiring_issues = issue_service.get_expiring_claims(
            hours_threshold=settings.CLAIM_GRACE_PERIOD_HOURS
        )
        
        logger.info(f"Found {len(expiring_issues)} claims expiring soon")
        
        emails_sent = 0
        errors = []
        
        for issue in expiring_issues:
            try:
                # Get user information
                user = db.query(User).filter(User.id == issue.claimed_by).first()
                
                if not user or not user.email:
                    logger.warning(f"No email found for user {issue.claimed_by}")
                    continue
                
                # Calculate hours remaining
                hours_remaining = int(
                    (issue.claim_expires_at - datetime.utcnow()).total_seconds() / 3600
                )
                
                # Send reminder email
                success = email_service.send_claim_expiration_reminder(
                    user_email=user.email,
                    user_name=user.full_name or user.github_username,
                    issue_title=issue.title,
                    issue_url=issue.github_url,
                    expires_at=issue.claim_expires_at,
                    hours_remaining=max(1, hours_remaining)
                )
                
                if success:
                    emails_sent += 1
                    logger.info(f"Sent expiration reminder to {user.email} for issue {issue.id}")
                else:
                    errors.append(f"Failed to send email to {user.email} for issue {issue.id}")
                    
            except Exception as e:
                error_msg = f"Error sending reminder for issue {issue.id}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        return {
            "expiring_count": len(expiring_issues),
            "issue_ids": [issue.id for issue in expiring_issues],
            "emails_sent": emails_sent,
            "errors": errors
        }
        
    except Exception as e:
        logger.error(f"Expiration reminder task failed: {str(e)}")
        raise
    finally:
        db.close()


@celery_app.task(name="app.tasks.claim_tasks.release_specific_claim_task")
def release_specific_claim_task(issue_id: int, user_id: int, force: bool = False):
    """
    Background task to release a specific claim.
    
    Can be used for manual admin actions or scheduled releases.
    
    Args:
        issue_id: ID of the issue to release
        user_id: ID of the user releasing (or admin)
        force: If True, bypasses ownership check
    """
    logger.info(f"Releasing claim for issue {issue_id} by user {user_id}")
    
    db = SessionLocal()
    try:
        issue_service = IssueService(db=db)
        result = issue_service.release_issue(issue_id, user_id, force=force)
        
        if result.success:
            logger.info(f"Successfully released issue {issue_id}")
        else:
            logger.warning(f"Failed to release issue {issue_id}: {result.message}")
        
        return {
            "success": result.success,
            "message": result.message,
            "issue_id": result.issue_id
        }
        
    except Exception as e:
        logger.error(f"Release claim task failed: {str(e)}")
        raise
    finally:
        db.close()
