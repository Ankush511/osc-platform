from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status

from app.models.user import User
from app.models.contribution import Contribution
from app.schemas.user import UserUpdate, UserResponse
from app.schemas.auth import GitHubUserData
from app.core.config import settings
from app.services.cache_service import cache_service, CacheKeys, CacheTTL


class UserService:
    """User management service for registration, preferences, and statistics"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, github_data: GitHubUserData) -> User:
        """
        Create a new user from GitHub profile data
        
        Requirements:
        - 1.2: Create user account with GitHub profile information
        - 1.3: Store GitHub username, profile picture, and basic profile data
        """
        # Check if user already exists
        existing_user = self.db.query(User).filter(
            User.github_id == github_data.id
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists"
            )
        
        # Create new user with GitHub profile data
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
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_github_id(self, github_id: int) -> Optional[User]:
        """Get user by GitHub ID"""
        return self.db.query(User).filter(User.github_id == github_id).first()
    
    def get_user_by_username(self, github_username: str) -> Optional[User]:
        """Get user by GitHub username"""
        return self.db.query(User).filter(
            User.github_username == github_username
        ).first()
    
    def update_preferences(self, user_id: int, preferences: UserUpdate) -> User:
        """
        Update user preferences (languages and labels)
        
        Requirements:
        - 2.4: Support filtering by programming language and label preferences
        - 2.5: Remember and apply filters in future sessions
        """
        user = self.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update preferences if provided
        if preferences.preferred_languages is not None:
            user.preferred_languages = preferences.preferred_languages
        
        if preferences.preferred_labels is not None:
            user.preferred_labels = preferences.preferred_labels
        
        self.db.commit()
        self.db.refresh(user)
        
        # Invalidate cached stats and profile when preferences change
        cache_service.delete(CacheKeys.user_stats(user_id))
        cache_service.delete(CacheKeys.user_profile(user_id))
        
        return user
    
    def update_profile(self, user_id: int, github_data: GitHubUserData) -> User:
        """
        Update user profile with latest GitHub data
        
        This is called during authentication to keep profile data fresh
        """
        user = self.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update profile fields
        user.github_username = github_data.login
        user.avatar_url = github_data.avatar_url
        user.email = github_data.email
        user.full_name = github_data.name
        user.bio = github_data.bio
        user.location = github_data.location
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def get_user_stats(self, user_id: int, use_cache: bool = True) -> Dict[str, Any]:
        """
        Calculate and return user statistics with caching
        
        Requirements:
        - 6.1: Display total issues solved, PRs submitted, and PRs merged
        """
        # Try to get from cache first
        if use_cache:
            cached_stats = cache_service.get(CacheKeys.user_stats(user_id))
            if cached_stats:
                return cached_stats
        
        user = self.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Calculate statistics from contributions
        contributions = self.db.query(Contribution).filter(
            Contribution.user_id == user_id
        ).all()
        
        total_prs_submitted = len(contributions)
        merged_prs = len([c for c in contributions if c.status == "merged"])
        
        # Get contributions by language (from related issues)
        contributions_by_language = self._calculate_contributions_by_language(user_id)
        
        # Get contributions by repository
        contributions_by_repo = self._calculate_contributions_by_repo(user_id)
        
        # Get recent contributions timeline
        recent_contributions = self._get_recent_contributions(user_id, limit=10)
        
        stats = {
            "user_id": user_id,
            "total_contributions": user.total_contributions,
            "total_prs_submitted": total_prs_submitted,
            "merged_prs": merged_prs,
            "contributions_by_language": contributions_by_language,
            "contributions_by_repo": contributions_by_repo,
            "recent_contributions": recent_contributions,
            "calculated_at": datetime.utcnow().isoformat()
        }
        
        # Cache the stats
        cache_service.set(CacheKeys.user_stats(user_id), stats, CacheTTL.USER_STATS)
        
        return stats
    
    def increment_contribution_count(self, user_id: int) -> User:
        """
        Increment user's total contribution count
        
        Called when a contribution is verified
        """
        user = self.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.total_contributions += 1
        self.db.commit()
        self.db.refresh(user)
        
        # Invalidate cached stats
        cache_service.delete(CacheKeys.user_stats(user_id))
        cache_service.delete(CacheKeys.contribution_timeline(user_id))
        
        return user
    
    def increment_merged_pr_count(self, user_id: int) -> User:
        """
        Increment user's merged PR count
        
        Called when a PR is merged
        """
        user = self.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.merged_prs += 1
        self.db.commit()
        self.db.refresh(user)
        
        # Invalidate cached stats
        cache_service.delete(CacheKeys.user_stats(user_id))
        cache_service.delete(CacheKeys.contribution_timeline(user_id))
        
        return user
    
    def _calculate_contributions_by_language(self, user_id: int) -> Dict[str, int]:
        """Calculate contributions grouped by programming language"""
        from app.models.issue import Issue
        
        result = self.db.query(
            Issue.programming_language,
            func.count(Contribution.id).label("count")
        ).join(
            Contribution, Contribution.issue_id == Issue.id
        ).filter(
            Contribution.user_id == user_id
        ).group_by(
            Issue.programming_language
        ).all()
        
        return {lang: count for lang, count in result if lang}
    
    def _calculate_contributions_by_repo(self, user_id: int) -> Dict[str, int]:
        """Calculate contributions grouped by repository"""
        from app.models.issue import Issue
        from app.models.repository import Repository
        
        result = self.db.query(
            Repository.full_name,
            func.count(Contribution.id).label("count")
        ).join(
            Issue, Issue.repository_id == Repository.id
        ).join(
            Contribution, Contribution.issue_id == Issue.id
        ).filter(
            Contribution.user_id == user_id
        ).group_by(
            Repository.full_name
        ).all()
        
        return {repo: count for repo, count in result}
    
    def _get_recent_contributions(self, user_id: int, limit: int = 10) -> list:
        """Get recent contributions with issue and repo details"""
        from app.models.issue import Issue
        from app.models.repository import Repository
        
        contributions = self.db.query(Contribution).filter(
            Contribution.user_id == user_id
        ).order_by(
            Contribution.submitted_at.desc()
        ).limit(limit).all()
        
        result = []
        for contrib in contributions:
            issue = self.db.query(Issue).filter(Issue.id == contrib.issue_id).first()
            if issue:
                repo = self.db.query(Repository).filter(
                    Repository.id == issue.repository_id
                ).first()
                
                result.append({
                    "contribution_id": contrib.id,
                    "issue_title": issue.title,
                    "repository": repo.full_name if repo else "Unknown",
                    "status": contrib.status,
                    "pr_url": contrib.pr_url,
                    "submitted_at": contrib.submitted_at.isoformat(),
                    "merged_at": contrib.merged_at.isoformat() if contrib.merged_at else None
                })
        
        return result
