"""
Issue discovery and filtering API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import redis
import math

from app.api.dependencies import get_db
from app.services.issue_service import IssueService
from app.schemas.issue import (
    IssueResponse,
    PaginatedIssuesResponse,
    IssueFilters,
    PaginationParams,
    SyncResult,
    IssueSearchRequest,
    ClaimIssueRequest,
    ClaimResult,
    ReleaseIssueRequest,
    ReleaseResult,
    ExtendClaimRequest,
    ExtensionResult,
    AutoReleaseResult
)
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/issues", tags=["issues"])


def get_redis_client() -> Optional[redis.Redis]:
    """Get Redis client for caching"""
    try:
        client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        client.ping()
        return client
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}. Caching disabled.")
        return None


def get_issue_service(
    db: Session = Depends(get_db),
    redis_client: Optional[redis.Redis] = Depends(get_redis_client)
) -> IssueService:
    """Get issue service instance"""
    return IssueService(db=db, redis_client=redis_client)


@router.get("/", response_model=PaginatedIssuesResponse)
async def get_issues(
    # Pagination
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    
    # Filters
    programming_languages: Optional[str] = Query(None, description="Comma-separated programming languages"),
    labels: Optional[str] = Query(None, description="Comma-separated labels"),
    difficulty_levels: Optional[str] = Query(None, description="Comma-separated difficulty levels"),
    status: Optional[str] = Query(None, description="Issue status"),
    search_query: Optional[str] = Query(None, description="Search in title and description"),
    repository_id: Optional[int] = Query(None, description="Filter by repository ID"),
    
    issue_service: IssueService = Depends(get_issue_service)
):
    """
    Get paginated and filtered issues.
    
    Supports filtering by:
    - Programming languages
    - Labels
    - Difficulty levels
    - Status
    - Text search
    - Repository
    
    Results are cached for improved performance.
    """
    # Parse filters
    filters = IssueFilters(
        programming_languages=programming_languages.split(",") if programming_languages else None,
        labels=labels.split(",") if labels else None,
        difficulty_levels=difficulty_levels.split(",") if difficulty_levels else None,
        status=status if status else None,
        search_query=search_query,
        repository_id=repository_id
    )
    
    pagination = PaginationParams(page=page, page_size=page_size)
    
    # Get filtered issues
    issues, total = issue_service.get_filtered_issues(filters=filters, pagination=pagination)
    
    # Convert to response models
    issue_responses = []
    for issue in issues:
        issue_dict = {
            "id": issue.id,
            "github_issue_id": issue.github_issue_id,
            "repository_id": issue.repository_id,
            "title": issue.title,
            "description": issue.description,
            "labels": issue.labels,
            "programming_language": issue.programming_language,
            "difficulty_level": issue.difficulty_level,
            "ai_explanation": issue.ai_explanation,
            "status": issue.status.value,
            "claimed_by": issue.claimed_by,
            "claimed_at": issue.claimed_at,
            "claim_expires_at": issue.claim_expires_at,
            "github_url": issue.github_url,
            "created_at": issue.created_at,
            "updated_at": issue.updated_at,
            "repository_name": issue.repository.name if issue.repository else None,
            "repository_full_name": issue.repository.full_name if issue.repository else None
        }
        issue_responses.append(IssueResponse(**issue_dict))
    
    # Calculate total pages
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    
    return PaginatedIssuesResponse(
        items=issue_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.post("/search", response_model=PaginatedIssuesResponse)
async def search_issues(
    request: IssueSearchRequest,
    issue_service: IssueService = Depends(get_issue_service)
):
    """
    Search issues by text query with optional filters.
    
    Searches in issue title and description.
    """
    # Get filtered issues
    issues, total = issue_service.search_issues(
        search_query=request.query,
        filters=request.filters,
        pagination=request.pagination
    )
    
    # Convert to response models
    issue_responses = []
    for issue in issues:
        issue_dict = {
            "id": issue.id,
            "github_issue_id": issue.github_issue_id,
            "repository_id": issue.repository_id,
            "title": issue.title,
            "description": issue.description,
            "labels": issue.labels,
            "programming_language": issue.programming_language,
            "difficulty_level": issue.difficulty_level,
            "ai_explanation": issue.ai_explanation,
            "status": issue.status.value,
            "claimed_by": issue.claimed_by,
            "claimed_at": issue.claimed_at,
            "claim_expires_at": issue.claim_expires_at,
            "github_url": issue.github_url,
            "created_at": issue.created_at,
            "updated_at": issue.updated_at,
            "repository_name": issue.repository.name if issue.repository else None,
            "repository_full_name": issue.repository.full_name if issue.repository else None
        }
        issue_responses.append(IssueResponse(**issue_dict))
    
    # Calculate total pages
    total_pages = math.ceil(total / request.pagination.page_size) if total > 0 else 0
    
    return PaginatedIssuesResponse(
        items=issue_responses,
        total=total,
        page=request.pagination.page,
        page_size=request.pagination.page_size,
        total_pages=total_pages
    )


@router.get("/{issue_id}", response_model=IssueResponse)
async def get_issue(
    issue_id: int,
    issue_service: IssueService = Depends(get_issue_service)
):
    """
    Get a specific issue by ID.
    """
    issue = issue_service.get_issue_by_id(issue_id)
    
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    issue_dict = {
        "id": issue.id,
        "github_issue_id": issue.github_issue_id,
        "repository_id": issue.repository_id,
        "title": issue.title,
        "description": issue.description,
        "labels": issue.labels,
        "programming_language": issue.programming_language,
        "difficulty_level": issue.difficulty_level,
        "ai_explanation": issue.ai_explanation,
        "status": issue.status.value,
        "claimed_by": issue.claimed_by,
        "claimed_at": issue.claimed_at,
        "claim_expires_at": issue.claim_expires_at,
        "github_url": issue.github_url,
        "created_at": issue.created_at,
        "updated_at": issue.updated_at,
        "repository_name": issue.repository.name if issue.repository else None,
        "repository_full_name": issue.repository.full_name if issue.repository else None
    }
    
    return IssueResponse(**issue_dict)


@router.get("/filters/available")
async def get_available_filters(
    issue_service: IssueService = Depends(get_issue_service)
):
    """
    Get available filter options (languages, labels, difficulties).
    
    Useful for building filter UI components.
    """
    return issue_service.get_available_filters()


@router.post("/sync", response_model=SyncResult)
async def sync_issues(
    repository_ids: Optional[List[int]] = None,
    issue_service: IssueService = Depends(get_issue_service)
):
    """
    Synchronize issues from GitHub repositories.
    
    This endpoint fetches new issues from configured repositories
    and updates existing ones. It should be called by scheduled tasks
    or administrators.
    
    Args:
        repository_ids: Optional list of repository IDs to sync. If not provided, syncs all active repos.
    """
    try:
        result = await issue_service.sync_issues(repository_ids=repository_ids)
        return result
    except Exception as e:
        logger.error(f"Issue sync failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")



@router.post("/{issue_id}/claim", response_model=ClaimResult)
async def claim_issue(
    issue_id: int,
    request: ClaimIssueRequest,
    issue_service: IssueService = Depends(get_issue_service)
):
    """
    Claim an issue for a user.
    
    When a user clicks "Solve It", this endpoint marks the issue as claimed
    and sets an expiration deadline based on the issue difficulty:
    - Easy: 7 days
    - Medium: 14 days
    - Hard: 21 days
    
    The issue will be automatically released if not completed before the deadline.
    """
    result = issue_service.claim_issue(issue_id=issue_id, user_id=request.user_id)
    
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    
    return result


@router.post("/{issue_id}/release", response_model=ReleaseResult)
async def release_issue(
    issue_id: int,
    request: ReleaseIssueRequest,
    issue_service: IssueService = Depends(get_issue_service)
):
    """
    Release a claimed issue.
    
    Users can manually release issues they have claimed if they decide
    not to work on them. This makes the issue available for others.
    """
    result = issue_service.release_issue(issue_id=issue_id, user_id=request.user_id)
    
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    
    return result


@router.post("/{issue_id}/extend", response_model=ExtensionResult)
async def extend_claim_deadline(
    issue_id: int,
    request: ExtendClaimRequest,
    issue_service: IssueService = Depends(get_issue_service)
):
    """
    Extend the claim deadline for an issue.
    
    Users can request deadline extensions with justification.
    Extensions are granted for 1-14 days based on the request.
    """
    result = issue_service.extend_claim_deadline(
        issue_id=issue_id,
        user_id=request.user_id,
        extension_days=request.extension_days,
        justification=request.justification
    )
    
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    
    return result


@router.post("/claims/auto-release", response_model=AutoReleaseResult)
async def trigger_auto_release(
    issue_service: IssueService = Depends(get_issue_service)
):
    """
    Manually trigger automatic release of expired claims.
    
    This endpoint is primarily for testing and admin use.
    In production, this runs automatically via Celery every hour.
    """
    result = issue_service.auto_release_expired_claims()
    return result


@router.get("/claims/expiring")
async def get_expiring_claims(
    hours: int = Query(24, ge=1, le=168, description="Hours threshold for expiration"),
    issue_service: IssueService = Depends(get_issue_service)
):
    """
    Get claims that are expiring within the specified time threshold.
    
    Useful for displaying warnings to users about upcoming deadlines.
    """
    expiring_issues = issue_service.get_expiring_claims(hours_threshold=hours)
    
    # Convert to response format
    issue_responses = []
    for issue in expiring_issues:
        issue_dict = {
            "id": issue.id,
            "github_issue_id": issue.github_issue_id,
            "repository_id": issue.repository_id,
            "title": issue.title,
            "description": issue.description,
            "labels": issue.labels,
            "programming_language": issue.programming_language,
            "difficulty_level": issue.difficulty_level,
            "ai_explanation": issue.ai_explanation,
            "status": issue.status.value,
            "claimed_by": issue.claimed_by,
            "claimed_at": issue.claimed_at,
            "claim_expires_at": issue.claim_expires_at,
            "github_url": issue.github_url,
            "created_at": issue.created_at,
            "updated_at": issue.updated_at,
            "repository_name": issue.repository.name if issue.repository else None,
            "repository_full_name": issue.repository.full_name if issue.repository else None
        }
        issue_responses.append(IssueResponse(**issue_dict))
    
    return {
        "count": len(issue_responses),
        "issues": issue_responses
    }
