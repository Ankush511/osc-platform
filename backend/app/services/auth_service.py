from typing import Optional, Dict, Any
from datetime import timedelta
import httpx
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, decode_token, verify_token_type
from app.models.user import User
from app.schemas.auth import GitHubUserData, TokenResponse


class AuthService:
    """Authentication service for GitHub OAuth and JWT management"""
    
    GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
    GITHUB_USER_URL = "https://api.github.com/user"
    
    def __init__(self, db: Session):
        self.db = db
    
    async def authenticate_github_user(self, code: str) -> TokenResponse:
        """
        Authenticate user with GitHub OAuth code and return JWT tokens
        
        Requirements:
        - 1.1: GitHub OAuth authentication
        - 1.2: Create user account with GitHub profile
        - 1.4: Login existing user instead of creating duplicate
        """
        # Exchange code for GitHub access token
        github_token = await self._exchange_code_for_token(code)
        
        # Fetch user profile from GitHub
        github_user_data = await self._fetch_github_user(github_token)
        
        # Get or create user in database
        user = self._get_or_create_user(github_user_data)
        
        # Generate JWT tokens
        return self._generate_tokens(user)
    
    async def _exchange_code_for_token(self, code: str) -> str:
        """Exchange OAuth code for GitHub access token"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.GITHUB_TOKEN_URL,
                headers={"Accept": "application/json"},
                data={
                    "client_id": settings.GITHUB_CLIENT_ID,
                    "client_secret": settings.GITHUB_CLIENT_SECRET,
                    "code": code,
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange code for token"
                )
            
            data = response.json()
            if "access_token" not in data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid OAuth response from GitHub"
                )
            
            return data["access_token"]
    
    async def _fetch_github_user(self, github_token: str) -> GitHubUserData:
        """Fetch user profile from GitHub API"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.GITHUB_USER_URL,
                headers={
                    "Authorization": f"Bearer {github_token}",
                    "Accept": "application/json"
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to fetch user profile from GitHub"
                )
            
            data = response.json()
            return GitHubUserData(**data)
    
    def _get_or_create_user(self, github_data: GitHubUserData) -> User:
        """Get existing user or create new one (Requirement 1.4)"""
        # Check if user already exists by github_id
        user = self.db.query(User).filter(User.github_id == github_data.id).first()
        
        if user:
            # Update user profile with latest GitHub data
            user.github_username = github_data.login
            user.avatar_url = github_data.avatar_url
            user.email = github_data.email
            user.full_name = github_data.name
            user.bio = github_data.bio
            user.location = github_data.location
            self.db.commit()
            self.db.refresh(user)
            return user
        
        # Create new user (Requirement 1.2)
        user = User(
            github_username=github_data.login,
            github_id=github_data.id,
            avatar_url=github_data.avatar_url,
            email=github_data.email,
            full_name=github_data.name,
            bio=github_data.bio,
            location=github_data.location,
            preferred_languages=[],
            preferred_labels=[],
            total_contributions=0,
            merged_prs=0
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def _generate_tokens(self, user: User) -> TokenResponse:
        """Generate access and refresh tokens for user"""
        token_data = {
            "sub": str(user.id),
            "github_username": user.github_username,
            "github_id": user.github_id
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token"""
        payload = decode_token(refresh_token)
        
        if not payload or not verify_token_type(payload, "refresh"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Verify user still exists
        user = self.db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Generate new tokens
        return self._generate_tokens(user)
    
    def validate_token(self, token: str) -> User:
        """Validate access token and return user"""
        payload = decode_token(token)
        
        if not payload or not verify_token_type(payload, "access"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        user = self.db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return user
    
    def revoke_token(self, token: str) -> bool:
        """
        Revoke token (placeholder for future Redis-based token blacklist)
        For now, tokens expire naturally based on their exp claim
        """
        # TODO: Implement token blacklist using Redis
        # This would store revoked tokens until their expiration
        return True
