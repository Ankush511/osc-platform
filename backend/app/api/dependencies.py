from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.base import SessionLocal
from app.models.user import User
from app.services.auth_service import AuthService

security = HTTPBearer()


def get_db() -> Generator:
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user from JWT token
    Use this to protect routes that require authentication
    """
    token = credentials.credentials
    auth_service = AuthService(db)
    return auth_service.validate_token(token)


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to get current active user
    Can be extended to check if user is active/banned
    """
    return current_user
