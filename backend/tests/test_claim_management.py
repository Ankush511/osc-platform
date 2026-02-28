"""
Comprehensive tests for issue claim management system
"""
import pytest
from datetime import datetime, timedelta
from app.services.issue_service import IssueService
from app.models.issue import Issue, IssueStatus
from app.models.user import User
from app.models.repository import Repository


@pytest.fixture
def issue_service(db_session):
    """Create an IssueService instance"""
    return IssueService(db=db_session)


@pytest.fixture
def second_user(db_session):
    """Create a second test user"""
    user = User(
        github_username="seconduser",
        github_id=54321,
        email="second@example.com",
        avatar_url="https://example.com/avatar2.png",
        full_name="Second User",
        preferred_languages=[],
        preferred_labels=[]
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def easy_issue(db_session, sample_repository):
    """Create an easy difficulty issue"""
    issue = Issue(
        github_issue_id=11111,
        repository_id=sample_repository.id,
        title="Fix typo in README",
        description="Simple typo fix needed",
        labels=["good first issue", "documentation"],
        programming_language="Markdown",
        difficulty_level="easy",
        status=IssueStatus.AVAILABLE,
        github_url="https://github.com/test-org/test-repo/issues/11"
    )
    db_session.add(issue)
    db_session.commit()
    db_session.refresh(issue)
    return issue


@pytest.fixture
def medium_issue(db_session, sample_repository):
    """Create a medium difficulty issue"""
    issue = Issue(
        github_issue_id=22222,
        repository_id=sample_repository.id,
        title="Add input validation",
        description="Add validation for user inputs",
        labels=["enhancement", "medium"],
        programming_language="Python",
        difficulty_level="medium",
        status=IssueStatus.AVAILABLE,
        github_url="https://github.com/test-org/test-repo/issues/22"
    )
    db_session.add(issue)
    db_session.commit()
    db_session.refresh(issue)
    return issue


@pytest.fixture
def hard_issue(db_session, sample_repository):
    """Create a hard difficulty issue"""
    issue = Issue(
        github_issue_id=33333,
        repository_id=sample_repository.id,
        title="Refactor authentication system",
        description="Complete overhaul of auth system",
        labels=["refactoring", "hard"],
        programming_language="Python",
        difficulty_level="hard",
        status=IssueStatus.AVAILABLE,
        github_url="https://github.com/test-org/test-repo/issues/33"
    )
    db_session.add(issue)
    db_session.commit()
    db_session.refresh(issue)
    return issue


class TestClaimIssue:
    """Tests for claiming issues"""
    
    def test_claim_available_issue_success(self, issue_service, sample_issue, test_user):
        """Test successfully claiming an available issue"""
        result = issue_service.claim_issue(sample_issue.id, test_user.id)
        
        assert result.success is True
        assert result.issue_id == sample_issue.id
        assert result.claimed_at is not None
        assert result.claim_expires_at is not None
        assert "successfully" in result.message.lower()
        
        # Verify database state
        issue_service.db.refresh(sample_issue)
        assert sample_issue.status == IssueStatus.CLAIMED
        assert sample_issue.claimed_by == test_user.id
        assert sample_issue.claimed_at is not None
        assert sample_issue.claim_expires_at is not None
    
    def test_claim_easy_issue_timeout(self, issue_service, easy_issue, test_user):
        """Test that easy issues get 7-day timeout"""
        result = issue_service.claim_issue(easy_issue.id, test_user.id)
        
        assert result.success is True
        
        # Check timeout is approximately 7 days
        time_diff = result.claim_expires_at - result.claimed_at
        assert 6.9 <= time_diff.days <= 7.1
    
    def test_claim_medium_issue_timeout(self, issue_service, medium_issue, test_user):
        """Test that medium issues get 14-day timeout"""
        result = issue_service.claim_issue(medium_issue.id, test_user.id)
        
        assert result.success is True
        
        # Check timeout is approximately 14 days
        time_diff = result.claim_expires_at - result.claimed_at
        assert 13.9 <= time_diff.days <= 14.1
    
    def test_claim_hard_issue_timeout(self, issue_service, hard_issue, test_user):
        """Test that hard issues get 21-day timeout"""
        result = issue_service.claim_issue(hard_issue.id, test_user.id)
        
        assert result.success is True
        
        # Check timeout is approximately 21 days
        time_diff = result.claim_expires_at - result.claimed_at
        assert 20.9 <= time_diff.days <= 21.1
    
    def test_claim_already_claimed_issue(self, issue_service, sample_issue, test_user, second_user):
        """Test that claiming an already claimed issue fails"""
        # First user claims the issue
        result1 = issue_service.claim_issue(sample_issue.id, test_user.id)
        assert result1.success is True
        
        # Second user tries to claim the same issue
        result2 = issue_service.claim_issue(sample_issue.id, second_user.id)
        assert result2.success is False
        assert "already claimed" in result2.message.lower()
    
    def test_claim_nonexistent_issue(self, issue_service, test_user):
        """Test claiming a non-existent issue"""
        result = issue_service.claim_issue(99999, test_user.id)
        
        assert result.success is False
        assert "not found" in result.message.lower()
    
    def test_claim_completed_issue(self, issue_service, sample_issue, test_user):
        """Test that completed issues cannot be claimed"""
        # Mark issue as completed
        sample_issue.status = IssueStatus.COMPLETED
        issue_service.db.commit()
        
        result = issue_service.claim_issue(sample_issue.id, test_user.id)
        
        assert result.success is False
        assert "not available" in result.message.lower()
    
    def test_claim_closed_issue(self, issue_service, sample_issue, test_user):
        """Test that closed issues cannot be claimed"""
        # Mark issue as closed
        sample_issue.status = IssueStatus.CLOSED
        issue_service.db.commit()
        
        result = issue_service.claim_issue(sample_issue.id, test_user.id)
        
        assert result.success is False
        assert "not available" in result.message.lower()


class TestReleaseIssue:
    """Tests for releasing claimed issues"""
    
    def test_release_claimed_issue_success(self, issue_service, sample_issue, test_user):
        """Test successfully releasing a claimed issue"""
        # First claim the issue
        claim_result = issue_service.claim_issue(sample_issue.id, test_user.id)
        assert claim_result.success is True
        
        # Then release it
        release_result = issue_service.release_issue(sample_issue.id, test_user.id)
        
        assert release_result.success is True
        assert release_result.issue_id == sample_issue.id
        assert "successfully" in release_result.message.lower()
        
        # Verify database state
        issue_service.db.refresh(sample_issue)
        assert sample_issue.status == IssueStatus.AVAILABLE
        assert sample_issue.claimed_by is None
        assert sample_issue.claimed_at is None
        assert sample_issue.claim_expires_at is None
    
    def test_release_unclaimed_issue(self, issue_service, sample_issue, test_user):
        """Test that releasing an unclaimed issue fails"""
        result = issue_service.release_issue(sample_issue.id, test_user.id)
        
        assert result.success is False
        assert "not claimed" in result.message.lower()
    
    def test_release_issue_claimed_by_another_user(self, issue_service, sample_issue, test_user, second_user):
        """Test that users cannot release issues claimed by others"""
        # First user claims the issue
        claim_result = issue_service.claim_issue(sample_issue.id, test_user.id)
        assert claim_result.success is True
        
        # Second user tries to release it
        release_result = issue_service.release_issue(sample_issue.id, second_user.id)
        
        assert release_result.success is False
        assert "only release issues you have claimed" in release_result.message.lower()
    
    def test_force_release_by_admin(self, issue_service, sample_issue, test_user, second_user):
        """Test that force release allows releasing any issue"""
        # First user claims the issue
        claim_result = issue_service.claim_issue(sample_issue.id, test_user.id)
        assert claim_result.success is True
        
        # Admin (second user) force releases it
        release_result = issue_service.release_issue(sample_issue.id, second_user.id, force=True)
        
        assert release_result.success is True
        
        # Verify issue is released
        issue_service.db.refresh(sample_issue)
        assert sample_issue.status == IssueStatus.AVAILABLE
    
    def test_release_nonexistent_issue(self, issue_service, test_user):
        """Test releasing a non-existent issue"""
        result = issue_service.release_issue(99999, test_user.id)
        
        assert result.success is False
        assert "not found" in result.message.lower()


class TestExtendClaimDeadline:
    """Tests for extending claim deadlines"""
    
    def test_extend_deadline_success(self, issue_service, sample_issue, test_user):
        """Test successfully extending a claim deadline"""
        # Claim the issue
        claim_result = issue_service.claim_issue(sample_issue.id, test_user.id)
        assert claim_result.success is True
        original_expiration = claim_result.claim_expires_at
        
        # Extend the deadline
        extension_result = issue_service.extend_claim_deadline(
            sample_issue.id,
            test_user.id,
            extension_days=7,
            justification="Need more time to complete testing"
        )
        
        assert extension_result.success is True
        assert extension_result.issue_id == sample_issue.id
        assert extension_result.new_expiration is not None
        assert extension_result.new_expiration > original_expiration
        
        # Verify extension is approximately 7 days
        time_diff = extension_result.new_expiration - original_expiration
        assert 6.9 <= time_diff.days <= 7.1
    
    def test_extend_deadline_custom_days(self, issue_service, sample_issue, test_user):
        """Test extending deadline with custom number of days"""
        # Claim the issue
        claim_result = issue_service.claim_issue(sample_issue.id, test_user.id)
        assert claim_result.success is True
        original_expiration = claim_result.claim_expires_at
        
        # Extend by 14 days
        extension_result = issue_service.extend_claim_deadline(
            sample_issue.id,
            test_user.id,
            extension_days=14,
            justification="Complex issue requires more time"
        )
        
        assert extension_result.success is True
        
        # Verify extension is approximately 14 days
        time_diff = extension_result.new_expiration - original_expiration
        assert 13.9 <= time_diff.days <= 14.1
    
    def test_extend_unclaimed_issue(self, issue_service, sample_issue, test_user):
        """Test that extending an unclaimed issue fails"""
        result = issue_service.extend_claim_deadline(
            sample_issue.id,
            test_user.id,
            extension_days=7,
            justification="Test"
        )
        
        assert result.success is False
        assert "not claimed" in result.message.lower()
    
    def test_extend_issue_claimed_by_another_user(self, issue_service, sample_issue, test_user, second_user):
        """Test that users cannot extend deadlines for issues claimed by others"""
        # First user claims the issue
        claim_result = issue_service.claim_issue(sample_issue.id, test_user.id)
        assert claim_result.success is True
        
        # Second user tries to extend
        extension_result = issue_service.extend_claim_deadline(
            sample_issue.id,
            second_user.id,
            extension_days=7,
            justification="Test"
        )
        
        assert extension_result.success is False
        assert "only extend deadlines for issues you have claimed" in extension_result.message.lower()
    
    def test_extend_expired_claim(self, issue_service, sample_issue, test_user):
        """Test that expired claims cannot be extended"""
        # Claim the issue
        claim_result = issue_service.claim_issue(sample_issue.id, test_user.id)
        assert claim_result.success is True
        
        # Manually set expiration to the past
        sample_issue.claim_expires_at = datetime.utcnow() - timedelta(days=1)
        issue_service.db.commit()
        
        # Try to extend
        extension_result = issue_service.extend_claim_deadline(
            sample_issue.id,
            test_user.id,
            extension_days=7,
            justification="Test"
        )
        
        assert extension_result.success is False
        assert "expired" in extension_result.message.lower()
    
    def test_extend_nonexistent_issue(self, issue_service, test_user):
        """Test extending deadline for non-existent issue"""
        result = issue_service.extend_claim_deadline(
            99999,
            test_user.id,
            extension_days=7,
            justification="Test"
        )
        
        assert result.success is False
        assert "not found" in result.message.lower()


class TestAutoReleaseExpiredClaims:
    """Tests for automatic release of expired claims"""
    
    def test_auto_release_single_expired_claim(self, issue_service, sample_issue, test_user):
        """Test auto-releasing a single expired claim"""
        # Claim the issue
        claim_result = issue_service.claim_issue(sample_issue.id, test_user.id)
        assert claim_result.success is True
        
        # Manually set expiration to the past
        sample_issue.claim_expires_at = datetime.utcnow() - timedelta(hours=1)
        issue_service.db.commit()
        
        # Run auto-release
        result = issue_service.auto_release_expired_claims()
        
        assert result.released_count == 1
        assert sample_issue.id in result.issue_ids
        assert len(result.errors) == 0
        
        # Verify issue is released
        issue_service.db.refresh(sample_issue)
        assert sample_issue.status == IssueStatus.AVAILABLE
        assert sample_issue.claimed_by is None
    
    def test_auto_release_multiple_expired_claims(self, issue_service, easy_issue, medium_issue, hard_issue, test_user):
        """Test auto-releasing multiple expired claims"""
        # Claim all issues
        issue_service.claim_issue(easy_issue.id, test_user.id)
        issue_service.claim_issue(medium_issue.id, test_user.id)
        issue_service.claim_issue(hard_issue.id, test_user.id)
        
        # Set all to expired
        for issue in [easy_issue, medium_issue, hard_issue]:
            issue.claim_expires_at = datetime.utcnow() - timedelta(hours=1)
        issue_service.db.commit()
        
        # Run auto-release
        result = issue_service.auto_release_expired_claims()
        
        assert result.released_count == 3
        assert easy_issue.id in result.issue_ids
        assert medium_issue.id in result.issue_ids
        assert hard_issue.id in result.issue_ids
        
        # Verify all issues are released
        for issue in [easy_issue, medium_issue, hard_issue]:
            issue_service.db.refresh(issue)
            assert issue.status == IssueStatus.AVAILABLE
    
    def test_auto_release_ignores_non_expired_claims(self, issue_service, sample_issue, test_user):
        """Test that auto-release doesn't affect non-expired claims"""
        # Claim the issue
        claim_result = issue_service.claim_issue(sample_issue.id, test_user.id)
        assert claim_result.success is True
        
        # Run auto-release (claim is not expired)
        result = issue_service.auto_release_expired_claims()
        
        assert result.released_count == 0
        assert sample_issue.id not in result.issue_ids
        
        # Verify issue is still claimed
        issue_service.db.refresh(sample_issue)
        assert sample_issue.status == IssueStatus.CLAIMED
        assert sample_issue.claimed_by == test_user.id
    
    def test_auto_release_mixed_expired_and_active(self, issue_service, easy_issue, medium_issue, test_user):
        """Test auto-release with mix of expired and active claims"""
        # Claim both issues
        issue_service.claim_issue(easy_issue.id, test_user.id)
        issue_service.claim_issue(medium_issue.id, test_user.id)
        
        # Only expire the easy issue
        easy_issue.claim_expires_at = datetime.utcnow() - timedelta(hours=1)
        issue_service.db.commit()
        
        # Run auto-release
        result = issue_service.auto_release_expired_claims()
        
        assert result.released_count == 1
        assert easy_issue.id in result.issue_ids
        assert medium_issue.id not in result.issue_ids
        
        # Verify states
        issue_service.db.refresh(easy_issue)
        issue_service.db.refresh(medium_issue)
        assert easy_issue.status == IssueStatus.AVAILABLE
        assert medium_issue.status == IssueStatus.CLAIMED
    
    def test_auto_release_no_expired_claims(self, issue_service):
        """Test auto-release when there are no expired claims"""
        result = issue_service.auto_release_expired_claims()
        
        assert result.released_count == 0
        assert len(result.issue_ids) == 0
        assert len(result.errors) == 0


class TestGetExpiringClaims:
    """Tests for getting expiring claims"""
    
    def test_get_expiring_claims_within_threshold(self, issue_service, sample_issue, test_user):
        """Test getting claims expiring within threshold"""
        # Claim the issue
        claim_result = issue_service.claim_issue(sample_issue.id, test_user.id)
        assert claim_result.success is True
        
        # Set expiration to 12 hours from now
        sample_issue.claim_expires_at = datetime.utcnow() + timedelta(hours=12)
        issue_service.db.commit()
        
        # Get expiring claims (24-hour threshold)
        expiring = issue_service.get_expiring_claims(hours_threshold=24)
        
        assert len(expiring) == 1
        assert expiring[0].id == sample_issue.id
    
    def test_get_expiring_claims_outside_threshold(self, issue_service, sample_issue, test_user):
        """Test that claims outside threshold are not returned"""
        # Claim the issue
        claim_result = issue_service.claim_issue(sample_issue.id, test_user.id)
        assert claim_result.success is True
        
        # Set expiration to 48 hours from now
        sample_issue.claim_expires_at = datetime.utcnow() + timedelta(hours=48)
        issue_service.db.commit()
        
        # Get expiring claims (24-hour threshold)
        expiring = issue_service.get_expiring_claims(hours_threshold=24)
        
        assert len(expiring) == 0
    
    def test_get_expiring_claims_already_expired(self, issue_service, sample_issue, test_user):
        """Test that already expired claims are not returned"""
        # Claim the issue
        claim_result = issue_service.claim_issue(sample_issue.id, test_user.id)
        assert claim_result.success is True
        
        # Set expiration to the past
        sample_issue.claim_expires_at = datetime.utcnow() - timedelta(hours=1)
        issue_service.db.commit()
        
        # Get expiring claims
        expiring = issue_service.get_expiring_claims(hours_threshold=24)
        
        assert len(expiring) == 0
    
    def test_get_expiring_claims_multiple(self, issue_service, easy_issue, medium_issue, hard_issue, test_user):
        """Test getting multiple expiring claims"""
        # Claim all issues
        issue_service.claim_issue(easy_issue.id, test_user.id)
        issue_service.claim_issue(medium_issue.id, test_user.id)
        issue_service.claim_issue(hard_issue.id, test_user.id)
        
        # Set two to expire within 24 hours
        easy_issue.claim_expires_at = datetime.utcnow() + timedelta(hours=12)
        medium_issue.claim_expires_at = datetime.utcnow() + timedelta(hours=20)
        hard_issue.claim_expires_at = datetime.utcnow() + timedelta(hours=48)
        issue_service.db.commit()
        
        # Get expiring claims
        expiring = issue_service.get_expiring_claims(hours_threshold=24)
        
        assert len(expiring) == 2
        expiring_ids = [issue.id for issue in expiring]
        assert easy_issue.id in expiring_ids
        assert medium_issue.id in expiring_ids
        assert hard_issue.id not in expiring_ids
    
    def test_get_expiring_claims_custom_threshold(self, issue_service, sample_issue, test_user):
        """Test getting expiring claims with custom threshold"""
        # Claim the issue
        claim_result = issue_service.claim_issue(sample_issue.id, test_user.id)
        assert claim_result.success is True
        
        # Set expiration to 10 hours from now
        sample_issue.claim_expires_at = datetime.utcnow() + timedelta(hours=10)
        issue_service.db.commit()
        
        # Should not be found with 6-hour threshold
        expiring_6h = issue_service.get_expiring_claims(hours_threshold=6)
        assert len(expiring_6h) == 0
        
        # Should be found with 12-hour threshold
        expiring_12h = issue_service.get_expiring_claims(hours_threshold=12)
        assert len(expiring_12h) == 1
        assert expiring_12h[0].id == sample_issue.id


class TestClaimManagementEdgeCases:
    """Tests for edge cases and error scenarios"""
    
    def test_claim_with_no_difficulty_level(self, issue_service, sample_issue, test_user):
        """Test claiming issue with no difficulty level defaults to easy timeout"""
        # Remove difficulty level
        sample_issue.difficulty_level = None
        issue_service.db.commit()
        
        result = issue_service.claim_issue(sample_issue.id, test_user.id)
        
        assert result.success is True
        
        # Should default to easy (7 days)
        time_diff = result.claim_expires_at - result.claimed_at
        assert 6.9 <= time_diff.days <= 7.1
    
    def test_multiple_claims_and_releases(self, issue_service, sample_issue, test_user, second_user):
        """Test multiple claim and release cycles"""
        # First user claims
        result1 = issue_service.claim_issue(sample_issue.id, test_user.id)
        assert result1.success is True
        
        # First user releases
        result2 = issue_service.release_issue(sample_issue.id, test_user.id)
        assert result2.success is True
        
        # Second user claims
        result3 = issue_service.claim_issue(sample_issue.id, second_user.id)
        assert result3.success is True
        
        # Verify second user owns it
        issue_service.db.refresh(sample_issue)
        assert sample_issue.claimed_by == second_user.id
    
    def test_extend_deadline_multiple_times(self, issue_service, sample_issue, test_user):
        """Test extending deadline multiple times"""
        # Claim the issue
        claim_result = issue_service.claim_issue(sample_issue.id, test_user.id)
        assert claim_result.success is True
        original_expiration = claim_result.claim_expires_at
        
        # First extension
        ext1 = issue_service.extend_claim_deadline(
            sample_issue.id, test_user.id, extension_days=7, justification="Need more time"
        )
        assert ext1.success is True
        
        # Second extension
        ext2 = issue_service.extend_claim_deadline(
            sample_issue.id, test_user.id, extension_days=7, justification="Still need more time"
        )
        assert ext2.success is True
        
        # Total extension should be approximately 14 days from original
        time_diff = ext2.new_expiration - original_expiration
        assert 13.9 <= time_diff.days <= 14.1
