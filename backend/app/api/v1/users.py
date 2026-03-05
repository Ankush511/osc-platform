from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.achievement import UserAchievementProgress
from app.services.user_service import UserService
from app.services.achievement_service import AchievementService


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/me/stats", response_model=Dict[str, Any])
def get_current_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_service = UserService(db)
    return user_service.get_user_stats(current_user.id)


@router.put("/me/preferences", response_model=UserResponse)
def update_user_preferences(
    preferences: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_service = UserService(db)
    return user_service.update_preferences(current_user.id, preferences)


@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get("/{user_id}/stats", response_model=Dict[str, Any])
def get_user_stats_by_id(user_id: int, db: Session = Depends(get_db)):
    user_service = UserService(db)
    return user_service.get_user_stats(user_id)


@router.get("/me/achievements", response_model=List[UserAchievementProgress])
def get_current_user_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    achievement_service = AchievementService(db)
    return achievement_service.get_user_achievements(current_user.id)


@router.get("/{user_id}/achievements", response_model=List[UserAchievementProgress])
def get_user_achievements_by_id(user_id: int, db: Session = Depends(get_db)):
    achievement_service = AchievementService(db)
    return achievement_service.get_user_achievements(user_id)


@router.get("/me/dashboard", response_model=Dict[str, Any])
def get_user_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_service = UserService(db)
    achievement_service = AchievementService(db)
    stats = user_service.get_user_stats(current_user.id)
    achievements = achievement_service.get_user_achievements(current_user.id)
    achievement_stats = achievement_service.get_achievement_stats(current_user.id)
    return {
        "user": UserResponse.model_validate(current_user),
        "statistics": stats,
        "achievements": achievements,
        "achievement_stats": achievement_stats
    }
