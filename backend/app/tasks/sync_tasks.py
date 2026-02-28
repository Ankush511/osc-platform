"""
Celery tasks for GitHub issue synchronization

Implements requirements 7.1, 7.2, 7.3:
- Fetch new issues from configured repositories
- Check if previously displayed issues are still open
- Remove closed issues from available issues
"""
import logging
from typing import List, Optional
from app.celery_app import celery_app
from app.db.base import SessionLocal
from app.services.issue_service import IssueService
from app.core.config import settings

logger = logging.getLogger(__name__)


@celery_app.task(
    name="app.tasks.sync_tasks.sync_all_repositories_task",
    bind=True,
    max_retries=3,
    default_retry_delay=300  # 5 minutes
)
def sync_all_repositories_task(self):
    """
    Synchronize issues from all active repositories.
    
    This task:
    - Fetches new issues from configured repositories (Req 7.1)
    - Checks if previously displayed issues are still open (Req 7.2)
    - Removes closed issues from available issues (Req 7.3)
    
    Runs on a scheduled basis (every 6 hours by default).
    """
    logger.info("Starting full repository synchronization")
    
    db = SessionLocal()
    try:
        issue_service = IssueService(db=db)
        
        # Run synchronization for all active repositories
        import asyncio
        result = asyncio.run(issue_service.sync_issues())
        
        logger.info(
            f"Sync completed: {result.repositories_synced} repos synced, "
            f"{result.issues_added} issues added, "
            f"{result.issues_updated} issues updated, "
            f"{result.issues_closed} issues closed, "
            f"Duration: {result.sync_duration_seconds:.2f}s"
        )
        
        if result.errors:
            logger.warning(f"Sync completed with {len(result.errors)} errors")
            for error in result.errors:
                logger.error(f"Sync error: {error}")
        
        return {
            "success": True,
            "repositories_synced": result.repositories_synced,
            "issues_added": result.issues_added,
            "issues_updated": result.issues_updated,
            "issues_closed": result.issues_closed,
            "errors": result.errors,
            "duration_seconds": result.sync_duration_seconds
        }
        
    except Exception as e:
        logger.error(f"Repository sync task failed: {str(e)}", exc_info=True)
        
        # Retry the task if it fails
        try:
            raise self.retry(exc=e)
        except self.MaxRetriesExceededError:
            logger.error("Max retries exceeded for repository sync task")
            return {
                "success": False,
                "error": str(e),
                "max_retries_exceeded": True
            }
    finally:
        db.close()


@celery_app.task(
    name="app.tasks.sync_tasks.sync_specific_repositories_task",
    bind=True,
    max_retries=3,
    default_retry_delay=180  # 3 minutes
)
def sync_specific_repositories_task(self, repository_ids: List[int]):
    """
    Synchronize issues from specific repositories.
    
    Args:
        repository_ids: List of repository IDs to synchronize
    
    This allows for targeted synchronization of specific repositories,
    useful for manual triggers or when new repositories are added.
    """
    logger.info(f"Starting synchronization for repositories: {repository_ids}")
    
    db = SessionLocal()
    try:
        issue_service = IssueService(db=db)
        
        # Run synchronization for specific repositories
        import asyncio
        result = asyncio.run(issue_service.sync_issues(repository_ids=repository_ids))
        
        logger.info(
            f"Specific sync completed: {result.repositories_synced} repos synced, "
            f"{result.issues_added} issues added, "
            f"{result.issues_updated} issues updated, "
            f"{result.issues_closed} issues closed"
        )
        
        return {
            "success": True,
            "repository_ids": repository_ids,
            "repositories_synced": result.repositories_synced,
            "issues_added": result.issues_added,
            "issues_updated": result.issues_updated,
            "issues_closed": result.issues_closed,
            "errors": result.errors
        }
        
    except Exception as e:
        logger.error(f"Specific repository sync task failed: {str(e)}", exc_info=True)
        
        try:
            raise self.retry(exc=e)
        except self.MaxRetriesExceededError:
            logger.error("Max retries exceeded for specific repository sync task")
            return {
                "success": False,
                "repository_ids": repository_ids,
                "error": str(e),
                "max_retries_exceeded": True
            }
    finally:
        db.close()


@celery_app.task(name="app.tasks.sync_tasks.check_closed_issues_task")
def check_closed_issues_task():
    """
    Check if open issues in the database are still open on GitHub.
    
    This is a lightweight task that specifically checks issue status
    without doing a full sync. Useful for quick status updates.
    
    Implements requirement 7.2 and 7.3.
    """
    logger.info("Starting closed issues check")
    
    db = SessionLocal()
    try:
        from app.models.issue import Issue, IssueStatus
        from app.services.github_service import GitHubService
        import asyncio
        
        # Get all non-closed issues
        open_issues = db.query(Issue).filter(
            Issue.status.in_([IssueStatus.AVAILABLE, IssueStatus.CLAIMED])
        ).all()
        
        logger.info(f"Checking {len(open_issues)} open issues")
        
        github_service = GitHubService()
        closed_count = 0
        errors = []
        
        async def check_issues():
            nonlocal closed_count, errors
            
            for issue in open_issues:
                try:
                    # Extract repo and issue number from GitHub URL
                    # URL format: https://github.com/owner/repo/issues/123
                    parts = issue.github_url.split('/')
                    repo = f"{parts[-4]}/{parts[-3]}"
                    issue_number = int(parts[-1])
                    
                    # Check issue status on GitHub
                    status = await github_service.check_issue_status(repo, issue_number)
                    
                    if status == "closed":
                        logger.info(f"Issue {issue.id} is closed on GitHub, updating status")
                        issue.status = IssueStatus.CLOSED
                        closed_count += 1
                        
                except Exception as e:
                    error_msg = f"Failed to check issue {issue.id}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
            
            await github_service.close()
        
        asyncio.run(check_issues())
        
        if closed_count > 0:
            db.commit()
        
        logger.info(f"Closed issues check completed: {closed_count} issues closed")
        
        return {
            "success": True,
            "issues_checked": len(open_issues),
            "issues_closed": closed_count,
            "errors": errors
        }
        
    except Exception as e:
        logger.error(f"Closed issues check task failed: {str(e)}", exc_info=True)
        db.rollback()
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()
