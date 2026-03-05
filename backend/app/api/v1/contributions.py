"""
Contribution and PR validation API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import hmac
import hashlib

from app.api.dependencies import get_db, get_current_user
from app.services.contribution_service import ContributionService
from app.models.user import User
from app.schemas.contribution import (
    SubmitPRRequest,
    SubmissionResult,
    ContributionResponse,
    ContributionStats,
    PRStatusUpdate
)
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/contributions", tags=["contributions"])


def get_contribution_service(
    db: Session = Depends(get_db)
) -> ContributionService:
    """Get contribution service instance"""
    return ContributionService(db=db)


@router.post("/submit", response_model=SubmissionResult)
async def submit_pull_request(
    request: SubmitPRRequest,
    current_user: User = Depends(get_current_user),
    contribution_service: ContributionService = Depends(get_contribution_service)
):
    """
    Submit a pull request for validation.
    """
    result = await contribution_service.submit_pr(
        issue_id=request.issue_id,
        pr_url=request.pr_url,
        user_id=current_user.id
    )
    
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    
    return result


@router.get("/user/{user_id}", response_model=List[ContributionResponse])
async def get_user_contributions(
    user_id: int,
    status: Optional[str] = None,
    contribution_service: ContributionService = Depends(get_contribution_service)
):
    """
    Get all contributions for a user.
    
    Optionally filter by status (submitted, merged, closed).
    """
    from app.models.contribution import ContributionStatus
    
    status_filter = None
    if status:
        try:
            status_filter = ContributionStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: submitted, merged, closed"
            )
    
    contributions = contribution_service.get_user_contributions(
        user_id=user_id,
        status=status_filter
    )
    
    # Convert to response format
    responses = []
    for contribution in contributions:
        response_dict = {
            "id": contribution.id,
            "user_id": contribution.user_id,
            "issue_id": contribution.issue_id,
            "pr_url": contribution.pr_url,
            "pr_number": contribution.pr_number,
            "status": contribution.status.value,
            "submitted_at": contribution.submitted_at,
            "merged_at": contribution.merged_at,
            "points_earned": contribution.points_earned,
            "issue_title": contribution.issue.title if contribution.issue else None,
            "repository_name": contribution.issue.repository.full_name if contribution.issue and contribution.issue.repository else None
        }
        responses.append(ContributionResponse(**response_dict))
    
    return responses


@router.get("/user/{user_id}/stats", response_model=ContributionStats)
async def get_user_contribution_stats(
    user_id: int,
    contribution_service: ContributionService = Depends(get_contribution_service)
):
    """
    Get contribution statistics for a user.
    
    Returns:
    - Total contributions
    - Submitted, merged, and closed PR counts
    - Total points earned
    - Contributions by programming language
    - Contributions by repository
    
    Requirement: 6.1, 6.2
    """
    stats = contribution_service.get_user_stats(user_id)
    return stats


@router.get("/{contribution_id}", response_model=ContributionResponse)
async def get_contribution(
    contribution_id: int,
    contribution_service: ContributionService = Depends(get_contribution_service)
):
    """
    Get a specific contribution by ID.
    """
    contribution = contribution_service.get_contribution_by_id(contribution_id)
    
    if not contribution:
        raise HTTPException(status_code=404, detail="Contribution not found")
    
    response_dict = {
        "id": contribution.id,
        "user_id": contribution.user_id,
        "issue_id": contribution.issue_id,
        "pr_url": contribution.pr_url,
        "pr_number": contribution.pr_number,
        "status": contribution.status.value,
        "submitted_at": contribution.submitted_at,
        "merged_at": contribution.merged_at,
        "points_earned": contribution.points_earned,
        "issue_title": contribution.issue.title if contribution.issue else None,
        "repository_name": contribution.issue.repository.full_name if contribution.issue and contribution.issue.repository else None
    }
    
    return ContributionResponse(**response_dict)


@router.post("/webhook/github")
async def github_webhook_handler(
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None),
    contribution_service: ContributionService = Depends(get_contribution_service)
):
    """
    Handle GitHub webhook events for PR status updates.
    
    This endpoint receives webhook events from GitHub when:
    - A PR is opened
    - A PR is closed
    - A PR is merged
    
    It updates the contribution status and awards points accordingly.
    
    Requirement: 5.5
    """
    # Get raw body for signature verification
    body = await request.body()
    
    # Verify webhook signature if secret is configured
    if hasattr(settings, 'GITHUB_WEBHOOK_SECRET') and settings.GITHUB_WEBHOOK_SECRET:
        if not x_hub_signature_256:
            raise HTTPException(status_code=401, detail="Missing signature")
        
        # Verify signature
        expected_signature = "sha256=" + hmac.new(
            settings.GITHUB_WEBHOOK_SECRET.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(x_hub_signature_256, expected_signature):
            raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Parse webhook payload
    payload = await request.json()
    
    # Handle pull_request events
    if "pull_request" in payload:
        pr = payload["pull_request"]
        action = payload.get("action", "")
        
        pr_url = pr.get("html_url", "")
        pr_number = pr.get("number", 0)
        merged = pr.get("merged", False)
        merged_at = pr.get("merged_at")
        
        # Update contribution status
        success = await contribution_service.update_pr_status(
            pr_url=pr_url,
            pr_number=pr_number,
            action=action,
            merged=merged,
            merged_at=merged_at
        )
        
        if success:
            logger.info(f"Webhook processed: PR #{pr_number}, action={action}, merged={merged}")
            return {"status": "success", "message": "Webhook processed"}
        else:
            logger.warning(f"Webhook processed but no contribution found: PR #{pr_number}")
            return {"status": "no_action", "message": "No matching contribution found"}
    
    return {"status": "ignored", "message": "Event type not handled"}


# ── Dev-only: simulate full PR submit + merge flow ──────────────────
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from app.models.contribution import Contribution, ContributionStatus
from app.models.issue import Issue, IssueStatus
from app.services.achievement_service import AchievementService


class DevSimulatePRRequest(BaseModel):
    issue_id: int = Field(..., description="ID of the claimed issue")
    simulate_merge: bool = Field(True, description="If true, immediately mark PR as merged")


@router.post("/dev/simulate-pr")
async def dev_simulate_pr(
    request: DevSimulatePRRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    DEV ONLY — Simulate a PR submission and optional merge without hitting GitHub API.
    Useful for testing the full flow: contribution → points → achievements → dashboard.
    """
    if settings.ENVIRONMENT not in ("development", "dev", "local"):
        raise HTTPException(status_code=403, detail="This endpoint is only available in development")

    issue = db.query(Issue).filter(Issue.id == request.issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    if issue.claimed_by != current_user.id:
        raise HTTPException(status_code=400, detail="Issue is not claimed by you")

    # Check for existing contribution
    existing = db.query(Contribution).filter(
        Contribution.issue_id == issue.id,
        Contribution.user_id == current_user.id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="A contribution already exists for this issue")

    now = datetime.now(timezone.utc)
    is_merged = request.simulate_merge

    contribution = Contribution(
        user_id=current_user.id,
        issue_id=issue.id,
        pr_url=f"https://github.com/mock/repo/pull/{issue.id}",
        pr_number=issue.id,
        status=ContributionStatus.MERGED if is_merged else ContributionStatus.SUBMITTED,
        submitted_at=now,
        merged_at=now if is_merged else None,
        points_earned=100 if is_merged else 10,
    )
    db.add(contribution)

    issue.status = IssueStatus.COMPLETED

    current_user.total_contributions += 1
    if is_merged:
        current_user.merged_prs += 1

    db.commit()
    db.refresh(contribution)

    # Invalidate issue caches so list/detail pages show updated status
    from app.services.cache_service import cache_service
    cache_service.delete_pattern("issues:*")

    # Check achievements
    achievement_service = AchievementService(db)
    newly_awarded = achievement_service.check_and_award_achievements(current_user.id)

    return {
        "success": True,
        "contribution_id": contribution.id,
        "status": contribution.status.value,
        "points_earned": contribution.points_earned,
        "is_merged": is_merged,
        "achievements_earned": [a.name for a in newly_awarded],
        "message": f"Simulated PR {'merged' if is_merged else 'submitted'} successfully",
    }
