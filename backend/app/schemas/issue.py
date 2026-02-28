"""
Issue-related schemas for API requests and responses
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime
from enum import Enum
from app.core.validation import InputValidator


class DifficultyLevel(str, Enum):
    """Issue difficulty levels"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    UNKNOWN = "unknown"


class IssueStatus(str, Enum):
    """Issue status values"""
    AVAILABLE = "available"
    CLAIMED = "claimed"
    COMPLETED = "completed"
    CLOSED = "closed"


class IssueFilters(BaseModel):
    """Filters for issue queries"""
    programming_languages: Optional[List[str]] = Field(None, description="Filter by programming languages", max_length=20)
    labels: Optional[List[str]] = Field(None, description="Filter by issue labels", max_length=50)
    difficulty_levels: Optional[List[str]] = Field(None, description="Filter by difficulty levels")
    status: Optional[IssueStatus] = Field(None, description="Filter by issue status")
    search_query: Optional[str] = Field(None, description="Text search in title and description", max_length=200)
    repository_id: Optional[int] = Field(None, description="Filter by repository ID", gt=0)
    
    @field_validator('programming_languages', 'labels')
    @classmethod
    def validate_string_lists(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v:
            return [InputValidator.sanitize_string(item, max_length=50) for item in v]
        return v
    
    @field_validator('search_query')
    @classmethod
    def validate_search_query(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return InputValidator.sanitize_string(v, max_length=200)
        return v


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")


class IssueResponse(BaseModel):
    """Issue response schema"""
    id: int
    github_issue_id: int
    repository_id: int
    title: str
    description: Optional[str]
    labels: List[str]
    programming_language: Optional[str]
    difficulty_level: Optional[str]
    ai_explanation: Optional[str]
    status: str
    claimed_by: Optional[int]
    claimed_at: Optional[datetime]
    claim_expires_at: Optional[datetime]
    github_url: str
    created_at: datetime
    updated_at: datetime
    
    # Nested repository info
    repository_name: Optional[str] = None
    repository_full_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class PaginatedIssuesResponse(BaseModel):
    """Paginated issues response"""
    items: List[IssueResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class SyncResult(BaseModel):
    """Result of issue synchronization"""
    repositories_synced: int
    issues_added: int
    issues_updated: int
    issues_closed: int
    errors: List[str] = []
    sync_duration_seconds: float


class IssueSearchRequest(BaseModel):
    """Issue search request"""
    query: str = Field(..., min_length=1, max_length=200, description="Search query")
    filters: Optional[IssueFilters] = None
    pagination: PaginationParams = PaginationParams()
    
    @field_validator('query')
    @classmethod
    def validate_query(cls, v: str) -> str:
        return InputValidator.sanitize_string(v, max_length=200)


class ClaimIssueRequest(BaseModel):
    """Request to claim an issue"""
    user_id: int = Field(..., description="ID of the user claiming the issue", gt=0)


class ClaimResult(BaseModel):
    """Result of claiming an issue"""
    success: bool
    message: str
    issue_id: Optional[int] = None
    claimed_at: Optional[datetime] = None
    claim_expires_at: Optional[datetime] = None


class ReleaseIssueRequest(BaseModel):
    """Request to release an issue"""
    user_id: int = Field(..., description="ID of the user releasing the issue", gt=0)


class ReleaseResult(BaseModel):
    """Result of releasing an issue"""
    success: bool
    message: str
    issue_id: Optional[int] = None


class ExtendClaimRequest(BaseModel):
    """Request to extend claim deadline"""
    user_id: int = Field(..., description="ID of the user requesting extension", gt=0)
    justification: str = Field(..., min_length=10, max_length=1000, description="Reason for extension request")
    extension_days: int = Field(7, ge=1, le=14, description="Number of days to extend (1-14)")
    
    @field_validator('justification')
    @classmethod
    def validate_justification(cls, v: str) -> str:
        return InputValidator.sanitize_string(v, max_length=1000)


class ExtensionResult(BaseModel):
    """Result of deadline extension request"""
    success: bool
    message: str
    issue_id: Optional[int] = None
    new_expiration: Optional[datetime] = None


class AutoReleaseResult(BaseModel):
    """Result of automatic claim release"""
    released_count: int
    issue_ids: List[int]
    errors: List[str] = []
