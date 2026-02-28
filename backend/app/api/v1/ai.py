"""
AI service API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import redis
import logging

from app.api.dependencies import get_db, get_current_user
from app.services.ai_service import AIService, AIServiceException, RateLimitException
from app.schemas.ai import (
    RepositorySummaryRequest,
    RepositorySummaryResponse,
    IssueExplanationRequest,
    IssueExplanationResponse,
    AIServiceError
)
from app.core.config import settings
from app.models.user import User


logger = logging.getLogger(__name__)
router = APIRouter()


def get_redis_client():
    """Get Redis client for caching"""
    try:
        client = redis.from_url(settings.REDIS_URL, decode_responses=False)
        return client
    except Exception as e:
        logger.warning(f"Failed to connect to Redis: {e}")
        return None


def get_ai_service(
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client)
) -> AIService:
    """Get AI service instance"""
    return AIService(db=db, redis_client=redis_client)


@router.post(
    "/repository-summary",
    response_model=RepositorySummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate repository summary",
    description="Generate an AI-powered summary of a repository"
)
async def generate_repository_summary(
    request: RepositorySummaryRequest,
    ai_service: AIService = Depends(get_ai_service),
    current_user: User = Depends(get_current_user)
):
    """
    Generate an AI-powered summary for a repository.
    
    The summary explains the project's purpose, technology stack, and why it's
    interesting for new contributors. Results are cached for 30 days.
    """
    try:
        # Check if cached first
        cache_key = f"ai:repo_summary:{request.repository_id}"
        cached = None
        
        if not request.force_regenerate and ai_service.redis_client:
            cached = ai_service._get_cached_response(cache_key)
        
        if cached:
            return RepositorySummaryResponse(
                repository_id=request.repository_id,
                summary=cached,
                cached=True
            )
        
        # Generate new summary
        summary = ai_service.generate_repository_summary(
            repository_id=request.repository_id,
            force_regenerate=request.force_regenerate
        )
        
        return RepositorySummaryResponse(
            repository_id=request.repository_id,
            summary=summary,
            cached=False
        )
    
    except RateLimitException as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error_code": "RATE_LIMIT_EXCEEDED",
                "message": str(e),
                "details": {"retry_after": 60}
            }
        )
    
    except AIServiceException as e:
        logger.error(f"AI service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "AI_SERVICE_ERROR",
                "message": str(e)
            }
        )
    
    except Exception as e:
        logger.error(f"Unexpected error generating repository summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred"
            }
        )


@router.post(
    "/issue-explanation",
    response_model=IssueExplanationResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate issue explanation",
    description="Generate an AI-powered explanation of an issue with difficulty analysis and learning resources"
)
async def generate_issue_explanation(
    request: IssueExplanationRequest,
    ai_service: AIService = Depends(get_ai_service),
    current_user: User = Depends(get_current_user)
):
    """
    Generate an AI-powered explanation for an issue.
    
    The explanation breaks down what needs to be done, key concepts involved,
    suggested approach, and prerequisites. Also includes difficulty analysis
    and learning resource suggestions. Results are cached for 30 days.
    """
    try:
        # Check if cached first
        cache_key = f"ai:issue_explanation:{request.issue_id}"
        cached_explanation = None
        
        if not request.force_regenerate and ai_service.redis_client:
            cached_explanation = ai_service._get_cached_response(cache_key)
        
        if cached_explanation:
            # Also get cached difficulty and resources
            difficulty = ai_service.analyze_difficulty(request.issue_id)
            resources = ai_service.suggest_learning_resources(request.issue_id)
            
            return IssueExplanationResponse(
                issue_id=request.issue_id,
                explanation=cached_explanation,
                difficulty_level=difficulty,
                learning_resources=resources,
                cached=True
            )
        
        # Generate new explanation
        explanation = ai_service.explain_issue(
            issue_id=request.issue_id,
            force_regenerate=request.force_regenerate
        )
        
        # Analyze difficulty
        difficulty = ai_service.analyze_difficulty(request.issue_id)
        
        # Suggest learning resources
        resources = ai_service.suggest_learning_resources(request.issue_id)
        
        return IssueExplanationResponse(
            issue_id=request.issue_id,
            explanation=explanation,
            difficulty_level=difficulty,
            learning_resources=resources,
            cached=False
        )
    
    except RateLimitException as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error_code": "RATE_LIMIT_EXCEEDED",
                "message": str(e),
                "details": {"retry_after": 60}
            }
        )
    
    except AIServiceException as e:
        logger.error(f"AI service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "AI_SERVICE_ERROR",
                "message": str(e)
            }
        )
    
    except Exception as e:
        logger.error(f"Unexpected error generating issue explanation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred"
            }
        )
