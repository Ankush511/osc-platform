"""
Celery tasks for Pull Request status tracking and updates

Handles PR status updates via GitHub webhooks and periodic checks.
"""
import logging
from typing import Optional
from datetime import datetime
from app.celery_app import celery_app
from app.db.base import SessionLocal
from app.models.contribution import Contribution, ContributionStatus
from app.models.issue import Issue, IssueStatus
from app.services.github_service import GitHubService
from app.core.config import settings

logger = logging.getLogger(__name__)


@celery_app.task(
    name="app.tasks.pr_tasks.update_pr_status_task",
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def update_pr_status_task(self, contribution_id: int):
    """
    Update the status of a specific pull request.
    
    This task is typically triggered by GitHub webhooks when PR status changes
    (opened, merged, closed, etc.).
    
    Args:
        contribution_id: ID of the contribution to update
    """
    logger.info(f"Updating PR status for contribution {contribution_id}")
    
    db = SessionLocal()
    try:
        # Get the contribution
        contribution = db.query(Contribution).filter(
            Contribution.id == contribution_id
        ).first()
        
        if not contribution:
            logger.error(f"Contribution {contribution_id} not found")
            return {
                "success": False,
                "error": "Contribution not found"
            }
        
        # Fetch PR status from GitHub
        import asyncio
        github_service = GitHubService()
        
        async def check_pr():
            try:
                # Extract repo and PR number from URL
                # URL format: https://github.com/owner/repo/pull/123
                parts = contribution.pr_url.split('/')
                repo = f"{parts[-4]}/{parts[-3]}"
                pr_number = int(parts[-1])
                
                # Validate and get PR info
                pr_info = await github_service.validate_pull_request(
                    pr_url=contribution.pr_url,
                    expected_user=None  # We already validated user when created
                )
                
                old_status = contribution.status
                
                # Update contribution status based on PR state
                if pr_info.merged:
                    contribution.status = ContributionStatus.MERGED
                    contribution.merged_at = pr_info.merged_at or datetime.utcnow()
                    
                    # Update issue status to completed
                    issue = db.query(Issue).filter(
                        Issue.id == contribution.issue_id
                    ).first()
                    if issue:
                        issue.status = IssueStatus.COMPLETED
                    
                    logger.info(f"PR {pr_number} merged for contribution {contribution_id}")
                    
                elif pr_info.state == "closed":
                    contribution.status = ContributionStatus.CLOSED
                    logger.info(f"PR {pr_number} closed for contribution {contribution_id}")
                    
                elif pr_info.state == "open":
                    # Keep as submitted
                    if contribution.status != ContributionStatus.SUBMITTED:
                        contribution.status = ContributionStatus.SUBMITTED
                
                db.commit()
                
                await github_service.close()
                
                return {
                    "success": True,
                    "contribution_id": contribution_id,
                    "old_status": old_status.value,
                    "new_status": contribution.status.value,
                    "pr_state": pr_info.state,
                    "merged": pr_info.merged
                }
                
            except Exception as e:
                await github_service.close()
                raise e
        
        result = asyncio.run(check_pr())
        return result
        
    except Exception as e:
        logger.error(f"Failed to update PR status for contribution {contribution_id}: {str(e)}", exc_info=True)
        db.rollback()
        
        try:
            raise self.retry(exc=e)
        except self.MaxRetriesExceededError:
            logger.error(f"Max retries exceeded for PR status update task (contribution {contribution_id})")
            return {
                "success": False,
                "contribution_id": contribution_id,
                "error": str(e),
                "max_retries_exceeded": True
            }
    finally:
        db.close()


@celery_app.task(name="app.tasks.pr_tasks.check_all_open_prs_task")
def check_all_open_prs_task():
    """
    Check status of all open (submitted) pull requests.
    
    This is a periodic task that ensures PR statuses are up-to-date
    even if webhooks fail or are missed.
    
    Runs every 12 hours by default.
    """
    logger.info("Starting check of all open PRs")
    
    db = SessionLocal()
    try:
        # Get all submitted contributions
        open_contributions = db.query(Contribution).filter(
            Contribution.status == ContributionStatus.SUBMITTED
        ).all()
        
        logger.info(f"Found {len(open_contributions)} open PRs to check")
        
        updated_count = 0
        merged_count = 0
        closed_count = 0
        errors = []
        
        for contribution in open_contributions:
            try:
                # Trigger update task for each contribution
                result = update_pr_status_task(contribution.id)
                
                if result.get("success"):
                    updated_count += 1
                    
                    new_status = result.get("new_status")
                    if new_status == ContributionStatus.MERGED.value:
                        merged_count += 1
                    elif new_status == ContributionStatus.CLOSED.value:
                        closed_count += 1
                else:
                    errors.append(f"Contribution {contribution.id}: {result.get('error')}")
                    
            except Exception as e:
                error_msg = f"Failed to check contribution {contribution.id}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        logger.info(
            f"Open PRs check completed: {updated_count} checked, "
            f"{merged_count} merged, {closed_count} closed"
        )
        
        return {
            "success": True,
            "total_checked": len(open_contributions),
            "updated_count": updated_count,
            "merged_count": merged_count,
            "closed_count": closed_count,
            "errors": errors
        }
        
    except Exception as e:
        logger.error(f"Check all open PRs task failed: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()


@celery_app.task(name="app.tasks.pr_tasks.handle_webhook_event_task")
def handle_webhook_event_task(event_type: str, payload: dict):
    """
    Handle GitHub webhook events for PR updates.
    
    This task processes webhook payloads and triggers appropriate actions.
    
    Args:
        event_type: Type of GitHub event (pull_request, issues, etc.)
        payload: Webhook payload from GitHub
    """
    logger.info(f"Processing webhook event: {event_type}")
    
    db = SessionLocal()
    try:
        if event_type == "pull_request":
            # Extract PR information
            pr_data = payload.get("pull_request", {})
            pr_url = pr_data.get("html_url")
            pr_number = pr_data.get("number")
            action = payload.get("action")  # opened, closed, reopened, etc.
            
            logger.info(f"PR webhook: {action} for PR #{pr_number}")
            
            # Find contribution by PR URL
            contribution = db.query(Contribution).filter(
                Contribution.pr_url == pr_url
            ).first()
            
            if not contribution:
                logger.warning(f"No contribution found for PR URL: {pr_url}")
                return {
                    "success": False,
                    "error": "Contribution not found for PR URL"
                }
            
            # Update PR status
            result = update_pr_status_task(contribution.id)
            
            return {
                "success": True,
                "event_type": event_type,
                "action": action,
                "pr_number": pr_number,
                "contribution_id": contribution.id,
                "update_result": result
            }
            
        elif event_type == "issues":
            # Handle issue events (closed, reopened, etc.)
            issue_data = payload.get("issue", {})
            issue_url = issue_data.get("html_url")
            action = payload.get("action")
            
            logger.info(f"Issue webhook: {action} for issue {issue_url}")
            
            # Find issue by GitHub URL
            issue = db.query(Issue).filter(
                Issue.github_url == issue_url
            ).first()
            
            if not issue:
                logger.warning(f"No issue found for URL: {issue_url}")
                return {
                    "success": False,
                    "error": "Issue not found for URL"
                }
            
            # Update issue status based on action
            if action == "closed":
                issue.status = IssueStatus.CLOSED
                db.commit()
                logger.info(f"Issue {issue.id} marked as closed via webhook")
                
            elif action == "reopened":
                # Only reopen if not claimed or completed
                if issue.status == IssueStatus.CLOSED:
                    issue.status = IssueStatus.AVAILABLE
                    db.commit()
                    logger.info(f"Issue {issue.id} marked as available via webhook")
            
            return {
                "success": True,
                "event_type": event_type,
                "action": action,
                "issue_id": issue.id
            }
        
        else:
            logger.info(f"Unhandled webhook event type: {event_type}")
            return {
                "success": True,
                "event_type": event_type,
                "message": "Event type not handled"
            }
        
    except Exception as e:
        logger.error(f"Webhook event handling failed: {str(e)}", exc_info=True)
        db.rollback()
        return {
            "success": False,
            "event_type": event_type,
            "error": str(e)
        }
    finally:
        db.close()
