from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class Achievement(Base):
    """Achievement definitions for gamification"""
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=False)
    badge_icon = Column(String(100), nullable=False)  # Icon identifier
    category = Column(String(50), nullable=False, index=True)  # milestone, language, streak, etc.
    threshold = Column(Integer, nullable=False)  # Required count to unlock
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user_achievements = relationship("UserAchievement", back_populates="achievement", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Achievement(id={self.id}, name='{self.name}')>"


class UserAchievement(Base):
    """User's earned achievements"""
    __tablename__ = "user_achievements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    achievement_id = Column(Integer, ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Tracking
    earned_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    progress = Column(Integer, default=0, nullable=False)  # Current progress towards achievement
    is_unlocked = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    user = relationship("User", backref="user_achievements")
    achievement = relationship("Achievement", back_populates="user_achievements")

    def __repr__(self):
        return f"<UserAchievement(user_id={self.user_id}, achievement_id={self.achievement_id}, unlocked={self.is_unlocked})>"
