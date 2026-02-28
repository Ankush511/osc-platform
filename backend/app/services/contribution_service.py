"""
Contribution service for PR validation and scoring
"""
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
import re

from app.models.contribution import Contribution, ContributionStatus
from app.models.issue import Issue, IssueStatus
from app.models.user import User
from app.models.repository import Repository
from app.services.github_service import GitHubService
from app.services.achievement_service import AchievementService
from app.schemas.contribution import (
    SubmissionResult,
    ValidationResult,
    PRStatusUpdate,
    ContributionStats
)

logger = logging.getLogger(__name__)


class ContributionService:
    """
    Service for managing contributions and PR validation.
    
    Handles:
    - PR submission and validation
    - Contribution scoring
    - PR status tracking
    - User statistics updates
    """
    
    # Points awarded for different contribution outcomes
    POINTS_SUBMITTED = 10
    POINTS_MERGED = 100
    POINTS_CLOSED = 0
    
    def __init__(self, db: Session, github_token: Optional[str] = None):
        """
        Initialize contribution service.
        
        Args:
            db: Database session
            github_token: Optional GitHub access token for API calls
        """
        self.db = db
        self.github_service = GitHubService(access_token=github_token)
    
    async def submit_pr(
        self,
        issue_id: int,
        pr_url: str,
        user_id: int
    ) -> SubmissionResult:
        """
        Submit a pull request for validation.
        
        Validates:
        1. Issue exists and is claimed by the user
        2. PR URL is valid and exists on GitHub
        3. PR is created by the registered user
        4. PR is linked to the correct issue (optional but recommended)
        
        Args:
            issue_id: ID of the claimed issue
            pr_url: GitHub PR URL
            user_id: ID of the user submitting the PR
            
        Returns:
            SubmissionResult with validation outcome
        """
        try:
            # Validate issue exists and is claimed by user
            issue = self.db.query(Issue).filter(Issue.id == issue_id).first()
            if not issue:
                return SubmissionResult(
                    success=False,
                    message="Issue not found"
                )
            
            if issue.status != IssueStatus.CLAIMED:
                return SubmissionResult(
                    success=False,
                    message="Issue is not claimed. Only claimed issues can have PRs submitted."
                )
            
            if issue.claimed_by != user_id:
                return SubmissionResult(
                    success=False,
                    message=f"Issue is claimed by another user. You can only submit PRs for issues you have claimed."
                )
            
            # Get user info
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return SubmissionResult(
                    success=False,
                    message="User not found"
                )
            
            # Check if PR already submitted for this issue
            existing_contribution = self.db.query(Contribution).filter(
                Contribution.issue_id == issue_id,
                Contribution.user_id == user_id
            ).first()
            
            if existing_contribution:
                return SubmissionResult(
                    success=False,
                    message="A PR has already been submitted for this issue"
                )
            
            # Validate PR with GitHub API
            validation = await self.github_service.validate_pull_request(
                pr_url=pr_url,
                expected_user=user.github_username
            )
            
            if not validation.is_valid:
                return SubmissionResult(
                    success=False,
                    message=validation.error_message or "PR validation failed"
                )
            
            # Check if PR is linked to the correct issue (warning, not error)
            issue_number = self._extract_issue_number_from_url(issue.github_url)
            if validation.linked_issue and validation.linked_issue != issue_number:
                logger.warning(
                    f"PR {pr_url} is linked to issue #{validation.linked_issue} "
                    f"but submitted for issue #{issue_number}"
                )
            
            # Create contribution record
            contribution = Contribution(
                user_id=user_id,
                issue_id=issue_id,
                pr_url=pr_url,
                pr_number=validation.pr_number,
                status=ContributionStatus.MERGED if validation.is_merged else ContributionStatus.SUBMITTED,
                submitted_at=datetime.utcnow(),
                merged_at=datetime.utcnow() if validation.is_merged else None,
                points_earned=self.POINTS_MERGED if validation.is_merged else self.POINTS_SUBMITTED
            )
            
            self.db.add(contribution)
            
            # Update issue status to completed
            issue.status = IssueStatus.COMPLETED
            
            # Update user statistics
            user.total_contributions += 1
            if validation.is_merged:
                user.merged_prs += 1
            
            self.db.commit()
            self.db.refresh(contribution)
            
            # Check and award achievements
            achievement_service = AchievementService(self.db)
            newly_awarded = achievement_service.check_and_award_achievements(user_id)
            
            if newly_awarded:
                logger.info(f"User {user_id} earned {len(newly_awarded)} new achievements")
            
            logger.info(
                f"PR submitted successfully: user={user.github_username}, "
                f"issue={issue_id}, pr={validation.pr_number}, "
                f"merged={validation.is_merged}"
            )
            
            return SubmissionResult(
                success=True,
                message="Pull request submitted and validated successfully",
                contribution_id=contribution.id,
                pr_number=validation.pr_number,
                status=contribution.status.value,
                points_earned=contribution.points_earned
            )
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to submit PR: {str(e)}")
            return SubmissionResult(
                success=False,
                message=f"Failed to submit PR: {str(e)}"
            )
        finally:
            await self.github_service.close()
    
    def _extract_issue_number_from_url(self, github_url: str) -> Optional[int]:
        """
        Extract issue number from GitHub URL.
        
        Args:
            github_url: GitHub issue URL
            
        Returns:
            Issue number or None if not found
        """
        match = re.search(r'/issues/(\d+)', github_url)
        return int(match.group(1)) if match else None
    
    async def update_pr_status(
        self,
        pr_url: str,
        pr_number: int,
        action: str,
        merged: bool = False,
        merged_at: Optional[datetime] = None
    ) -> bool:
        """
        Update PR status from webhook event.
        
        Args:
            pr_url: GitHub PR URL
            pr_number: PR number
            action: Webhook action (opened, closed, merged, etc.)
            merged: Whether PR was merged
            merged_at: Timestamp when PR was merged
            
        Returns:
            True if update was successful
        """
        try:
            # Find contribution by PR URL or PR number
            contribution = self.db.query(Contribution).filter(
                (Contribution.pr_url == pr_url) | (Contribution.pr_number == pr_number)
            ).first()
            
            if not contribution:
                logger.warning(f"No contribution found for PR {pr_url}")
                return False
            
            # Update status based on action
            old_status = contribution.status
            
            if merged:
                contribution.status = ContributionStatus.MERGED
                contribution.merged_at = merged_at or datetime.utcnow()
                
                # Award merge points if not already awarded
                if old_status != ContributionStatus.MERGED:
                    contribution.points_earned = self.POINTS_MERGED
                    
                    # Update user statistics
                    user = self.db.query(User).filter(User.id == contribution.user_id).first()
                    if user:
                        user.merged_prs += 1
                        
            elif action == "closed" and not merged:
                contribution.status = ContributionStatus.CLOSED
                contribution.points_earned = self.POINTS_CLOSED
            
            self.db.commit()
            
            # Check and award achievements when PR is merged
            if merged and old_status != ContributionStatus.MERGED:
                achievement_service = AchievementService(self.db)
                newly_awarded = achievement_service.check_and_award_achievements(contribution.user_id)
                
                if newly_awarded:
                    logger.info(f"User {contribution.user_id} earned {len(newly_awarded)} new achievements")
            
            logger.info(
                f"Updated PR status: pr={pr_number}, "
                f"old_status={old_status}, new_status={contribution.status}"
            )
            
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update PR status: {str(e)}")
            return False
    
    def get_user_contributions(
        self,
        user_id: int,
        status: Optional[ContributionStatus] = None
    ) -> List[Contribution]:
        """
        Get contributions for a user.
        
        Args:
            user_id: User ID
            status: Optional status filter
            
        Returns:
            List of contributions
        """
        query = self.db.query(Contribution).filter(Contribution.user_id == user_id)
        
        if status:
            query = query.filter(Contribution.status == status)
        
        return query.order_by(Contribution.submitted_at.desc()).all()
    
    def get_contribution_by_id(self, contribution_id: int) -> Optional[Contribution]:
        """
        Get a contribution by ID.
        
        Args:
            contribution_id: Contribution ID
            
        Returns:
            Contribution or None if not found
        """
        return self.db.query(Contribution).filter(Contribution.id == contribution_id).first()
    
    def get_user_stats(self, user_id: int) -> ContributionStats:
        """
        Get contribution statistics for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            ContributionStats with aggregated data
        """
        contributions = self.get_user_contributions(user_id)
        
        total_contributions = len(contributions)
        submitted_prs = sum(1 for c in contributions if c.status == ContributionStatus.SUBMITTED)
        merged_prs = sum(1 for c in contributions if c.status == ContributionStatus.MERGED)
        closed_prs = sum(1 for c in contributions if c.status == ContributionStatus.CLOSED)
        total_points = sum(c.points_earned for c in contributions)
        
        # Group by language
        contributions_by_language: Dict[str, int] = {}
        contributions_by_repository: Dict[str, int] = {}
        
        for contribution in contributions:
            issue = contribution.issue
            if issue:
                # By language
                lang = issue.programming_language or "Unknown"
                contributions_by_language[lang] = contributions_by_language.get(lang, 0) + 1
                
                # By repository
                if issue.repository:
                    repo_name = issue.repository.full_name
                    contributions_by_repository[repo_name] = contributions_by_repository.get(repo_name, 0) + 1
        
        return ContributionStats(
            total_contributions=total_contributions,
            submitted_prs=submitted_prs,
            merged_prs=merged_prs,
            closed_prs=closed_prs,
            total_points=total_points,
            contributions_by_language=contributions_by_language,
            contributions_by_repository=contributions_by_repository
        )
    
    def calculate_contribution_score(self, contribution: Contribution) -> int:
        """
        Calculate score for a contribution based on status.
        
        Args:
            contribution: Contribution object
            
        Returns:
            Points earned
        """
        if contribution.status == ContributionStatus.MERGED:
            return self.POINTS_MERGED
        elif contribution.status == ContributionStatus.SUBMITTED:
            return self.POINTS_SUBMITTED
        else:
            return self.POINTS_CLOSED
