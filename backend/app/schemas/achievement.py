from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class AchievementBase(BaseModel):
    """Base achievement schema"""
    name: str
    description: str
    badge_icon: str
    category: str
    threshold: int


class AchievementCreate(AchievementBase):
    """Achievement creation schema"""
    pass


class AchievementResponse(AchievementBase):
    """Achievement response schema"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserAchievementBase(BaseModel):
    """Base user achievement schema"""
    achievement_id: int
    progress: int = 0
    is_unlocked: bool = False


class UserAchievementResponse(BaseModel):
    """User achievement response schema"""
    id: int
    user_id: int
    achievement_id: int
    earned_at: datetime
    progress: int
    is_unlocked: bool
    achievement: AchievementResponse

    class Config:
        from_attributes = True


class UserAchievementProgress(BaseModel):
    """User achievement progress with details"""
    achievement: AchievementResponse
    progress: int
    is_unlocked: bool
    earned_at: Optional[datetime] = None
    percentage: float = Field(ge=0, le=100)
