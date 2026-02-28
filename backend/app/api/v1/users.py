from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import redis

from app.api.dependencies import get_db, get_current_user, get_redis_client
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.achievement import UserAchievementProgress
from app.services.user_service import UserService
from app.services.achievement_service import AchievementService


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user's profile
    
    Requirements:
    - 1.3: Return user profile with GitHub data and preferences
    """
    return current_user


@router.get("/me/stats", response_model=Dict[str, Any])
def get_current_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client)
):
    """
    Get current user's statistics with caching
    
    Requirements:
    - 6.1: Display total issues solved, PRs submitted, and PRs merged
    """
    user_service = UserService(db, redis_client)
    return user_service.get_user_stats(current_user.id)


@router.put("/me/preferences", response_model=UserResponse)
def update_user_preferences(
    preferences: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client)
):
    """
    Update user preferences (languages and labels)
    
    Requirements:
    - 2.4: Support filtering by programming language and label preferences
    - 2.5: Remember and apply filters in future sessions
    """
    user_service = UserService(db, redis_client)
    return user_service.update_preferences(current_user.id, preferences)


@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get user profile by ID (public endpoint)
    """
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.get("/{user_id}/stats", response_model=Dict[str, Any])
def get_user_stats_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client)
):
    """
    Get user statistics by ID (public endpoint)
    
    Requirements:
    - 6.1: Display user statistics
    """
    user_service = UserService(db, redis_client)
    return user_service.get_user_stats(user_id)


@router.get("/me/achievements", response_model=List[UserAchievementProgress])
def get_current_user_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's achievement progress
    
    Requirements:
    - 6.3: Award badges or achievements for milestones
    """
    achievement_service = AchievementService(db)
    return achievement_service.get_user_achievements(current_user.id)


@router.get("/{user_id}/achievements", response_model=List[UserAchievementProgress])
def get_user_achievements_by_id(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get user's achievement progress by ID (public endpoint)
    
    Requirements:
    - 6.3: Display achievement progress
    """
    achievement_service = AchievementService(db)
    return achievement_service.get_user_achievements(user_id)


@router.get("/me/dashboard", response_model=Dict[str, Any])
def get_user_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client)
):
    """
    Get comprehensive user dashboard data
    
    Requirements:
    - 6.1: Display total issues solved, PRs submitted, and PRs merged
    - 6.2: Show contributions by programming language and repository
    - 6.3: Award badges or achievements for milestones
    - 6.4: Display a timeline of recent contributions
    """
    user_service = UserService(db, redis_client)
    achievement_service = AchievementService(db)
    
    # Get user statistics
    stats = user_service.get_user_stats(current_user.id)
    
    # Get achievement progress
    achievements = achievement_service.get_user_achievements(current_user.id)
    achievement_stats = achievement_service.get_achievement_stats(current_user.id)
    
    return {
        "user": UserResponse.model_validate(current_user),
        "statistics": stats,
        "achievements": achievements,
        "achievement_stats": achievement_stats
    }
