"""
Tasks for Pull Request status tracking.
Called directly as functions (no Celery).
"""
import logging
import asyncio
from datetime import datetime
from app.db.base import SessionLocal
from app.models.contribution import Contribution, ContributionStatus
from app.models.issue import Issue, IssueStatus
from app.services.github_service import GitHubService

logger = logging.getLogger(__name__)


def update_pr_status_task(contribution_id: int):
    """Update the status of a specific pull request."""
    logger.info(f"Updating PR status for contribution {contribution_id}")
    db = SessionLocal()
    try:
        contribution = db.query(Contribution).filter(Contribution.id == contribution_id).first()
        if not contribution:
            return {"success": False, "error": "Contribution not found"}

        github_service = GitHubService()

        async def check_pr():
            try:
                pr_info = await github_service.validate_pull_request(
                    pr_url=contribution.pr_url, expected_user=None
                )
                old_status = contribution.status
                if pr_info.merged:
                    contribution.status = ContributionStatus.MERGED
                    contribution.merged_at = pr_info.merged_at or datetime.utcnow()
                    issue = db.query(Issue).filter(Issue.id == contribution.issue_id).first()
                    if issue:
                        issue.status = IssueStatus.COMPLETED
                elif pr_info.state == "closed":
                    contribution.status = ContributionStatus.CLOSED
                elif pr_info.state == "open" and contribution.status != ContributionStatus.SUBMITTED:
                    contribution.status = ContributionStatus.SUBMITTED
                db.commit()
                await github_service.close()
                return {"success": True, "contribution_id": contribution_id,
                        "old_status": old_status.value, "new_status": contribution.status.value}
            except Exception as e:
                await github_service.close()
                raise e

        return asyncio.run(check_pr())
    except Exception as e:
        logger.error(f"Failed to update PR status: {str(e)}")
        db.rollback()
        return {"success": False, "error": str(e)}
    finally:
        db.close()
