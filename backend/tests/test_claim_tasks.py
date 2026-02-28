"""
Tests for Celery claim management tasks
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from app.tasks.claim_tasks import (
    auto_release_expired_claims_task,
    send_expiration_reminders_task,
    release_specific_claim_task
)
from app.models.issue import Issue, IssueStatus


class TestAutoReleaseExpiredClaimsTask:
    """Tests for auto_release_expired_claims_task"""
    
    @patch('app.tasks.claim_tasks.SessionLocal')
    @patch('app.tasks.claim_tasks.EmailService')
    def test_auto_release_task_success(self, mock_email_service, mock_session_local, db_session, sample_issue, test_user):
        """Test successful auto-release task execution with email notification"""
        # Setup mock to return our test session
        mock_session_local.return_value = db_session
        
        # Mock email service
        mock_email_instance = MagicMock()
        mock_email_service.return_value = mock_email_instance
        mock_email_instance.send_claim_released_notification.return_value = True
        
        # Claim and expire the issue
        sample_issue.status = IssueStatus.CLAIMED
        sample_issue.claimed_by = test_user.id
        sample_issue.claimed_at = datetime.utcnow() - timedelta(days=8)
        sample_issue.claim_expires_at = datetime.utcnow() - timedelta(hours=1)
        db_session.commit()
        
        # Run the task
        result = auto_release_expired_claims_task()
        
        assert result["released_count"] == 1
        assert sample_issue.id in result["issue_ids"]
        assert len(result["errors"]) == 0
        assert result["emails_sent"] == 1
        
        # Verify issue was released
        db_session.refresh(sample_issue)
        assert sample_issue.status == IssueStatus.AVAILABLE
        assert sample_issue.claimed_by is None
    
    @patch('app.tasks.claim_tasks.SessionLocal')
    def test_auto_release_task_no_expired_claims(self, mock_session_local, db_session):
        """Test auto-release task with no expired claims"""
        mock_session_local.return_value = db_session
        
        result = auto_release_expired_claims_task()
        
        assert result["released_count"] == 0
        assert len(result["issue_ids"]) == 0
        assert len(result["errors"]) == 0
    
    @patch('app.tasks.claim_tasks.SessionLocal')
    @patch('app.tasks.claim_tasks.EmailService')
    def test_auto_release_task_multiple_expired(
        self, mock_email_service, mock_session_local, db_session, sample_repository, test_user
    ):
        """Test auto-release task with multiple expired claims"""
        mock_session_local.return_value = db_session
        
        # Mock email service
        mock_email_instance = MagicMock()
        mock_email_service.return_value = mock_email_instance
        mock_email_instance.send_claim_released_notification.return_value = True
        
        # Create multiple expired issues
        issues = []
        for i in range(3):
            issue = Issue(
                github_issue_id=10000 + i,
                repository_id=sample_repository.id,
                title=f"Test Issue {i}",
                description="Test description",
                labels=["test"],
                programming_language="Python",
                status=IssueStatus.CLAIMED,
                claimed_by=test_user.id,
                claimed_at=datetime.utcnow() - timedelta(days=8),
                claim_expires_at=datetime.utcnow() - timedelta(hours=1),
                github_url=f"https://github.com/test/repo/issues/{i}"
            )
            db_session.add(issue)
            issues.append(issue)
        
        db_session.commit()
        
        # Run the task
        result = auto_release_expired_claims_task()
        
        assert result["released_count"] == 3
        assert len(result["issue_ids"]) == 3
        assert result["emails_sent"] == 3
        
        # Verify all issues were released
        for issue in issues:
            db_session.refresh(issue)
            assert issue.status == IssueStatus.AVAILABLE


class TestSendExpirationRemindersTask:
    """Tests for send_expiration_reminders_task"""
    
    @patch('app.tasks.claim_tasks.SessionLocal')
    @patch('app.tasks.claim_tasks.EmailService')
    def test_expiration_reminders_task(self, mock_email_service, mock_session_local, db_session, sample_issue, test_user):
        """Test expiration reminders task finds expiring claims and sends emails"""
        mock_session_local.return_value = db_session
        
        # Mock email service
        mock_email_instance = MagicMock()
        mock_email_service.return_value = mock_email_instance
        mock_email_instance.send_claim_expiration_reminder.return_value = True
        
        # Claim the issue and set to expire soon
        sample_issue.status = IssueStatus.CLAIMED
        sample_issue.claimed_by = test_user.id
        sample_issue.claimed_at = datetime.utcnow()
        sample_issue.claim_expires_at = datetime.utcnow() + timedelta(hours=12)
        db_session.commit()
        
        # Run the task
        result = send_expiration_reminders_task()
        
        assert result["expiring_count"] == 1
        assert sample_issue.id in result["issue_ids"]
        assert result["emails_sent"] == 1
        assert len(result["errors"]) == 0
    
    @patch('app.tasks.claim_tasks.SessionLocal')
    def test_expiration_reminders_task_no_expiring(self, mock_session_local, db_session):
        """Test expiration reminders task with no expiring claims"""
        mock_session_local.return_value = db_session
        
        result = send_expiration_reminders_task()
        
        assert result["expiring_count"] == 0
        assert len(result["issue_ids"]) == 0
    
    @patch('app.tasks.claim_tasks.SessionLocal')
    @patch('app.tasks.claim_tasks.EmailService')
    def test_expiration_reminders_task_multiple(
        self, mock_email_service, mock_session_local, db_session, sample_repository, test_user
    ):
        """Test expiration reminders task with multiple expiring claims"""
        mock_session_local.return_value = db_session
        
        # Mock email service
        mock_email_instance = MagicMock()
        mock_email_service.return_value = mock_email_instance
        mock_email_instance.send_claim_expiration_reminder.return_value = True
        
        # Create multiple expiring issues
        issues = []
        for i in range(2):
            issue = Issue(
                github_issue_id=20000 + i,
                repository_id=sample_repository.id,
                title=f"Expiring Issue {i}",
                description="Test description",
                labels=["test"],
                programming_language="Python",
                status=IssueStatus.CLAIMED,
                claimed_by=test_user.id,
                claimed_at=datetime.utcnow(),
                claim_expires_at=datetime.utcnow() + timedelta(hours=12),
                github_url=f"https://github.com/test/repo/issues/{i}"
            )
            db_session.add(issue)
            issues.append(issue)
        
        db_session.commit()
        
        # Run the task
        result = send_expiration_reminders_task()
        
        assert result["expiring_count"] == 2
        assert len(result["issue_ids"]) == 2
        assert result["emails_sent"] == 2


class TestReleaseSpecificClaimTask:
    """Tests for release_specific_claim_task"""
    
    @patch('app.tasks.claim_tasks.SessionLocal')
    def test_release_specific_claim_task_success(
        self, mock_session_local, db_session, sample_issue, test_user
    ):
        """Test successfully releasing a specific claim via task"""
        mock_session_local.return_value = db_session
        
        # Claim the issue
        sample_issue.status = IssueStatus.CLAIMED
        sample_issue.claimed_by = test_user.id
        sample_issue.claimed_at = datetime.utcnow()
        sample_issue.claim_expires_at = datetime.utcnow() + timedelta(days=7)
        db_session.commit()
        
        # Run the task
        result = release_specific_claim_task(sample_issue.id, test_user.id)
        
        assert result["success"] is True
        assert result["issue_id"] == sample_issue.id
        
        # Verify issue was released
        db_session.refresh(sample_issue)
        assert sample_issue.status == IssueStatus.AVAILABLE
    
    @patch('app.tasks.claim_tasks.SessionLocal')
    def test_release_specific_claim_task_force(
        self, mock_session_local, db_session, sample_issue, test_user, second_user
    ):
        """Test force releasing a claim via task"""
        mock_session_local.return_value = db_session
        
        # First user claims the issue
        sample_issue.status = IssueStatus.CLAIMED
        sample_issue.claimed_by = test_user.id
        sample_issue.claimed_at = datetime.utcnow()
        sample_issue.claim_expires_at = datetime.utcnow() + timedelta(days=7)
        db_session.commit()
        
        # Admin (second user) force releases it
        result = release_specific_claim_task(sample_issue.id, second_user.id, force=True)
        
        assert result["success"] is True
        
        # Verify issue was released
        db_session.refresh(sample_issue)
        assert sample_issue.status == IssueStatus.AVAILABLE
    
    @patch('app.tasks.claim_tasks.SessionLocal')
    def test_release_specific_claim_task_not_claimed(
        self, mock_session_local, db_session, sample_issue, test_user
    ):
        """Test releasing unclaimed issue via task"""
        mock_session_local.return_value = db_session
        
        # Issue is not claimed
        assert sample_issue.status == IssueStatus.AVAILABLE
        
        # Try to release
        result = release_specific_claim_task(sample_issue.id, test_user.id)
        
        assert result["success"] is False
        assert "not claimed" in result["message"].lower()
    
    @patch('app.tasks.claim_tasks.SessionLocal')
    def test_release_specific_claim_task_wrong_user(
        self, mock_session_local, db_session, sample_issue, test_user, second_user
    ):
        """Test releasing claim by wrong user via task"""
        mock_session_local.return_value = db_session
        
        # First user claims the issue
        sample_issue.status = IssueStatus.CLAIMED
        sample_issue.claimed_by = test_user.id
        sample_issue.claimed_at = datetime.utcnow()
        sample_issue.claim_expires_at = datetime.utcnow() + timedelta(days=7)
        db_session.commit()
        
        # Second user tries to release without force
        result = release_specific_claim_task(sample_issue.id, second_user.id, force=False)
        
        assert result["success"] is False
        assert "only release" in result["message"].lower()
