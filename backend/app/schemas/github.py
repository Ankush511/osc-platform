"""
GitHub API response schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class GitHubUser(BaseModel):
    """GitHub user profile data"""
    login: str
    id: int
    avatar_url: str
    name: Optional[str] = None
    email: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    public_repos: int = 0
    followers: int = 0
    following: int = 0


class GitHubLabel(BaseModel):
    """GitHub issue label"""
    name: str
    color: str
    description: Optional[str] = None


class GitHubIssue(BaseModel):
    """GitHub issue data"""
    id: int
    number: int
    title: str
    body: Optional[str] = None
    state: str
    html_url: str
    labels: List[GitHubLabel] = []
    created_at: datetime
    updated_at: datetime
    user: dict


class GitHubRepository(BaseModel):
    """GitHub repository data"""
    id: int
    name: str
    full_name: str
    description: Optional[str] = None
    html_url: str
    language: Optional[str] = None
    stargazers_count: int = 0
    forks_count: int = 0
    topics: List[str] = []
    default_branch: str = "main"


class GitHubPullRequest(BaseModel):
    """GitHub pull request data"""
    id: int
    number: int
    title: str
    body: Optional[str] = None
    state: str
    html_url: str
    user: dict
    head: dict
    base: dict
    merged: bool = False
    merged_at: Optional[datetime] = None
    created_at: datetime


class PRValidation(BaseModel):
    """Pull request validation result"""
    is_valid: bool
    pr_number: int
    pr_url: str
    author: str
    is_merged: bool
    linked_issue: Optional[int] = None
    error_message: Optional[str] = None


class WebhookConfig(BaseModel):
    """GitHub webhook configuration"""
    id: int
    url: str
    active: bool
    events: List[str]


class RateLimitInfo(BaseModel):
    """GitHub API rate limit information"""
    limit: int
    remaining: int
    reset: datetime
    used: int
