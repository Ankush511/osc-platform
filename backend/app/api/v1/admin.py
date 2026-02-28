"""
Admin API endpoints for platform management and monitoring
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
import redis

from app.api.dependencies import get_db, get_current_user, get_redis_client
from app.models.user import User
from app.schemas.admin import (
    PlatformStats,
    RepositoryCreate,
    RepositoryUpdate,
    RepositoryManagement,
    UserManagement,
    UserRoleUpdate,
    SystemHealth,
    ConfigurationSettings,
    ConfigurationUpdate,
    SyncTrigger,
    RateLimitStatus
)
from app.schemas.issue import SyncResult
from app.services.admin_service import AdminService
from app.services.issue_service import IssueService


router = APIRouter(prefix="/admin", tags=["admin"])


def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to verify user has admin privileges.
    
    Raises:
        HTTPException: If user is not an admin
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


@router.get("/stats", response_model=PlatformStats)
def get_platform_statistics(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get overall platform statistics.
    
    Requirements:
    - 7.4: Platform statistics for monitoring
    
    Admin only endpoint.
    """
    admin_service = AdminService(db)
    return admin_service.get_platform_stats()


@router.get("/repositories", response_model=dict)
def get_repositories(
    active_only: bool = Query(False, description="Filter to only active repositories"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get repositories with management information.
    
    Requirements:
    - 7.4: Repository management interface
    
    Admin only endpoint.
    """
    admin_service = AdminService(db)
    repositories, total = admin_service.get_repositories(
        active_only=active_only,
        page=page,
        page_size=page_size
    )
    
    return {
        "repositories": repositories,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


@router.post("/repositories", response_model=RepositoryManagement, status_code=status.HTTP_201_CREATED)
async def add_repository(
    repository: RepositoryCreate,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Add a new repository to the platform.
    
    Requirements:
    - 7.4: System should support adding repositories for issue fetching
    
    Admin only endpoint.
    """
    admin_service = AdminService(db)
    
    try:
        new_repo = await admin_service.add_repository(repository.full_name)
        
        # Get issue count (will be 0 for new repo)
        issue_count = 0
        
        return RepositoryManagement(
            id=new_repo.id,
            full_name=new_repo.full_name,
            name=new_repo.name,
            description=new_repo.description,
            primary_language=new_repo.primary_language,
            stars=new_repo.stars,
            forks=new_repo.forks,
            is_active=new_repo.is_active,
            last_synced=new_repo.last_synced,
            issue_count=issue_count,
            created_at=new_repo.created_at
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add repository: {str(e)}"
        )


@router.patch("/repositories/{repo_id}", response_model=RepositoryManagement)
def update_repository(
    repo_id: int,
    update: RepositoryUpdate,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update repository settings.
    
    Requirements:
    - 7.4: Repository management interface for activating/deactivating repos
    
    Admin only endpoint.
    """
    admin_service = AdminService(db)
    
    try:
        updated_repo = admin_service.update_repository(repo_id, update.is_active)
        
        # Get issue count
        from app.models.issue import Issue
        from sqlalchemy import func
        issue_count = db.query(func.count(Issue.id)).filter(
            Issue.repository_id == repo_id
        ).scalar() or 0
        
        return RepositoryManagement(
            id=updated_repo.id,
            full_name=updated_repo.full_name,
            name=updated_repo.name,
            description=updated_repo.description,
            primary_language=updated_repo.primary_language,
            stars=updated_repo.stars,
            forks=updated_repo.forks,
            is_active=updated_repo.is_active,
            last_synced=updated_repo.last_synced,
            issue_count=issue_count,
            created_at=updated_repo.created_at
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update repository: {str(e)}"
        )


@router.delete("/repositories/{repo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_repository(
    repo_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Delete a repository and all associated issues.
    
    Requirements:
    - 7.4: System should support removing repositories
    
    Admin only endpoint.
    """
    admin_service = AdminService(db)
    
    try:
        admin_service.delete_repository(repo_id)
        return None
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete repository: {str(e)}"
        )


@router.post("/repositories/sync", response_model=SyncResult)
async def trigger_repository_sync(
    sync_trigger: SyncTrigger,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client)
):
    """
    Manually trigger repository synchronization.
    
    Requirements:
    - 7.1: Fetch new issues from configured repositories
    - 7.2: Check if previously displayed issues are still open
    
    Admin only endpoint.
    """
    issue_service = IssueService(db, redis_client)
    
    try:
        result = await issue_service.sync_issues(sync_trigger.repository_ids)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync repositories: {str(e)}"
        )


@router.get("/users", response_model=dict)
def get_users(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    admin_only: bool = Query(False, description="Filter to only admin users"),
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get users with management information.
    
    Requirements:
    - User management tools for admin oversight
    
    Admin only endpoint.
    """
    admin_service = AdminService(db)
    users, total = admin_service.get_users(
        page=page,
        page_size=page_size,
        admin_only=admin_only
    )
    
    return {
        "users": users,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


@router.patch("/users/{user_id}/role", response_model=UserManagement)
def update_user_role(
    user_id: int,
    role_update: UserRoleUpdate,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update user admin role.
    
    Requirements:
    - User management tools for admin oversight
    
    Admin only endpoint.
    """
    admin_service = AdminService(db)
    
    try:
        updated_user = admin_service.update_user_role(user_id, role_update.is_admin)
        
        # Get claimed issues count
        from app.models.issue import Issue, IssueStatus
        from sqlalchemy import func
        claimed_count = db.query(func.count(Issue.id)).filter(
            Issue.claimed_by == user_id,
            Issue.status == IssueStatus.CLAIMED
        ).scalar() or 0
        
        return UserManagement(
            id=updated_user.id,
            github_username=updated_user.github_username,
            email=updated_user.email,
            full_name=updated_user.full_name,
            is_admin=updated_user.is_admin,
            total_contributions=updated_user.total_contributions,
            merged_prs=updated_user.merged_prs,
            claimed_issues_count=claimed_count,
            created_at=updated_user.created_at
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user role: {str(e)}"
        )


@router.get("/health", response_model=SystemHealth)
async def check_system_health(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client)
):
    """
    Check health of all system components.
    
    Requirements:
    - System health monitoring and alerting
    
    Admin only endpoint.
    """
    admin_service = AdminService(db, redis_client)
    return await admin_service.check_system_health()


@router.get("/config", response_model=ConfigurationSettings)
def get_configuration(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get current platform configuration.
    
    Requirements:
    - Configuration management for AI and GitHub settings
    
    Admin only endpoint.
    """
    admin_service = AdminService(db)
    return admin_service.get_configuration()


@router.patch("/config", response_model=ConfigurationSettings)
def update_configuration(
    config_update: ConfigurationUpdate,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update platform configuration.
    
    Note: Updates are runtime only. For persistent changes,
    update environment variables.
    
    Requirements:
    - Configuration management for platform settings
    
    Admin only endpoint.
    """
    admin_service = AdminService(db)
    
    try:
        # Convert to dict, excluding None values
        updates = config_update.model_dump(exclude_none=True)
        
        return admin_service.update_configuration(updates)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update configuration: {str(e)}"
        )


@router.get("/rate-limit", response_model=RateLimitStatus)
async def get_rate_limit_status(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get GitHub API rate limit status.
    
    Requirements:
    - 7.5: System should handle API rate limits gracefully
    
    Admin only endpoint.
    """
    admin_service = AdminService(db)
    
    try:
        return await admin_service.get_rate_limit_status()
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get rate limit status: {str(e)}"
        )
