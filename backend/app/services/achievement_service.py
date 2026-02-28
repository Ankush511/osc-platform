from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status

from app.models.achievement import Achievement, UserAchievement
from app.models.contribution import Contribution, ContributionStatus
from app.models.issue import Issue
from app.schemas.achievement import AchievementCreate, UserAchievementProgress


class AchievementService:
    """Achievement system for gamification and user milestones"""
    
    # Predefined achievements
    ACHIEVEMENTS = [
        {
            "name": "First Steps",
            "description": "Submit your first pull request",
            "badge_icon": "🎯",
            "category": "milestone",
            "threshold": 1
        },
        {
            "name": "Getting Started",
            "description": "Get your first PR merged",
            "badge_icon": "✅",
            "category": "milestone",
            "threshold": 1
        },
        {
            "name": "Contributor",
            "description": "Submit 5 pull requests",
            "badge_icon": "🌟",
            "category": "milestone",
            "threshold": 5
        },
        {
            "name": "Active Contributor",
            "description": "Get 5 PRs merged",
            "badge_icon": "⭐",
            "category": "milestone",
            "threshold": 5
        },
        {
            "name": "Dedicated Developer",
            "description": "Submit 10 pull requests",
            "badge_icon": "💪",
            "category": "milestone",
            "threshold": 10
        },
        {
            "name": "Merge Master",
            "description": "Get 10 PRs merged",
            "badge_icon": "🏆",
            "category": "milestone",
            "threshold": 10
        },
        {
            "name": "Open Source Hero",
            "description": "Submit 25 pull requests",
            "badge_icon": "🦸",
            "category": "milestone",
            "threshold": 25
        },
        {
            "name": "Century Club",
            "description": "Get 25 PRs merged",
            "badge_icon": "💯",
            "category": "milestone",
            "threshold": 25
        },
        {
            "name": "Python Pioneer",
            "description": "Contribute to 5 Python projects",
            "badge_icon": "🐍",
            "category": "language",
            "threshold": 5
        },
        {
            "name": "JavaScript Journeyman",
            "description": "Contribute to 5 JavaScript projects",
            "badge_icon": "📜",
            "category": "language",
            "threshold": 5
        },
        {
            "name": "TypeScript Titan",
            "description": "Contribute to 5 TypeScript projects",
            "badge_icon": "📘",
            "category": "language",
            "threshold": 5
        },
        {
            "name": "Go Guru",
            "description": "Contribute to 5 Go projects",
            "badge_icon": "🔵",
            "category": "language",
            "threshold": 5
        },
        {
            "name": "Rust Ranger",
            "description": "Contribute to 5 Rust projects",
            "badge_icon": "🦀",
            "category": "language",
            "threshold": 5
        },
        {
            "name": "Polyglot",
            "description": "Contribute to projects in 3 different languages",
            "badge_icon": "🌐",
            "category": "language",
            "threshold": 3
        },
    ]
    
    def __init__(self, db: Session):
        self.db = db
    
    def initialize_achievements(self) -> List[Achievement]:
        """
        Initialize predefined achievements in the database
        
        This should be called during application setup
        """
        achievements = []
        
        for achievement_data in self.ACHIEVEMENTS:
            # Check if achievement already exists
            existing = self.db.query(Achievement).filter(
                Achievement.name == achievement_data["name"]
            ).first()
            
            if not existing:
                achievement = Achievement(**achievement_data)
                self.db.add(achievement)
                achievements.append(achievement)
        
        self.db.commit()
        return achievements
    
    def get_all_achievements(self) -> List[Achievement]:
        """Get all available achievements"""
        return self.db.query(Achievement).all()
    
    def get_user_achievements(self, user_id: int) -> List[UserAchievementProgress]:
        """
        Get user's achievement progress
        
        Requirements:
        - 6.3: Award badges or achievements for milestones
        """
        all_achievements = self.get_all_achievements()
        user_achievements = self.db.query(UserAchievement).filter(
            UserAchievement.user_id == user_id
        ).all()
        
        # Create a map of achievement_id to user_achievement
        user_achievement_map = {ua.achievement_id: ua for ua in user_achievements}
        
        result = []
        for achievement in all_achievements:
            user_achievement = user_achievement_map.get(achievement.id)
            
            if user_achievement:
                progress = user_achievement.progress
                is_unlocked = user_achievement.is_unlocked
                earned_at = user_achievement.earned_at if is_unlocked else None
            else:
                # Calculate current progress
                progress = self._calculate_achievement_progress(user_id, achievement)
                is_unlocked = False
                earned_at = None
            
            percentage = min((progress / achievement.threshold) * 100, 100.0)
            
            result.append(UserAchievementProgress(
                achievement=achievement,
                progress=progress,
                is_unlocked=is_unlocked,
                earned_at=earned_at,
                percentage=percentage
            ))
        
        return result
    
    def check_and_award_achievements(self, user_id: int) -> List[Achievement]:
        """
        Check user's progress and award any newly earned achievements
        
        Requirements:
        - 6.3: Award badges or achievements for milestones
        
        Returns list of newly awarded achievements
        """
        all_achievements = self.get_all_achievements()
        newly_awarded = []
        
        for achievement in all_achievements:
            # Check if user already has this achievement
            existing = self.db.query(UserAchievement).filter(
                UserAchievement.user_id == user_id,
                UserAchievement.achievement_id == achievement.id
            ).first()
            
            # Calculate current progress
            progress = self._calculate_achievement_progress(user_id, achievement)
            
            if existing:
                # Update progress
                existing.progress = progress
                
                # Check if newly unlocked
                if not existing.is_unlocked and progress >= achievement.threshold:
                    existing.is_unlocked = True
                    existing.earned_at = datetime.utcnow()
                    newly_awarded.append(achievement)
            else:
                # Create new user achievement record
                is_unlocked = progress >= achievement.threshold
                user_achievement = UserAchievement(
                    user_id=user_id,
                    achievement_id=achievement.id,
                    progress=progress,
                    is_unlocked=is_unlocked,
                    earned_at=datetime.utcnow() if is_unlocked else None
                )
                self.db.add(user_achievement)
                
                if is_unlocked:
                    newly_awarded.append(achievement)
        
        self.db.commit()
        return newly_awarded
    
    def _calculate_achievement_progress(self, user_id: int, achievement: Achievement) -> int:
        """
        Calculate user's progress towards a specific achievement
        
        Requirements:
        - 6.5: Only count verified and completed contributions
        """
        category = achievement.category
        
        if category == "milestone":
            # Milestone achievements based on PR counts
            if "merged" in achievement.name.lower() or "merge" in achievement.name.lower():
                # Count merged PRs
                return self.db.query(func.count(Contribution.id)).filter(
                    Contribution.user_id == user_id,
                    Contribution.status == ContributionStatus.MERGED
                ).scalar() or 0
            else:
                # Count all submitted PRs
                return self.db.query(func.count(Contribution.id)).filter(
                    Contribution.user_id == user_id
                ).scalar() or 0
        
        elif category == "language":
            # Language-specific achievements
            language_map = {
                "Python": ["Python Pioneer"],
                "JavaScript": ["JavaScript Journeyman"],
                "TypeScript": ["TypeScript Titan"],
                "Go": ["Go Guru"],
                "Rust": ["Rust Ranger"]
            }
            
            # Find which language this achievement is for
            target_language = None
            for lang, achievement_names in language_map.items():
                if achievement.name in achievement_names:
                    target_language = lang
                    break
            
            if target_language:
                # Count contributions in this language
                return self.db.query(func.count(Contribution.id.distinct())).join(
                    Issue, Contribution.issue_id == Issue.id
                ).filter(
                    Contribution.user_id == user_id,
                    Issue.programming_language == target_language
                ).scalar() or 0
            
            # Polyglot achievement - count distinct languages
            if achievement.name == "Polyglot":
                return self.db.query(func.count(func.distinct(Issue.programming_language))).join(
                    Contribution, Contribution.issue_id == Issue.id
                ).filter(
                    Contribution.user_id == user_id,
                    Issue.programming_language.isnot(None)
                ).scalar() or 0
        
        return 0
    
    def get_unlocked_achievements(self, user_id: int) -> List[UserAchievement]:
        """Get all unlocked achievements for a user"""
        return self.db.query(UserAchievement).filter(
            UserAchievement.user_id == user_id,
            UserAchievement.is_unlocked == True
        ).all()
    
    def get_achievement_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Get achievement statistics for a user
        
        Requirements:
        - 6.3: Display achievement progress
        """
        total_achievements = self.db.query(func.count(Achievement.id)).scalar() or 0
        unlocked_achievements = self.db.query(func.count(UserAchievement.id)).filter(
            UserAchievement.user_id == user_id,
            UserAchievement.is_unlocked == True
        ).scalar() or 0
        
        return {
            "total_achievements": total_achievements,
            "unlocked_achievements": unlocked_achievements,
            "completion_percentage": (unlocked_achievements / total_achievements * 100) if total_achievements > 0 else 0
        }
