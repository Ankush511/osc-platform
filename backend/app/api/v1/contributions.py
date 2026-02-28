"""
Contribution and PR validation API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import hmac
import hashlib

from app.api.dependencies import get_db
from app.services.contribution_service import ContributionService
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
    contribution_service: ContributionService = Depends(get_contribution_service)
):
    """
    Submit a pull request for validation.
    
    This endpoint:
    1. Validates that the issue is claimed by the user
    2. Verifies the PR exists and is created by the user
    3. Checks if the PR is linked to the correct issue
    4. Creates a contribution record
    5. Updates issue status to completed
    6. Awards points based on PR status
    
    Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6
    """
    result = await contribution_service.submit_pr(
        issue_id=request.issue_id,
        pr_url=request.pr_url,
        user_id=request.user_id
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
