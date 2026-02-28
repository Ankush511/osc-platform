from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema"""
    github_username: str
    github_id: int
    email: Optional[str] = None
    avatar_url: str
    full_name: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema"""
    pass


class UserUpdate(BaseModel):
    """User update schema"""
    preferred_languages: Optional[List[str]] = None
    preferred_labels: Optional[List[str]] = None


class UserPreferences(BaseModel):
    """User preferences schema"""
    preferred_languages: List[str] = Field(default_factory=list)
    preferred_labels: List[str] = Field(default_factory=list)


class UserStats(BaseModel):
    """User statistics schema"""
    user_id: int
    total_contributions: int
    total_prs_submitted: int
    merged_prs: int
    contributions_by_language: Dict[str, int] = Field(default_factory=dict)
    contributions_by_repo: Dict[str, int] = Field(default_factory=dict)
    recent_contributions: List[Dict[str, Any]] = Field(default_factory=list)
    calculated_at: str


class UserResponse(UserBase):
    """User response schema"""
    id: int
    preferred_languages: List[str] = Field(default_factory=list)
    preferred_labels: List[str] = Field(default_factory=list)
    total_contributions: int = 0
    merged_prs: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
