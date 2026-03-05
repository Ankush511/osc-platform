"""
Issue discovery and filtering API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import math
import logging

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.services.issue_service import IssueService
from app.tasks.difficulty_tasks import refine_difficulty_for_issues
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

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/issues", tags=["issues"])


def get_issue_service(db: Session = Depends(get_db)) -> IssueService:
    return IssueService(db=db)


def _issue_to_response(issue) -> IssueResponse:
    return IssueResponse(
        id=issue.id, github_issue_id=issue.github_issue_id,
        repository_id=issue.repository_id, title=issue.title,
        description=issue.description, labels=issue.labels,
        programming_language=issue.programming_language,
        difficulty_level=issue.difficulty_level,
        ai_explanation=issue.ai_explanation,
        status=issue.status.value, claimed_by=issue.claimed_by,
        claimed_at=issue.claimed_at, claim_expires_at=issue.claim_expires_at,
        github_url=issue.github_url, created_at=issue.created_at,
        updated_at=issue.updated_at,
        repository_name=issue.repository.name if issue.repository else None,
        repository_full_name=issue.repository.full_name if issue.repository else None
    )


@router.get("/", response_model=PaginatedIssuesResponse)
async def get_issues(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    programming_languages: Optional[str] = Query(None),
    labels: Optional[str] = Query(None),
    difficulty_levels: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search_query: Optional[str] = Query(None),
    repository_id: Optional[int] = Query(None),
    issue_service: IssueService = Depends(get_issue_service)
):
    filters = IssueFilters(
        programming_languages=programming_languages.split(",") if programming_languages else None,
        labels=labels.split(",") if labels else None,
        difficulty_levels=difficulty_levels.split(",") if difficulty_levels else None,
        status=status if status else None,
        search_query=search_query,
        repository_id=repository_id
    )
    pagination = PaginationParams(page=page, page_size=page_size)
    issues, total = issue_service.get_filtered_issues(filters=filters, pagination=pagination)
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    return PaginatedIssuesResponse(
        items=[_issue_to_response(i) for i in issues],
        total=total, page=page, page_size=page_size, total_pages=total_pages
    )


@router.post("/search", response_model=PaginatedIssuesResponse)
async def search_issues(
    request: IssueSearchRequest,
    issue_service: IssueService = Depends(get_issue_service)
):
    issues, total = issue_service.search_issues(
        search_query=request.query, filters=request.filters, pagination=request.pagination
    )
    total_pages = math.ceil(total / request.pagination.page_size) if total > 0 else 0
    return PaginatedIssuesResponse(
        items=[_issue_to_response(i) for i in issues],
        total=total, page=request.pagination.page,
        page_size=request.pagination.page_size, total_pages=total_pages
    )


@router.get("/{issue_id}", response_model=IssueResponse)
async def get_issue(issue_id: int, issue_service: IssueService = Depends(get_issue_service)):
    issue = issue_service.get_issue_by_id(issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    return _issue_to_response(issue)


@router.get("/filters/available")
async def get_available_filters(issue_service: IssueService = Depends(get_issue_service)):
    return issue_service.get_available_filters()


@router.post("/sync", response_model=SyncResult)
async def sync_issues(
    background_tasks: BackgroundTasks,
    repository_ids: Optional[List[int]] = None,
    issue_service: IssueService = Depends(get_issue_service)
):
    try:
        result = await issue_service.sync_issues(repository_ids=repository_ids)
        # Queue AI difficulty refinement for newly added issues
        if result.new_issue_ids:
            logger.info(f"Queuing AI difficulty refinement for {len(result.new_issue_ids)} new issues")
            background_tasks.add_task(refine_difficulty_for_issues, result.new_issue_ids)
        return result
    except Exception as e:
        logger.error(f"Issue sync failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@router.post("/{issue_id}/claim", response_model=ClaimResult)
async def claim_issue(
    issue_id: int,
    current_user: User = Depends(get_current_user),
    issue_service: IssueService = Depends(get_issue_service)
):
    result = issue_service.claim_issue(issue_id=issue_id, user_id=current_user.id)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    return result


@router.post("/{issue_id}/release", response_model=ReleaseResult)
async def release_issue(
    issue_id: int,
    request: ReleaseIssueRequest,
    current_user: User = Depends(get_current_user),
    issue_service: IssueService = Depends(get_issue_service)
):
    result = issue_service.release_issue(issue_id=issue_id, user_id=current_user.id, reason=request.reason)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    return result


@router.post("/{issue_id}/extend", response_model=ExtensionResult)
async def extend_claim_deadline(
    issue_id: int, request: ExtendClaimRequest,
    current_user: User = Depends(get_current_user),
    issue_service: IssueService = Depends(get_issue_service)
):
    result = issue_service.extend_claim_deadline(
        issue_id=issue_id, user_id=current_user.id,
        extension_days=request.extension_days, justification=request.justification
    )
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    return result


@router.post("/claims/auto-release", response_model=AutoReleaseResult)
async def trigger_auto_release(issue_service: IssueService = Depends(get_issue_service)):
    return issue_service.auto_release_expired_claims()


@router.get("/claims/expiring")
async def get_expiring_claims(
    hours: int = Query(24, ge=1, le=168),
    issue_service: IssueService = Depends(get_issue_service)
):
    expiring_issues = issue_service.get_expiring_claims(hours_threshold=hours)
    return {
        "count": len(expiring_issues),
        "issues": [_issue_to_response(i) for i in expiring_issues]
    }
