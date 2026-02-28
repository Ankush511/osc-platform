"""
Issue management service with synchronization, filtering, search, and caching
"""
import logging
import time
import json
from typing import List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, func, String
import redis

from app.models.issue import Issue, IssueStatus
from app.models.repository import Repository
from app.schemas.issue import (
    IssueFilters,
    PaginationParams,
    SyncResult,
    IssueResponse,
    ClaimResult,
    ReleaseResult,
    ExtensionResult,
    AutoReleaseResult
)
from app.services.github_service import GitHubService, GitHubAPIError
from app.core.config import settings

logger = logging.getLogger(__name__)


class IssueService:
    """
    Issue management service implementing:
    - Issue synchronization from GitHub repositories
    - Advanced filtering by language, labels, and difficulty
    - Text-based search functionality
    - Pagination for large result sets
    - Redis caching for frequently accessed data
    """
    
    # Cache configuration
    CACHE_PREFIX = "issues:"
    CACHE_TTL = 300  # 5 minutes
    FILTERED_ISSUES_CACHE_PREFIX = "filtered_issues:"
    
    # Labels to fetch for beginner-friendly issues
    BEGINNER_LABELS = [
        "good first issue",
        "beginner-friendly",
        "help wanted",
        "first-timers-only",
        "good-first-issue",
        "beginner friendly"
    ]
    
    def __init__(self, db: Session, redis_client: Optional[redis.Redis] = None):
        """
        Initialize issue service.
        
        Args:
            db: Database session
            redis_client: Optional Redis client for caching
        """
        self.db = db
        self.redis_client = redis_client
        
    def _get_cache_key(self, key_type: str, **kwargs) -> str:
        """Generate cache key from parameters"""
        params = "_".join(f"{k}:{v}" for k, v in sorted(kwargs.items()) if v is not None)
        return f"{self.CACHE_PREFIX}{key_type}:{params}"
    
    def _get_from_cache(self, cache_key: str) -> Optional[dict]:
        """Get data from Redis cache"""
        if not self.redis_client:
            return None
        
        try:
            cached = self.redis_client.get(cache_key)
            if cached:
                logger.debug(f"Cache hit: {cache_key}")
                return json.loads(cached)
        except Exception as e:
            logger.error(f"Cache read error: {e}")
        
        return None
    
    def _set_cache(self, cache_key: str, data: dict, ttl: int = CACHE_TTL):
        """Set data in Redis cache"""
        if not self.redis_client:
            return
        
        try:
            self.redis_client.setex(
                cache_key,
                ttl,
                json.dumps(data, default=str)
            )
            logger.debug(f"Cache set: {cache_key}")
        except Exception as e:
            logger.error(f"Cache write error: {e}")
    
    def _invalidate_cache_pattern(self, pattern: str):
        """Invalidate all cache keys matching pattern"""
        if not self.redis_client:
            return
        
        try:
            keys = self.redis_client.keys(f"{self.CACHE_PREFIX}{pattern}*")
            if keys:
                self.redis_client.delete(*keys)
                logger.debug(f"Invalidated {len(keys)} cache keys")
        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")
    
    async def sync_issues(self, repository_ids: Optional[List[int]] = None) -> SyncResult:
        """
        Synchronize issues from GitHub repositories.
        
        Args:
            repository_ids: Optional list of repository IDs to sync. If None, syncs all active repos.
            
        Returns:
            SyncResult with synchronization statistics
        """
        start_time = time.time()
        result = SyncResult(
            repositories_synced=0,
            issues_added=0,
            issues_updated=0,
            issues_closed=0,
            errors=[],
            sync_duration_seconds=0.0
        )
        
        # Get repositories to sync
        query = self.db.query(Repository).filter(Repository.is_active == True)
        if repository_ids:
            query = query.filter(Repository.id.in_(repository_ids))
        
        repositories = query.all()
        
        if not repositories:
            logger.warning("No active repositories found for synchronization")
            result.sync_duration_seconds = time.time() - start_time
            return result
        
        # Initialize GitHub service (using app token or no auth for public repos)
        github_service = GitHubService()
        
        try:
            for repo in repositories:
                try:
                    logger.info(f"Syncing issues from {repo.full_name}")
                    
                    # Fetch issues with beginner-friendly labels
                    github_issues = await github_service.fetch_repository_issues(
                        repo=repo.full_name,
                        labels=self.BEGINNER_LABELS,
                        state="open"
                    )
                    
                    # Track existing issues for this repository
                    existing_issues = {
                        issue.github_issue_id: issue
                        for issue in self.db.query(Issue).filter(
                            Issue.repository_id == repo.id
                        ).all()
                    }
                    
                    # Process fetched issues
                    for gh_issue in github_issues:
                        existing_issue = existing_issues.get(gh_issue.id)
                        
                        if existing_issue:
                            # Update existing issue
                            existing_issue.title = gh_issue.title
                            existing_issue.description = gh_issue.body
                            existing_issue.labels = [label.name for label in gh_issue.labels]
                            existing_issue.github_url = gh_issue.html_url
                            existing_issue.updated_at = datetime.utcnow()
                            
                            # If issue was closed on GitHub, update status
                            if gh_issue.state == "closed" and existing_issue.status != IssueStatus.CLOSED:
                                existing_issue.status = IssueStatus.CLOSED
                                result.issues_closed += 1
                            else:
                                result.issues_updated += 1
                            
                            # Remove from tracking dict
                            existing_issues.pop(gh_issue.id)
                        else:
                            # Create new issue
                            new_issue = Issue(
                                github_issue_id=gh_issue.id,
                                repository_id=repo.id,
                                title=gh_issue.title,
                                description=gh_issue.body,
                                labels=[label.name for label in gh_issue.labels],
                                programming_language=repo.primary_language,
                                difficulty_level=self._infer_difficulty(gh_issue.labels),
                                status=IssueStatus.AVAILABLE,
                                github_url=gh_issue.html_url
                            )
                            self.db.add(new_issue)
                            result.issues_added += 1
                    
                    # Mark remaining issues as closed (they're no longer open on GitHub)
                    for issue in existing_issues.values():
                        if issue.status != IssueStatus.CLOSED:
                            issue.status = IssueStatus.CLOSED
                            result.issues_closed += 1
                    
                    # Update repository sync timestamp
                    repo.last_synced = datetime.utcnow()
                    result.repositories_synced += 1
                    
                    self.db.commit()
                    
                except GitHubAPIError as e:
                    error_msg = f"Failed to sync {repo.full_name}: {str(e)}"
                    logger.error(error_msg)
                    result.errors.append(error_msg)
                    self.db.rollback()
                    continue
                except Exception as e:
                    error_msg = f"Unexpected error syncing {repo.full_name}: {str(e)}"
                    logger.error(error_msg)
                    result.errors.append(error_msg)
                    self.db.rollback()
                    continue
            
            # Invalidate all issue caches after sync
            self._invalidate_cache_pattern("")
            
        finally:
            await github_service.close()
        
        result.sync_duration_seconds = time.time() - start_time
        logger.info(
            f"Sync completed: {result.repositories_synced} repos, "
            f"{result.issues_added} added, {result.issues_updated} updated, "
            f"{result.issues_closed} closed in {result.sync_duration_seconds:.2f}s"
        )
        
        return result
    
    def _infer_difficulty(self, labels: List) -> str:
        """
        Infer difficulty level from issue labels.
        
        Args:
            labels: List of GitHubLabel objects
            
        Returns:
            Difficulty level string
        """
        label_names = [label.name.lower() for label in labels]
        
        # Check for explicit difficulty labels
        if any("easy" in label or "beginner" in label or "good first issue" in label for label in label_names):
            return "easy"
        elif any("medium" in label or "intermediate" in label for label in label_names):
            return "medium"
        elif any("hard" in label or "advanced" in label or "difficult" in label for label in label_names):
            return "hard"
        
        # Default to easy for beginner-friendly labels
        return "easy"
    
    def get_filtered_issues(
        self,
        filters: Optional[IssueFilters] = None,
        pagination: Optional[PaginationParams] = None
    ) -> Tuple[List[Issue], int]:
        """
        Get filtered and paginated issues.
        
        Args:
            filters: Optional filters to apply
            pagination: Optional pagination parameters
            
        Returns:
            Tuple of (issues list, total count)
        """
        # Check cache first
        cache_key = self._get_cache_key(
            "filtered",
            langs=",".join(filters.programming_languages) if filters and filters.programming_languages else None,
            labels=",".join(filters.labels) if filters and filters.labels else None,
            diff=",".join(filters.difficulty_levels) if filters and filters.difficulty_levels else None,
            status=filters.status.value if filters and filters.status else None,
            query=filters.search_query if filters and filters.search_query else None,
            repo=filters.repository_id if filters and filters.repository_id else None,
            page=pagination.page if pagination else 1,
            size=pagination.page_size if pagination else 20
        )
        
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            # Reconstruct issues from cached data
            issue_ids = cached_data["issue_ids"]
            total = cached_data["total"]
            
            if issue_ids:
                issues = self.db.query(Issue).filter(Issue.id.in_(issue_ids)).all()
                # Maintain order from cache
                issues_dict = {issue.id: issue for issue in issues}
                issues = [issues_dict[id] for id in issue_ids if id in issues_dict]
                return issues, total
            return [], total
        
        # Build query
        query = self.db.query(Issue).options(joinedload(Issue.repository))
        
        # Apply filters
        if filters:
            # Programming language filter
            if filters.programming_languages:
                query = query.filter(Issue.programming_language.in_(filters.programming_languages))
            
            # Labels filter (issue must have at least one of the specified labels)
            if filters.labels:
                # Use overlap operator for PostgreSQL arrays
                from sqlalchemy.dialects.postgresql import array
                label_conditions = [
                    Issue.labels.op('&&')(array([label])) for label in filters.labels
                ]
                query = query.filter(or_(*label_conditions))
            
            # Difficulty filter
            if filters.difficulty_levels:
                query = query.filter(Issue.difficulty_level.in_(filters.difficulty_levels))
            
            # Status filter
            if filters.status:
                query = query.filter(Issue.status == filters.status)
            
            # Repository filter
            if filters.repository_id:
                query = query.filter(Issue.repository_id == filters.repository_id)
            
            # Text search in title and description
            if filters.search_query:
                search_term = f"%{filters.search_query}%"
                query = query.filter(
                    or_(
                        Issue.title.ilike(search_term),
                        Issue.description.ilike(search_term)
                    )
                )
        
        # Get total count before pagination
        total = query.count()
        
        # Apply pagination
        if pagination:
            offset = (pagination.page - 1) * pagination.page_size
            query = query.offset(offset).limit(pagination.page_size)
        
        # Order by created_at descending (newest first)
        query = query.order_by(Issue.created_at.desc())
        
        issues = query.all()
        
        # Cache the results
        cache_data = {
            "issue_ids": [issue.id for issue in issues],
            "total": total
        }
        self._set_cache(cache_key, cache_data)
        
        return issues, total
    
    def search_issues(
        self,
        search_query: str,
        filters: Optional[IssueFilters] = None,
        pagination: Optional[PaginationParams] = None
    ) -> Tuple[List[Issue], int]:
        """
        Search issues by text query with optional filters.
        
        Args:
            search_query: Text to search in title and description
            filters: Optional additional filters
            pagination: Optional pagination parameters
            
        Returns:
            Tuple of (issues list, total count)
        """
        # Create or update filters with search query
        if filters is None:
            filters = IssueFilters(search_query=search_query)
        else:
            filters.search_query = search_query
        
        return self.get_filtered_issues(filters=filters, pagination=pagination)
    
    def get_issue_by_id(self, issue_id: int) -> Optional[Issue]:
        """
        Get issue by ID with caching.
        
        Args:
            issue_id: Issue ID
            
        Returns:
            Issue object or None if not found
        """
        cache_key = self._get_cache_key("single", id=issue_id)
        
        # Check cache
        cached_data = self._get_from_cache(cache_key)
        if cached_data and cached_data.get("exists"):
            return self.db.query(Issue).filter(Issue.id == issue_id).first()
        elif cached_data and not cached_data.get("exists"):
            return None
        
        # Query database
        issue = self.db.query(Issue).filter(Issue.id == issue_id).first()
        
        # Cache result
        self._set_cache(cache_key, {"exists": issue is not None})
        
        return issue
    
    def get_available_filters(self) -> dict:
        """
        Get available filter options (languages, labels, difficulties).
        
        Returns:
            Dictionary with available filter values
        """
        cache_key = self._get_cache_key("filters")
        
        # Check cache
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
        
        # Query distinct values
        languages = self.db.query(Issue.programming_language).filter(
            Issue.programming_language.isnot(None),
            Issue.status == IssueStatus.AVAILABLE
        ).distinct().all()
        
        difficulties = self.db.query(Issue.difficulty_level).filter(
            Issue.difficulty_level.isnot(None),
            Issue.status == IssueStatus.AVAILABLE
        ).distinct().all()
        
        # Get all unique labels from available issues
        issues_with_labels = self.db.query(Issue.labels).filter(
            Issue.status == IssueStatus.AVAILABLE
        ).all()
        
        all_labels = set()
        for (labels,) in issues_with_labels:
            if labels:
                all_labels.update(labels)
        
        result = {
            "languages": sorted([lang[0] for lang in languages if lang[0]]),
            "difficulties": sorted([diff[0] for diff in difficulties if diff[0]]),
            "labels": sorted(list(all_labels))
        }
        
        # Cache for longer (10 minutes)
        self._set_cache(cache_key, result, ttl=600)
        
        return result

    def claim_issue(self, issue_id: int, user_id: int) -> ClaimResult:
        """
        Claim an issue for a user.
        
        Args:
            issue_id: ID of the issue to claim
            user_id: ID of the user claiming the issue
            
        Returns:
            ClaimResult with success status and details
        """
        try:
            # Get the issue
            issue = self.db.query(Issue).filter(Issue.id == issue_id).first()
            
            if not issue:
                return ClaimResult(
                    success=False,
                    message="Issue not found"
                )
            
            # Check if issue is available
            if issue.status != IssueStatus.AVAILABLE:
                if issue.status == IssueStatus.CLAIMED:
                    claimer_info = f" by user {issue.claimed_by}" if issue.claimed_by else ""
                    return ClaimResult(
                        success=False,
                        message=f"Issue is already claimed{claimer_info}"
                    )
                else:
                    return ClaimResult(
                        success=False,
                        message=f"Issue is not available (status: {issue.status.value})"
                    )
            
            # Calculate claim expiration based on difficulty
            timeout_days = self._get_timeout_for_difficulty(issue.difficulty_level)
            claimed_at = datetime.utcnow()
            claim_expires_at = claimed_at + timedelta(days=timeout_days)
            
            # Update issue
            issue.status = IssueStatus.CLAIMED
            issue.claimed_by = user_id
            issue.claimed_at = claimed_at
            issue.claim_expires_at = claim_expires_at
            
            self.db.commit()
            self.db.refresh(issue)
            
            # Invalidate caches
            self._invalidate_cache_pattern("")
            
            logger.info(f"Issue {issue_id} claimed by user {user_id}, expires at {claim_expires_at}")
            
            return ClaimResult(
                success=True,
                message="Issue claimed successfully",
                issue_id=issue_id,
                claimed_at=claimed_at,
                claim_expires_at=claim_expires_at
            )
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error claiming issue {issue_id}: {str(e)}")
            return ClaimResult(
                success=False,
                message=f"Failed to claim issue: {str(e)}"
            )
    
    def _get_timeout_for_difficulty(self, difficulty_level: Optional[str]) -> int:
        """
        Get timeout days based on difficulty level.
        
        Args:
            difficulty_level: Issue difficulty level
            
        Returns:
            Number of days for claim timeout
        """
        if not difficulty_level:
            return settings.CLAIM_TIMEOUT_EASY_DAYS
        
        difficulty_map = {
            "easy": settings.CLAIM_TIMEOUT_EASY_DAYS,
            "medium": settings.CLAIM_TIMEOUT_MEDIUM_DAYS,
            "hard": settings.CLAIM_TIMEOUT_HARD_DAYS
        }
        
        return difficulty_map.get(difficulty_level.lower(), settings.CLAIM_TIMEOUT_EASY_DAYS)
    
    def release_issue(self, issue_id: int, user_id: int, force: bool = False) -> ReleaseResult:
        """
        Release a claimed issue.
        
        Args:
            issue_id: ID of the issue to release
            user_id: ID of the user releasing the issue
            force: If True, allows admin to release any issue
            
        Returns:
            ReleaseResult with success status and details
        """
        try:
            # Get the issue
            issue = self.db.query(Issue).filter(Issue.id == issue_id).first()
            
            if not issue:
                return ReleaseResult(
                    success=False,
                    message="Issue not found"
                )
            
            # Check if issue is claimed
            if issue.status != IssueStatus.CLAIMED:
                return ReleaseResult(
                    success=False,
                    message=f"Issue is not claimed (status: {issue.status.value})"
                )
            
            # Verify user owns the claim (unless force)
            if not force and issue.claimed_by != user_id:
                return ReleaseResult(
                    success=False,
                    message="You can only release issues you have claimed"
                )
            
            # Release the issue
            issue.status = IssueStatus.AVAILABLE
            issue.claimed_by = None
            issue.claimed_at = None
            issue.claim_expires_at = None
            
            self.db.commit()
            self.db.refresh(issue)
            
            # Invalidate caches
            self._invalidate_cache_pattern("")
            
            logger.info(f"Issue {issue_id} released by user {user_id}")
            
            return ReleaseResult(
                success=True,
                message="Issue released successfully",
                issue_id=issue_id
            )
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error releasing issue {issue_id}: {str(e)}")
            return ReleaseResult(
                success=False,
                message=f"Failed to release issue: {str(e)}"
            )
    
    def extend_claim_deadline(
        self,
        issue_id: int,
        user_id: int,
        extension_days: int = 7,
        justification: Optional[str] = None
    ) -> ExtensionResult:
        """
        Extend the claim deadline for an issue.
        
        Args:
            issue_id: ID of the issue
            user_id: ID of the user requesting extension
            extension_days: Number of days to extend (default 7)
            justification: Reason for extension request
            
        Returns:
            ExtensionResult with success status and new expiration
        """
        try:
            # Get the issue
            issue = self.db.query(Issue).filter(Issue.id == issue_id).first()
            
            if not issue:
                return ExtensionResult(
                    success=False,
                    message="Issue not found"
                )
            
            # Check if issue is claimed by the user
            if issue.status != IssueStatus.CLAIMED:
                return ExtensionResult(
                    success=False,
                    message="Issue is not claimed"
                )
            
            if issue.claimed_by != user_id:
                return ExtensionResult(
                    success=False,
                    message="You can only extend deadlines for issues you have claimed"
                )
            
            # Check if claim has already expired
            if issue.claim_expires_at and issue.claim_expires_at < datetime.utcnow():
                return ExtensionResult(
                    success=False,
                    message="Cannot extend expired claim. Please claim the issue again."
                )
            
            # Extend the deadline
            if issue.claim_expires_at:
                new_expiration = issue.claim_expires_at + timedelta(days=extension_days)
            else:
                # Fallback if no expiration set
                new_expiration = datetime.utcnow() + timedelta(days=extension_days)
            
            issue.claim_expires_at = new_expiration
            
            self.db.commit()
            self.db.refresh(issue)
            
            # Invalidate caches
            self._invalidate_cache_pattern("")
            
            logger.info(
                f"Issue {issue_id} deadline extended by {extension_days} days for user {user_id}. "
                f"New expiration: {new_expiration}. Justification: {justification}"
            )
            
            return ExtensionResult(
                success=True,
                message=f"Deadline extended by {extension_days} days",
                issue_id=issue_id,
                new_expiration=new_expiration
            )
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error extending deadline for issue {issue_id}: {str(e)}")
            return ExtensionResult(
                success=False,
                message=f"Failed to extend deadline: {str(e)}"
            )
    
    def auto_release_expired_claims(self) -> AutoReleaseResult:
        """
        Automatically release expired claims.
        
        This method should be called by a background job (Celery task).
        It finds all claimed issues with expired deadlines and releases them.
        
        Returns:
            AutoReleaseResult with count of released issues and any errors
        """
        released_ids = []
        errors = []
        
        try:
            # Find all claimed issues with expired deadlines
            now = datetime.utcnow()
            expired_issues = self.db.query(Issue).filter(
                Issue.status == IssueStatus.CLAIMED,
                Issue.claim_expires_at.isnot(None),
                Issue.claim_expires_at < now
            ).all()
            
            logger.info(f"Found {len(expired_issues)} expired claims to release")
            
            for issue in expired_issues:
                try:
                    # Release the issue
                    issue.status = IssueStatus.AVAILABLE
                    old_claimer = issue.claimed_by
                    issue.claimed_by = None
                    issue.claimed_at = None
                    issue.claim_expires_at = None
                    
                    released_ids.append(issue.id)
                    
                    logger.info(f"Auto-released issue {issue.id} (was claimed by user {old_claimer})")
                    
                except Exception as e:
                    error_msg = f"Failed to release issue {issue.id}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
            
            # Commit all changes
            self.db.commit()
            
            # Invalidate caches
            if released_ids:
                self._invalidate_cache_pattern("")
            
            logger.info(f"Auto-release completed: {len(released_ids)} issues released")
            
            return AutoReleaseResult(
                released_count=len(released_ids),
                issue_ids=released_ids,
                errors=errors
            )
            
        except Exception as e:
            self.db.rollback()
            error_msg = f"Auto-release failed: {str(e)}"
            logger.error(error_msg)
            return AutoReleaseResult(
                released_count=0,
                issue_ids=[],
                errors=[error_msg]
            )
    
    def get_expiring_claims(self, hours_threshold: int = 24) -> List[Issue]:
        """
        Get claims that are expiring within the specified threshold.
        
        Useful for sending reminder notifications.
        
        Args:
            hours_threshold: Number of hours before expiration to consider
            
        Returns:
            List of issues expiring soon
        """
        try:
            now = datetime.utcnow()
            threshold_time = now + timedelta(hours=hours_threshold)
            
            expiring_issues = self.db.query(Issue).filter(
                Issue.status == IssueStatus.CLAIMED,
                Issue.claim_expires_at.isnot(None),
                Issue.claim_expires_at > now,
                Issue.claim_expires_at <= threshold_time
            ).all()
            
            return expiring_issues
            
        except Exception as e:
            logger.error(f"Error fetching expiring claims: {str(e)}")
            return []
