"""
AI service API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.api.dependencies import get_db, get_current_user
from app.services.ai_service import AIService, AIServiceException, RateLimitException
from app.schemas.ai import (
    RepositorySummaryRequest,
    RepositorySummaryResponse,
    IssueExplanationRequest,
    IssueExplanationResponse,
)
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()


def get_ai_service(db: Session = Depends(get_db)) -> AIService:
    return AIService(db=db)


@router.post("/repository-summary", response_model=RepositorySummaryResponse)
async def generate_repository_summary(
    request: RepositorySummaryRequest,
    ai_service: AIService = Depends(get_ai_service),
    current_user: User = Depends(get_current_user)
):
    try:
        summary = ai_service.generate_repository_summary(
            repository_id=request.repository_id,
            force_regenerate=request.force_regenerate
        )
        return RepositorySummaryResponse(
            repository_id=request.repository_id, summary=summary, cached=False
        )
    except RateLimitException as e:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e))
    except AIServiceException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/issue-explanation", response_model=IssueExplanationResponse)
async def generate_issue_explanation(
    request: IssueExplanationRequest,
    ai_service: AIService = Depends(get_ai_service),
    current_user: User = Depends(get_current_user)
):
    try:
        explanation = ai_service.explain_issue(
            issue_id=request.issue_id, force_regenerate=request.force_regenerate
        )
        difficulty = ai_service.analyze_difficulty(request.issue_id)
        resources = ai_service.suggest_learning_resources(request.issue_id)
        return IssueExplanationResponse(
            issue_id=request.issue_id, explanation=explanation,
            difficulty_level=difficulty, learning_resources=resources, cached=False
        )
    except RateLimitException as e:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e))
    except AIServiceException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
