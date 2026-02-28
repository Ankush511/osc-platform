"""
Admin schemas for platform management
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.core.validation import InputValidator


class PlatformStats(BaseModel):
    """Overall platform statistics"""
    total_users: int
    active_users_last_30_days: int
    total_repositories: int
    active_repositories: int
    total_issues: int
    available_issues: int
    claimed_issues: int
    completed_issues: int
    total_contributions: int
    merged_prs: int
    pending_prs: int


class RepositoryCreate(BaseModel):
    """Schema for adding a new repository"""
    full_name: str = Field(..., description="Repository full name (owner/repo)", min_length=1, max_length=200)
    
    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        return InputValidator.validate_github_repo(v)
    
    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "facebook/react"
            }
        }


class RepositoryUpdate(BaseModel):
    """Schema for updating repository settings"""
    is_active: Optional[bool] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "is_active": True
            }
        }


class RepositoryManagement(BaseModel):
    """Repository management response"""
    id: int
    full_name: str
    name: str
    description: Optional[str]
    primary_language: Optional[str]
    stars: int
    forks: int
    is_active: bool
    last_synced: Optional[datetime]
    issue_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserManagement(BaseModel):
    """User management response"""
    id: int
    github_username: str
    email: Optional[str]
    full_name: Optional[str]
    is_admin: bool
    total_contributions: int
    merged_prs: int
    claimed_issues_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserRoleUpdate(BaseModel):
    """Schema for updating user role"""
    is_admin: bool
    
    class Config:
        json_schema_extra = {
            "example": {
                "is_admin": True
            }
        }


class SystemHealth(BaseModel):
    """System health status"""
    status: str = Field(..., description="Overall system status: healthy, degraded, unhealthy")
    database: Dict[str, Any]
    redis: Dict[str, Any]
    github_api: Dict[str, Any]
    ai_service: Dict[str, Any]
    celery: Dict[str, Any]
    timestamp: datetime


class ConfigurationSettings(BaseModel):
    """Platform configuration settings"""
    github_client_id: str
    openai_configured: bool
    email_enabled: bool
    claim_timeout_easy_days: int
    claim_timeout_medium_days: int
    claim_timeout_hard_days: int
    claim_grace_period_hours: int
    environment: str


class ConfigurationUpdate(BaseModel):
    """Schema for updating configuration"""
    claim_timeout_easy_days: Optional[int] = Field(None, ge=1, le=90)
    claim_timeout_medium_days: Optional[int] = Field(None, ge=1, le=90)
    claim_timeout_hard_days: Optional[int] = Field(None, ge=1, le=90)
    claim_grace_period_hours: Optional[int] = Field(None, ge=1, le=168)
    email_enabled: Optional[bool] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "claim_timeout_easy_days": 7,
                "claim_timeout_medium_days": 14,
                "claim_timeout_hard_days": 21,
                "claim_grace_period_hours": 24,
                "email_enabled": True
            }
        }


class SyncTrigger(BaseModel):
    """Schema for triggering repository sync"""
    repository_ids: Optional[List[int]] = Field(None, description="Specific repository IDs to sync. If None, syncs all active repos")
    
    class Config:
        json_schema_extra = {
            "example": {
                "repository_ids": [1, 2, 3]
            }
        }


class ActivityLog(BaseModel):
    """Activity log entry"""
    timestamp: datetime
    event_type: str
    user_id: Optional[int]
    user_name: Optional[str]
    details: str
    metadata: Optional[Dict[str, Any]]


class RateLimitStatus(BaseModel):
    """GitHub API rate limit status"""
    limit: int
    remaining: int
    reset_at: datetime
    used: int
    percentage_used: float
