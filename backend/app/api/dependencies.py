from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import redis

from app.db.base import SessionLocal
from app.models.user import User
from app.services.auth_service import AuthService
from app.core.config import settings

security = HTTPBearer()

# Redis client singleton
_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> redis.Redis:
    """Redis client dependency for caching"""
    global _redis_client
    
    if _redis_client is None:
        try:
            _redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True
            )
            # Test connection
            _redis_client.ping()
        except Exception as e:
            print(f"Redis connection failed: {e}")
            # Return None if Redis is not available
            # Services should handle None gracefully
            return None
    
    return _redis_client


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
    # Future: Add user status checks here
    return current_user
