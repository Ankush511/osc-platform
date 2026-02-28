"""
Contribution and PR validation schemas
"""
from pydantic import BaseModel, Field, HttpUrl, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum
from app.core.validation import InputValidator


class ContributionStatus(str, Enum):
    """Contribution status values"""
    SUBMITTED = "submitted"
    MERGED = "merged"
    CLOSED = "closed"


class SubmitPRRequest(BaseModel):
    """Request to submit a pull request"""
    issue_id: int = Field(..., description="ID of the claimed issue", gt=0)
    pr_url: str = Field(..., description="GitHub PR URL", min_length=1, max_length=500)
    user_id: int = Field(..., description="ID of the user submitting the PR", gt=0)
    
    @field_validator('pr_url')
    @classmethod
    def validate_pr_url(cls, v: str) -> str:
        return InputValidator.validate_github_url(v)


class SubmissionResult(BaseModel):
    """Result of PR submission"""
    success: bool
    message: str
    contribution_id: Optional[int] = None
    pr_number: Optional[int] = None
    status: Optional[str] = None
    points_earned: Optional[int] = None


class ValidationResult(BaseModel):
    """Result of PR validation"""
    is_valid: bool
    pr_number: int
    pr_url: str
    author: str
    is_merged: bool
    linked_issue: Optional[int] = None
    error_message: Optional[str] = None


class ContributionResponse(BaseModel):
    """Contribution response schema"""
    id: int
    user_id: int
    issue_id: int
    pr_url: str
    pr_number: int
    status: str
    submitted_at: datetime
    merged_at: Optional[datetime]
    points_earned: int
    
    # Nested data
    issue_title: Optional[str] = None
    repository_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class PRStatusUpdate(BaseModel):
    """PR status update from webhook"""
    pr_url: str
    pr_number: int
    action: str  # opened, closed, merged, etc.
    merged: bool = False
    merged_at: Optional[datetime] = None


class ContributionStats(BaseModel):
    """User contribution statistics"""
    total_contributions: int
    submitted_prs: int
    merged_prs: int
    closed_prs: int
    total_points: int
    contributions_by_language: dict
    contributions_by_repository: dict
