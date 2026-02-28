"""
Admin service for platform management and monitoring
"""
import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
import redis

from app.models.user import User
from app.models.repository import Repository
from app.models.issue import Issue, IssueStatus
from app.models.contribution import Contribution, ContributionStatus
from app.schemas.admin import (
    PlatformStats,
    RepositoryManagement,
    UserManagement,
    SystemHealth,
    ConfigurationSettings,
    RateLimitStatus,
    ActivityLog
)
from app.services.github_service import GitHubService, GitHubAPIError
from app.core.config import settings

logger = logging.getLogger(__name__)


class AdminService:
    """
    Admin service for platform management.
    
    Provides functionality for:
    - Platform statistics and monitoring
    - Repository management (add/remove/activate)
    - User management and role assignment
    - System health checks
    - Configuration management
    """
    
    def __init__(self, db: Session, redis_client: Optional[redis.Redis] = None):
        """
        Initialize admin service.
        
        Args:
            db: Database session
            redis_client: Optional Redis client for health checks
        """
        self.db = db
        self.redis_client = redis_client
    
    def get_platform_stats(self) -> PlatformStats:
        """
        Get overall platform statistics.
        
        Returns:
            PlatformStats with comprehensive platform metrics
        """
        try:
            # User statistics
            total_users = self.db.query(func.count(User.id)).scalar()
            
            # Active users in last 30 days (users with contributions or claims)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            active_users = self.db.query(func.count(func.distinct(Contribution.user_id))).filter(
                Contribution.submitted_at >= thirty_days_ago
            ).scalar()
            
            # Repository statistics
            total_repositories = self.db.query(func.count(Repository.id)).scalar()
            active_repositories = self.db.query(func.count(Repository.id)).filter(
                Repository.is_active == True
            ).scalar()
            
            # Issue statistics
            total_issues = self.db.query(func.count(Issue.id)).scalar()
            available_issues = self.db.query(func.count(Issue.id)).filter(
                Issue.status == IssueStatus.AVAILABLE
            ).scalar()
            claimed_issues = self.db.query(func.count(Issue.id)).filter(
                Issue.status == IssueStatus.CLAIMED
            ).scalar()
            completed_issues = self.db.query(func.count(Issue.id)).filter(
                Issue.status == IssueStatus.COMPLETED
            ).scalar()
            
            # Contribution statistics
            total_contributions = self.db.query(func.count(Contribution.id)).scalar()
            merged_prs = self.db.query(func.count(Contribution.id)).filter(
                Contribution.status == ContributionStatus.MERGED
            ).scalar()
            pending_prs = self.db.query(func.count(Contribution.id)).filter(
                Contribution.status == ContributionStatus.SUBMITTED
            ).scalar()
            
            return PlatformStats(
                total_users=total_users or 0,
                active_users_last_30_days=active_users or 0,
                total_repositories=total_repositories or 0,
                active_repositories=active_repositories or 0,
                total_issues=total_issues or 0,
                available_issues=available_issues or 0,
                claimed_issues=claimed_issues or 0,
                completed_issues=completed_issues or 0,
                total_contributions=total_contributions or 0,
                merged_prs=merged_prs or 0,
                pending_prs=pending_prs or 0
            )
            
        except Exception as e:
            logger.error(f"Error getting platform stats: {str(e)}")
            raise
    
    def get_repositories(
        self,
        active_only: bool = False,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[RepositoryManagement], int]:
        """
        Get repositories with management information.
        
        Args:
            active_only: If True, only return active repositories
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            Tuple of (repositories list, total count)
        """
        try:
            # Build query
            query = self.db.query(Repository)
            
            if active_only:
                query = query.filter(Repository.is_active == True)
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * page_size
            repositories = query.order_by(Repository.created_at.desc()).offset(offset).limit(page_size).all()
            
            # Add issue count for each repository
            result = []
            for repo in repositories:
                issue_count = self.db.query(func.count(Issue.id)).filter(
                    Issue.repository_id == repo.id
                ).scalar()
                
                repo_data = RepositoryManagement(
                    id=repo.id,
                    full_name=repo.full_name,
                    name=repo.name,
                    description=repo.description,
                    primary_language=repo.primary_language,
                    stars=repo.stars,
                    forks=repo.forks,
                    is_active=repo.is_active,
                    last_synced=repo.last_synced,
                    issue_count=issue_count or 0,
                    created_at=repo.created_at
                )
                result.append(repo_data)
            
            return result, total
            
        except Exception as e:
            logger.error(f"Error getting repositories: {str(e)}")
            raise
    
    async def add_repository(self, full_name: str) -> Repository:
        """
        Add a new repository to the platform.
        
        Args:
            full_name: Repository full name (owner/repo)
            
        Returns:
            Created Repository object
            
        Raises:
            ValueError: If repository already exists or cannot be fetched
        """
        try:
            # Check if repository already exists
            existing = self.db.query(Repository).filter(
                Repository.full_name == full_name
            ).first()
            
            if existing:
                raise ValueError(f"Repository {full_name} already exists")
            
            # Fetch repository info from GitHub
            github_service = GitHubService()
            
            try:
                repo_info = await github_service.get_repository_info(full_name)
                
                # Create repository
                new_repo = Repository(
                    github_repo_id=repo_info.id,
                    full_name=repo_info.full_name,
                    name=repo_info.name,
                    description=repo_info.description,
                    primary_language=repo_info.language,
                    topics=repo_info.topics or [],
                    stars=repo_info.stargazers_count,
                    forks=repo_info.forks_count,
                    is_active=True,
                    last_synced=None
                )
                
                self.db.add(new_repo)
                self.db.commit()
                self.db.refresh(new_repo)
                
                logger.info(f"Added repository: {full_name}")
                
                return new_repo
                
            finally:
                await github_service.close()
                
        except GitHubAPIError as e:
            logger.error(f"GitHub API error adding repository {full_name}: {str(e)}")
            raise ValueError(f"Failed to fetch repository from GitHub: {str(e)}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding repository {full_name}: {str(e)}")
            raise
    
    def update_repository(self, repo_id: int, is_active: bool) -> Repository:
        """
        Update repository settings.
        
        Args:
            repo_id: Repository ID
            is_active: Whether repository should be active
            
        Returns:
            Updated Repository object
            
        Raises:
            ValueError: If repository not found
        """
        try:
            repo = self.db.query(Repository).filter(Repository.id == repo_id).first()
            
            if not repo:
                raise ValueError(f"Repository with ID {repo_id} not found")
            
            repo.is_active = is_active
            
            self.db.commit()
            self.db.refresh(repo)
            
            logger.info(f"Updated repository {repo.full_name}: is_active={is_active}")
            
            return repo
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating repository {repo_id}: {str(e)}")
            raise
    
    def delete_repository(self, repo_id: int) -> bool:
        """
        Delete a repository and all associated issues.
        
        Args:
            repo_id: Repository ID
            
        Returns:
            True if deleted successfully
            
        Raises:
            ValueError: If repository not found
        """
        try:
            repo = self.db.query(Repository).filter(Repository.id == repo_id).first()
            
            if not repo:
                raise ValueError(f"Repository with ID {repo_id} not found")
            
            repo_name = repo.full_name
            
            # Delete repository (cascade will delete associated issues)
            self.db.delete(repo)
            self.db.commit()
            
            logger.info(f"Deleted repository: {repo_name}")
            
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting repository {repo_id}: {str(e)}")
            raise
    
    def get_users(
        self,
        page: int = 1,
        page_size: int = 20,
        admin_only: bool = False
    ) -> Tuple[List[UserManagement], int]:
        """
        Get users with management information.
        
        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            admin_only: If True, only return admin users
            
        Returns:
            Tuple of (users list, total count)
        """
        try:
            # Build query
            query = self.db.query(User)
            
            if admin_only:
                query = query.filter(User.is_admin == True)
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * page_size
            users = query.order_by(User.created_at.desc()).offset(offset).limit(page_size).all()
            
            # Add claimed issues count for each user
            result = []
            for user in users:
                claimed_count = self.db.query(func.count(Issue.id)).filter(
                    Issue.claimed_by == user.id,
                    Issue.status == IssueStatus.CLAIMED
                ).scalar()
                
                user_data = UserManagement(
                    id=user.id,
                    github_username=user.github_username,
                    email=user.email,
                    full_name=user.full_name,
                    is_admin=user.is_admin,
                    total_contributions=user.total_contributions,
                    merged_prs=user.merged_prs,
                    claimed_issues_count=claimed_count or 0,
                    created_at=user.created_at
                )
                result.append(user_data)
            
            return result, total
            
        except Exception as e:
            logger.error(f"Error getting users: {str(e)}")
            raise
    
    def update_user_role(self, user_id: int, is_admin: bool) -> User:
        """
        Update user admin role.
        
        Args:
            user_id: User ID
            is_admin: Whether user should be admin
            
        Returns:
            Updated User object
            
        Raises:
            ValueError: If user not found
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if not user:
                raise ValueError(f"User with ID {user_id} not found")
            
            user.is_admin = is_admin
            
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"Updated user {user.github_username}: is_admin={is_admin}")
            
            return user
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating user role {user_id}: {str(e)}")
            raise
    
    async def check_system_health(self) -> SystemHealth:
        """
        Check health of all system components.
        
        Returns:
            SystemHealth with status of all components
        """
        health_data = {
            "database": {"status": "unknown", "details": {}},
            "redis": {"status": "unknown", "details": {}},
            "github_api": {"status": "unknown", "details": {}},
            "ai_service": {"status": "unknown", "details": {}},
            "celery": {"status": "unknown", "details": {}}
        }
        
        # Check database
        try:
            self.db.execute("SELECT 1")
            health_data["database"] = {
                "status": "healthy",
                "details": {"connection": "active"}
            }
        except Exception as e:
            health_data["database"] = {
                "status": "unhealthy",
                "details": {"error": str(e)}
            }
        
        # Check Redis
        if self.redis_client:
            try:
                self.redis_client.ping()
                info = self.redis_client.info()
                health_data["redis"] = {
                    "status": "healthy",
                    "details": {
                        "connected_clients": info.get("connected_clients", 0),
                        "used_memory_human": info.get("used_memory_human", "unknown")
                    }
                }
            except Exception as e:
                health_data["redis"] = {
                    "status": "unhealthy",
                    "details": {"error": str(e)}
                }
        else:
            health_data["redis"] = {
                "status": "unavailable",
                "details": {"message": "Redis not configured"}
            }
        
        # Check GitHub API
        github_service = GitHubService()
        try:
            rate_limit = await github_service.get_rate_limit()
            health_data["github_api"] = {
                "status": "healthy" if rate_limit.remaining > 100 else "degraded",
                "details": {
                    "rate_limit_remaining": rate_limit.remaining,
                    "rate_limit_total": rate_limit.limit,
                    "reset_at": rate_limit.reset_at.isoformat()
                }
            }
        except Exception as e:
            health_data["github_api"] = {
                "status": "unhealthy",
                "details": {"error": str(e)}
            }
        finally:
            await github_service.close()
        
        # Check AI service (OpenAI)
        if settings.OPENAI_API_KEY:
            health_data["ai_service"] = {
                "status": "configured",
                "details": {"api_key_set": True}
            }
        else:
            health_data["ai_service"] = {
                "status": "unavailable",
                "details": {"api_key_set": False}
            }
        
        # Check Celery (basic check - would need more sophisticated monitoring)
        health_data["celery"] = {
            "status": "unknown",
            "details": {"message": "Celery monitoring not implemented"}
        }
        
        # Determine overall status
        statuses = [comp["status"] for comp in health_data.values()]
        if "unhealthy" in statuses:
            overall_status = "unhealthy"
        elif "degraded" in statuses:
            overall_status = "degraded"
        else:
            overall_status = "healthy"
        
        return SystemHealth(
            status=overall_status,
            database=health_data["database"],
            redis=health_data["redis"],
            github_api=health_data["github_api"],
            ai_service=health_data["ai_service"],
            celery=health_data["celery"],
            timestamp=datetime.utcnow()
        )
    
    def get_configuration(self) -> ConfigurationSettings:
        """
        Get current platform configuration.
        
        Returns:
            ConfigurationSettings with current settings
        """
        return ConfigurationSettings(
            github_client_id=settings.GITHUB_CLIENT_ID,
            openai_configured=bool(settings.OPENAI_API_KEY),
            email_enabled=settings.EMAIL_ENABLED,
            claim_timeout_easy_days=settings.CLAIM_TIMEOUT_EASY_DAYS,
            claim_timeout_medium_days=settings.CLAIM_TIMEOUT_MEDIUM_DAYS,
            claim_timeout_hard_days=settings.CLAIM_TIMEOUT_HARD_DAYS,
            claim_grace_period_hours=settings.CLAIM_GRACE_PERIOD_HOURS,
            environment=settings.ENVIRONMENT
        )
    
    def update_configuration(self, updates: Dict[str, Any]) -> ConfigurationSettings:
        """
        Update platform configuration.
        
        Note: This updates runtime settings. For persistent changes,
        environment variables should be updated.
        
        Args:
            updates: Dictionary of configuration updates
            
        Returns:
            Updated ConfigurationSettings
        """
        try:
            # Update settings (runtime only)
            if "claim_timeout_easy_days" in updates:
                settings.CLAIM_TIMEOUT_EASY_DAYS = updates["claim_timeout_easy_days"]
            if "claim_timeout_medium_days" in updates:
                settings.CLAIM_TIMEOUT_MEDIUM_DAYS = updates["claim_timeout_medium_days"]
            if "claim_timeout_hard_days" in updates:
                settings.CLAIM_TIMEOUT_HARD_DAYS = updates["claim_timeout_hard_days"]
            if "claim_grace_period_hours" in updates:
                settings.CLAIM_GRACE_PERIOD_HOURS = updates["claim_grace_period_hours"]
            if "email_enabled" in updates:
                settings.EMAIL_ENABLED = updates["email_enabled"]
            
            logger.info(f"Updated configuration: {updates}")
            
            return self.get_configuration()
            
        except Exception as e:
            logger.error(f"Error updating configuration: {str(e)}")
            raise
    
    async def get_rate_limit_status(self) -> RateLimitStatus:
        """
        Get GitHub API rate limit status.
        
        Returns:
            RateLimitStatus with current rate limit information
        """
        github_service = GitHubService()
        
        try:
            rate_limit = await github_service.get_rate_limit()
            
            used = rate_limit.limit - rate_limit.remaining
            percentage_used = (used / rate_limit.limit * 100) if rate_limit.limit > 0 else 0
            
            return RateLimitStatus(
                limit=rate_limit.limit,
                remaining=rate_limit.remaining,
                reset_at=rate_limit.reset_at,
                used=used,
                percentage_used=round(percentage_used, 2)
            )
            
        finally:
            await github_service.close()
