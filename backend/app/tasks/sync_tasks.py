"""
Tasks for GitHub issue synchronization.
Called directly as functions (no Celery).
"""
import logging
import asyncio
from app.db.base import SessionLocal
from app.services.issue_service import IssueService
from app.tasks.difficulty_tasks import refine_difficulty_for_issues

logger = logging.getLogger(__name__)


def sync_all_repositories_task():
    """Synchronize issues from all active repositories."""
    logger.info("Starting full repository synchronization")
    db = SessionLocal()
    try:
        issue_service = IssueService(db=db)
        result = asyncio.run(issue_service.sync_issues())
        logger.info(f"Sync completed: {result.repositories_synced} repos synced")
        # Refine difficulty for newly added issues via AI
        if result.new_issue_ids:
            logger.info(f"Refining difficulty for {len(result.new_issue_ids)} new issues")
            refine_difficulty_for_issues(result.new_issue_ids)
        return {"success": True, "repositories_synced": result.repositories_synced,
                "issues_added": result.issues_added, "issues_updated": result.issues_updated,
                "issues_closed": result.issues_closed, "errors": result.errors}
    except Exception as e:
        logger.error(f"Repository sync task failed: {str(e)}")
        return {"success": False, "error": str(e)}
    finally:
        db.close()


def check_closed_issues_task():
    """Check if open issues in the database are still open on GitHub."""
    logger.info("Starting closed issues check")
    db = SessionLocal()
    try:
        from app.models.issue import Issue, IssueStatus
        from app.services.github_service import GitHubService

        open_issues = db.query(Issue).filter(
            Issue.status.in_([IssueStatus.AVAILABLE, IssueStatus.CLAIMED])
        ).all()
        logger.info(f"Checking {len(open_issues)} open issues")

        github_service = GitHubService()
        closed_count = 0

        async def check_issues():
            nonlocal closed_count
            for issue in open_issues:
                try:
                    parts = issue.github_url.split('/')
                    repo = f"{parts[-4]}/{parts[-3]}"
                    issue_number = int(parts[-1])
                    status = await github_service.check_issue_status(repo, issue_number)
                    if status == "closed":
                        issue.status = IssueStatus.CLOSED
                        closed_count += 1
                except Exception as e:
                    logger.error(f"Failed to check issue {issue.id}: {str(e)}")
            await github_service.close()

        asyncio.run(check_issues())
        if closed_count > 0:
            db.commit()
        return {"success": True, "issues_checked": len(open_issues), "issues_closed": closed_count}
    except Exception as e:
        logger.error(f"Closed issues check failed: {str(e)}")
        db.rollback()
        return {"success": False, "error": str(e)}
    finally:
        db.close()
