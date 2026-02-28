from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.schemas.auth import GitHubCallbackRequest, TokenResponse, TokenRefreshRequest
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/github/callback", response_model=TokenResponse)
async def github_callback(
    request: GitHubCallbackRequest,
    db: Session = Depends(get_db)
):
    """
    GitHub OAuth callback endpoint
    
    Exchanges OAuth code for JWT tokens and creates/updates user account
    
    Requirements:
    - 1.1: GitHub OAuth authentication
    - 1.2: Create user account with GitHub profile
    - 1.4: Login existing user instead of duplicate
    """
    auth_service = AuthService(db)
    return await auth_service.authenticate_github_user(request.code)


@router.post("/refresh", response_model=TokenResponse)
def refresh_access_token(
    request: TokenRefreshRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token
    
    Returns new access and refresh tokens
    """
    auth_service = AuthService(db)
    return auth_service.refresh_token(request.refresh_token)


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information
    
    Protected endpoint that requires valid JWT token
    """
    return current_user


@router.post("/logout")
def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout current user
    
    In future, this will add token to blacklist
    For now, client should discard tokens
    """
    # TODO: Implement token blacklist with Redis
    return {"message": "Successfully logged out"}
