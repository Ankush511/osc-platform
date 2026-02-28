"""
Unit tests for contribution service
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.contribution_service import ContributionService
from app.models.contribution import Contribution, ContributionStatus
from app.models.issue import Issue, IssueStatus
from app.models.user import User
from app.schemas.github import PRValidation


class TestContributionService:
    """Test contribution service functionality"""
    
    @pytest.mark.asyncio
    async def test_submit_pr_success(self, db_session, test_user, sample_issue):
        """Test successful PR submission"""
        # Claim the issue first
        sample_issue.status = IssueStatus.CLAIMED
        sample_issue.claimed_by = test_user.id
        sample_issue.claimed_at = datetime.utcnow()
        db_session.commit()
        
        # Mock GitHub service validation
        mock_validation = PRValidation(
            is_valid=True,
            pr_number=123,
            pr_url="https://github.com/test-org/test-repo/pull/123",
            author="testuser",
            is_merged=False,
            linked_issue=1,
            error_message=None
        )
        
        service = ContributionService(db=db_session)
        
        with patch.object(service.github_service, 'validate_pull_request', new_callable=AsyncMock) as mock_validate:
            mock_validate.return_value = mock_validation
            
            result = await service.submit_pr(
                issue_id=sample_issue.id,
                pr_url="https://github.com/test-org/test-repo/pull/123",
                user_id=test_user.id
            )
        
        assert result.success is True
        assert result.pr_number == 123
        assert result.status == "submitted"
        assert result.points_earned == ContributionService.POINTS_SUBMITTED
        
        # Verify contribution was created
        contribution = db_session.query(Contribution).filter(
            Contribution.user_id == test_user.id,
            Contribution.issue_id == sample_issue.id
        ).first()
        
        assert contribution is not None
        assert contribution.pr_number == 123
        assert contribution.status == ContributionStatus.SUBMITTED
        
        # Verify issue status updated
        db_session.refresh(sample_issue)
        assert sample_issue.status == IssueStatus.COMPLETED
        
        # Verify user stats updated
        db_session.refresh(test_user)
        assert test_user.total_contributions == 1
    
    @pytest.mark.asyncio
    async def test_submit_pr_already_merged(self, db_session, test_user, sample_issue):
        """Test PR submission when PR is already merged"""
        # Claim the issue first
        sample_issue.status = IssueStatus.CLAIMED
        sample_issue.claimed_by = test_user.id
        db_session.commit()
        
        # Mock GitHub service validation with merged PR
        mock_validation = PRValidation(
            is_valid=True,
            pr_number=123,
            pr_url="https://github.com/test-org/test-repo/pull/123",
            author="testuser",
            is_merged=True,
            linked_issue=1,
            error_message=None
        )
        
        service = ContributionService(db=db_session)
        
        with patch.object(service.github_service, 'validate_pull_request', new_callable=AsyncMock) as mock_validate:
            mock_validate.return_value = mock_validation
            
            result = await service.submit_pr(
                issue_id=sample_issue.id,
                pr_url="https://github.com/test-org/test-repo/pull/123",
                user_id=test_user.id
            )
        
        assert result.success is True
        assert result.status == "merged"
        assert result.points_earned == ContributionService.POINTS_MERGED
        
        # Verify user stats updated with merged PR
        db_session.refresh(test_user)
        assert test_user.total_contributions == 1
        assert test_user.merged_prs == 1
    
    @pytest.mark.asyncio
    async def test_submit_pr_issue_not_claimed(self, db_session, test_user, sample_issue):
        """Test PR submission fails when issue is not claimed"""
        service = ContributionService(db=db_session)
        
        result = await service.submit_pr(
            issue_id=sample_issue.id,
            pr_url="https://github.com/test-org/test-repo/pull/123",
            user_id=test_user.id
        )
        
        assert result.success is False
        assert "not claimed" in result.message.lower()
    
    @pytest.mark.asyncio
    async def test_submit_pr_claimed_by_different_user(self, db_session, test_user, second_user, sample_issue):
        """Test PR submission fails when issue is claimed by different user"""
        # Claim issue with second user
        sample_issue.status = IssueStatus.CLAIMED
        sample_issue.claimed_by = second_user.id
        db_session.commit()
        
        service = ContributionService(db=db_session)
        
        result = await service.submit_pr(
            issue_id=sample_issue.id,
            pr_url="https://github.com/test-org/test-repo/pull/123",
            user_id=test_user.id
        )
        
        assert result.success is False
        assert "claimed by another user" in result.message.lower()
    
    @pytest.mark.asyncio
    async def test_submit_pr_invalid_author(self, db_session, test_user, sample_issue):
        """Test PR submission fails when PR author doesn't match user"""
        # Claim the issue
        sample_issue.status = IssueStatus.CLAIMED
        sample_issue.claimed_by = test_user.id
        db_session.commit()
        
        # Mock GitHub service validation with wrong author
        mock_validation = PRValidation(
            is_valid=False,
            pr_number=123,
            pr_url="https://github.com/test-org/test-repo/pull/123",
            author="wronguser",
            is_merged=False,
            error_message="PR author 'wronguser' does not match expected user 'testuser'"
        )
        
        service = ContributionService(db=db_session)
        
        with patch.object(service.github_service, 'validate_pull_request', new_callable=AsyncMock) as mock_validate:
            mock_validate.return_value = mock_validation
            
            result = await service.submit_pr(
                issue_id=sample_issue.id,
                pr_url="https://github.com/test-org/test-repo/pull/123",
                user_id=test_user.id
            )
        
        assert result.success is False
        assert "does not match" in result.message.lower()
    
    @pytest.mark.asyncio
    async def test_submit_pr_duplicate(self, db_session, test_user, sample_issue):
        """Test PR submission fails when PR already submitted"""
        # Claim the issue and create existing contribution
        sample_issue.status = IssueStatus.CLAIMED
        sample_issue.claimed_by = test_user.id
        db_session.commit()
        
        existing_contribution = Contribution(
            user_id=test_user.id,
            issue_id=sample_issue.id,
            pr_url="https://github.com/test-org/test-repo/pull/100",
            pr_number=100,
            status=ContributionStatus.SUBMITTED
        )
        db_session.add(existing_contribution)
        db_session.commit()
        
        service = ContributionService(db=db_session)
        
        result = await service.submit_pr(
            issue_id=sample_issue.id,
            pr_url="https://github.com/test-org/test-repo/pull/123",
            user_id=test_user.id
        )
        
        assert result.success is False
        assert "already been submitted" in result.message.lower()
    
    @pytest.mark.asyncio
    async def test_update_pr_status_to_merged(self, db_session, test_user, sample_issue):
        """Test updating PR status to merged"""
        # Create a submitted contribution
        contribution = Contribution(
            user_id=test_user.id,
            issue_id=sample_issue.id,
            pr_url="https://github.com/test-org/test-repo/pull/123",
            pr_number=123,
            status=ContributionStatus.SUBMITTED,
            points_earned=ContributionService.POINTS_SUBMITTED
        )
        db_session.add(contribution)
        db_session.commit()
        
        service = ContributionService(db=db_session)
        
        # Update to merged
        success = await service.update_pr_status(
            pr_url="https://github.com/test-org/test-repo/pull/123",
            pr_number=123,
            action="closed",
            merged=True,
            merged_at=datetime.utcnow()
        )
        
        assert success is True
        
        # Verify contribution updated
        db_session.refresh(contribution)
        assert contribution.status == ContributionStatus.MERGED
        assert contribution.merged_at is not None
        assert contribution.points_earned == ContributionService.POINTS_MERGED
        
        # Verify user stats updated
        db_session.refresh(test_user)
        assert test_user.merged_prs == 1
    
    @pytest.mark.asyncio
    async def test_update_pr_status_to_closed(self, db_session, test_user, sample_issue):
        """Test updating PR status to closed without merge"""
        # Create a submitted contribution
        contribution = Contribution(
            user_id=test_user.id,
            issue_id=sample_issue.id,
            pr_url="https://github.com/test-org/test-repo/pull/123",
            pr_number=123,
            status=ContributionStatus.SUBMITTED,
            points_earned=ContributionService.POINTS_SUBMITTED
        )
        db_session.add(contribution)
        db_session.commit()
        
        service = ContributionService(db=db_session)
        
        # Update to closed
        success = await service.update_pr_status(
            pr_url="https://github.com/test-org/test-repo/pull/123",
            pr_number=123,
            action="closed",
            merged=False
        )
        
        assert success is True
        
        # Verify contribution updated
        db_session.refresh(contribution)
        assert contribution.status == ContributionStatus.CLOSED
        assert contribution.points_earned == ContributionService.POINTS_CLOSED
    
    def test_get_user_contributions(self, db_session, test_user, sample_issue):
        """Test getting user contributions"""
        # Create multiple contributions
        contribution1 = Contribution(
            user_id=test_user.id,
            issue_id=sample_issue.id,
            pr_url="https://github.com/test-org/test-repo/pull/123",
            pr_number=123,
            status=ContributionStatus.SUBMITTED
        )
        contribution2 = Contribution(
            user_id=test_user.id,
            issue_id=sample_issue.id,
            pr_url="https://github.com/test-org/test-repo/pull/124",
            pr_number=124,
            status=ContributionStatus.MERGED
        )
        db_session.add_all([contribution1, contribution2])
        db_session.commit()
        
        service = ContributionService(db=db_session)
        
        # Get all contributions
        contributions = service.get_user_contributions(test_user.id)
        assert len(contributions) == 2
        
        # Get only merged contributions
        merged_contributions = service.get_user_contributions(
            test_user.id,
            status=ContributionStatus.MERGED
        )
        assert len(merged_contributions) == 1
        assert merged_contributions[0].status == ContributionStatus.MERGED
    
    def test_get_user_stats(self, db_session, test_user, sample_issue, sample_repository):
        """Test getting user contribution statistics"""
        # Create contributions with different statuses
        contribution1 = Contribution(
            user_id=test_user.id,
            issue_id=sample_issue.id,
            pr_url="https://github.com/test-org/test-repo/pull/123",
            pr_number=123,
            status=ContributionStatus.SUBMITTED,
            points_earned=ContributionService.POINTS_SUBMITTED
        )
        contribution2 = Contribution(
            user_id=test_user.id,
            issue_id=sample_issue.id,
            pr_url="https://github.com/test-org/test-repo/pull/124",
            pr_number=124,
            status=ContributionStatus.MERGED,
            points_earned=ContributionService.POINTS_MERGED
        )
        contribution3 = Contribution(
            user_id=test_user.id,
            issue_id=sample_issue.id,
            pr_url="https://github.com/test-org/test-repo/pull/125",
            pr_number=125,
            status=ContributionStatus.CLOSED,
            points_earned=ContributionService.POINTS_CLOSED
        )
        db_session.add_all([contribution1, contribution2, contribution3])
        db_session.commit()
        
        service = ContributionService(db=db_session)
        stats = service.get_user_stats(test_user.id)
        
        assert stats.total_contributions == 3
        assert stats.submitted_prs == 1
        assert stats.merged_prs == 1
        assert stats.closed_prs == 1
        assert stats.total_points == ContributionService.POINTS_SUBMITTED + ContributionService.POINTS_MERGED
        
        # Check language breakdown
        assert "Python" in stats.contributions_by_language
        assert stats.contributions_by_language["Python"] == 3
        
        # Check repository breakdown
        assert "test-org/test-repo" in stats.contributions_by_repository
        assert stats.contributions_by_repository["test-org/test-repo"] == 3
    
    def test_calculate_contribution_score(self, db_session, test_user, sample_issue):
        """Test contribution score calculation"""
        service = ContributionService(db=db_session)
        
        # Test submitted contribution
        submitted_contribution = Contribution(
            user_id=test_user.id,
            issue_id=sample_issue.id,
            pr_url="https://github.com/test-org/test-repo/pull/123",
            pr_number=123,
            status=ContributionStatus.SUBMITTED
        )
        assert service.calculate_contribution_score(submitted_contribution) == ContributionService.POINTS_SUBMITTED
        
        # Test merged contribution
        merged_contribution = Contribution(
            user_id=test_user.id,
            issue_id=sample_issue.id,
            pr_url="https://github.com/test-org/test-repo/pull/124",
            pr_number=124,
            status=ContributionStatus.MERGED
        )
        assert service.calculate_contribution_score(merged_contribution) == ContributionService.POINTS_MERGED
        
        # Test closed contribution
        closed_contribution = Contribution(
            user_id=test_user.id,
            issue_id=sample_issue.id,
            pr_url="https://github.com/test-org/test-repo/pull/125",
            pr_number=125,
            status=ContributionStatus.CLOSED
        )
        assert service.calculate_contribution_score(closed_contribution) == ContributionService.POINTS_CLOSED
