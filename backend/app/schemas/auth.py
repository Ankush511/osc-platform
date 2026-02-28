from pydantic import BaseModel, Field, field_validator
from typing import Optional
from app.core.validation import InputValidator


class GitHubUserData(BaseModel):
    """GitHub user profile data"""
    login: str
    id: int
    avatar_url: str
    name: Optional[str] = None
    email: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    
    @field_validator('login')
    @classmethod
    def validate_login(cls, v: str) -> str:
        return InputValidator.validate_github_username(v)
    
    @field_validator('avatar_url')
    @classmethod
    def validate_avatar_url(cls, v: str) -> str:
        return InputValidator.validate_url(v, allowed_schemes=['https'])
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return InputValidator.validate_email(v)
        return v
    
    @field_validator('name', 'bio', 'location')
    @classmethod
    def validate_text_fields(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return InputValidator.sanitize_string(v, max_length=500)
        return v


class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(default=1800, description="Token expiration in seconds")


class TokenRefreshRequest(BaseModel):
    """Token refresh request"""
    refresh_token: str


class GitHubCallbackRequest(BaseModel):
    """GitHub OAuth callback request"""
    code: str
