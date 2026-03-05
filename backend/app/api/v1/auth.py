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
    GitHub OAuth callback endpoint.
    Accepts either an OAuth code or a GitHub access token.
    """
    auth_service = AuthService(db)
    
    # Try using it as a GitHub access token first (from NextAuth)
    # If that fails, try exchanging it as an OAuth code
    try:
        return await auth_service.authenticate_with_github_token(request.code)
    except Exception:
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
