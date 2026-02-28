"""
AI service schemas for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class DifficultyLevel(str, Enum):
    """Issue difficulty levels"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    UNKNOWN = "unknown"


class LearningResource(BaseModel):
    """Learning resource recommendation"""
    title: str = Field(..., description="Resource title")
    url: str = Field(..., description="Resource URL")
    type: str = Field(..., description="Resource type (documentation, tutorial, video, etc.)")
    description: Optional[str] = Field(None, description="Brief description of the resource")


class RepositorySummaryRequest(BaseModel):
    """Request for repository summary generation"""
    repository_id: int = Field(..., description="Repository ID")
    force_regenerate: bool = Field(False, description="Force regeneration even if cached")


class RepositorySummaryResponse(BaseModel):
    """Response containing repository summary"""
    repository_id: int
    summary: str
    cached: bool = Field(..., description="Whether the summary was retrieved from cache")


class IssueExplanationRequest(BaseModel):
    """Request for issue explanation generation"""
    issue_id: int = Field(..., description="Issue ID")
    force_regenerate: bool = Field(False, description="Force regeneration even if cached")


class IssueExplanationResponse(BaseModel):
    """Response containing issue explanation"""
    issue_id: int
    explanation: str
    difficulty_level: DifficultyLevel
    learning_resources: List[LearningResource] = []
    cached: bool = Field(..., description="Whether the explanation was retrieved from cache")


class AIServiceError(BaseModel):
    """AI service error response"""
    error_code: str
    message: str
    details: Optional[dict] = None
