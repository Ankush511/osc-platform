"""
Tests for Pull Request status tracking tasks
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, AsyncMock
from app.tasks.pr_tasks import (
    update_pr_status_task,
    check_all_open_prs_task,
    handle_webhook_event_task
)
from app.models.contribution import Contribution, ContributionStatus
from app.models.issue import Issue, IssueStatus


@pytest.fixture
def sample_contribution(db_session, sample_issue, test_user):
    """Create a sample contribution for testing"""
    contribution = Contribution(
        user_id=test_user.id,
        issue_id=sample_issue.id,
        pr_url="https://github.com/test-org/test-repo/pull/123",
        pr_number=123,
        status=ContributionStatus.SUBMITTED
    )
    db_session.add(contribution)
    db_session.commit()
    db_session.refresh(contribution)
    return contribution


class TestUpdatePRStatusTask:
    """Tests for update_pr_status_task"""
    
    @patch('app.tasks.pr_tasks.SessionLocal')
    @patch('asyncio.run')
    def test_update_pr_status_merged(self, mock_asyncio_run, mock_session_local, db_session, sample_contribution):
        """Test updating PR status when PR is merged"""
        mock_session_local.return_value = db_session
        
        # Mock PR info indicating merged
        from app.schemas.github import PRValidation
        mock_pr_info = PRValidation(
            valid=True,
            pr_number=123,
            state="closed",
            merged=True,
            merged_at=datetime.utcnow(),
            created_by="testuser",
            linked_issue_number=1
        )
        
        async def mock_check():
            return {
                "success": True,
                "contribution_id": sample_contribution.id,
                "old_status": ContributionStatus.SUBMITTED.value,
                "new_status": ContributionStatus.MERGED.value,
                "pr_state": "closed",
                "merged": True
            }
        
        mock_asyncio_run.side_effect = mock_check
        
        # Run the task
        result = update_pr_status_task(sample_contribution.id)
        
        assert result["success"] is True
        assert result["new_status"] == ContributionStatus.MERGED.value
        assert result["merged"] is True
    
    @patch('app.tasks.pr_tasks.SessionLocal')
    @patch('asyncio.run')
    def test_update_pr_status_closed(self, mock_asyncio_run, mock_session_local, db_session, sample_contribution):
        """Test updating PR status when PR is closed without merge"""
        mock_session_local.return_value = db_session
        
        async def mock_check():
            return {
                "success": True,
                "contribution_id": sample_contribution.id,
                "old_status": ContributionStatus.SUBMITTED.value,
                "new_status": ContributionStatus.CLOSED.value,
                "pr_state": "closed",
                "merged": False
            }
        
        mock_asyncio_run.side_effect = mock_check
        
        result = update_pr_status_task(sample_contribution.id)
        
        assert result["success"] is True
        assert result["new_status"] == ContributionStatus.CLOSED.value
    
    @patch('app.tasks.pr_tasks.SessionLocal')
    def test_update_pr_status_not_found(self, mock_session_local, db_session):
        """Test updating PR status for non-existent contribution"""
        mock_session_local.return_value = db_session
        
        result = update_pr_status_task(99999)
        
        assert result["success"] is False
        assert "not found" in result["error"].lower()


class TestCheckAllOpenPRsTask:
    """Tests for check_all_open_prs_task"""
    
    @patch('app.tasks.pr_tasks.SessionLocal')
    @patch('app.tasks.pr_tasks.update_pr_status_task')
    def test_check_all_open_prs_success(self, mock_update_task, mock_session_local, db_session, sample_contribution):
        """Test checking all open PRs"""
        mock_session_local.return_value = db_session
        
        # Mock successful update
        mock_update_task.return_value = {
            "success": True,
            "new_status": ContributionStatus.MERGED.value
        }
        
        result = check_all_open_prs_task()
        
        assert result["success"] is True
        assert result["total_checked"] == 1
        assert result["updated_count"] == 1
    
    @patch('app.tasks.pr_tasks.SessionLocal')
    @patch('app.tasks.pr_tasks.update_pr_status_task')
    def test_check_all_open_prs_multiple(self, mock_update_task, mock_session_local, db_session, sample_issue, test_user):
        """Test checking multiple open PRs"""
        mock_session_local.return_value = db_session
        
        # Create multiple contributions
        for i in range(3):
            contribution = Contribution(
                user_id=test_user.id,
                issue_id=sample_issue.id,
                pr_url=f"https://github.com/test/repo/pull/{100 + i}",
                pr_number=100 + i,
                status=ContributionStatus.SUBMITTED
            )
            db_session.add(contribution)
        db_session.commit()
        
        # Mock updates with different results
        mock_update_task.side_effect = [
            {"success": True, "new_status": ContributionStatus.MERGED.value},
            {"success": True, "new_status": ContributionStatus.SUBMITTED.value},
            {"success": True, "new_status": ContributionStatus.CLOSED.value}
        ]
        
        result = check_all_open_prs_task()
        
        assert result["success"] is True
        assert result["total_checked"] == 3
        assert result["merged_count"] == 1
        assert result["closed_count"] == 1
    
    @patch('app.tasks.pr_tasks.SessionLocal')
    def test_check_all_open_prs_no_open(self, mock_session_local, db_session):
        """Test checking when there are no open PRs"""
        mock_session_local.return_value = db_session
        
        result = check_all_open_prs_task()
        
        assert result["success"] is True
        assert result["total_checked"] == 0


class TestHandleWebhookEventTask:
    """Tests for handle_webhook_event_task"""
    
    @patch('app.tasks.pr_tasks.SessionLocal')
    @patch('app.tasks.pr_tasks.update_pr_status_task')
    def test_handle_pr_webhook_opened(self, mock_update_task, mock_session_local, db_session, sample_contribution):
        """Test handling PR opened webhook"""
        mock_session_local.return_value = db_session
        
        mock_update_task.return_value = {
            "success": True,
            "new_status": ContributionStatus.SUBMITTED.value
        }
        
        payload = {
            "action": "opened",
            "pull_request": {
                "html_url": sample_contribution.pr_url,
                "number": 123
            }
        }
        
        result = handle_webhook_event_task("pull_request", payload)
        
        assert result["success"] is True
        assert result["action"] == "opened"
        assert result["pr_number"] == 123
    
    @patch('app.tasks.pr_tasks.SessionLocal')
    @patch('app.tasks.pr_tasks.update_pr_status_task')
    def test_handle_pr_webhook_closed(self, mock_update_task, mock_session_local, db_session, sample_contribution):
        """Test handling PR closed webhook"""
        mock_session_local.return_value = db_session
        
        mock_update_task.return_value = {
            "success": True,
            "new_status": ContributionStatus.CLOSED.value
        }
        
        payload = {
            "action": "closed",
            "pull_request": {
                "html_url": sample_contribution.pr_url,
                "number": 123
            }
        }
        
        result = handle_webhook_event_task("pull_request", payload)
        
        assert result["success"] is True
        assert result["action"] == "closed"
    
    @patch('app.tasks.pr_tasks.SessionLocal')
    def test_handle_pr_webhook_not_found(self, mock_session_local, db_session):
        """Test handling webhook for unknown PR"""
        mock_session_local.return_value = db_session
        
        payload = {
            "action": "opened",
            "pull_request": {
                "html_url": "https://github.com/unknown/repo/pull/999",
                "number": 999
            }
        }
        
        result = handle_webhook_event_task("pull_request", payload)
        
        assert result["success"] is False
        assert "not found" in result["error"].lower()
    
    @patch('app.tasks.pr_tasks.SessionLocal')
    def test_handle_issue_webhook_closed(self, mock_session_local, db_session, sample_issue):
        """Test handling issue closed webhook"""
        mock_session_local.return_value = db_session
        
        sample_issue.status = IssueStatus.AVAILABLE
        db_session.commit()
        
        payload = {
            "action": "closed",
            "issue": {
                "html_url": sample_issue.github_url
            }
        }
        
        result = handle_webhook_event_task("issues", payload)
        
        assert result["success"] is True
        assert result["action"] == "closed"
        
        # Verify issue was marked as closed
        db_session.refresh(sample_issue)
        assert sample_issue.status == IssueStatus.CLOSED
    
    @patch('app.tasks.pr_tasks.SessionLocal')
    def test_handle_issue_webhook_reopened(self, mock_session_local, db_session, sample_issue):
        """Test handling issue reopened webhook"""
        mock_session_local.return_value = db_session
        
        sample_issue.status = IssueStatus.CLOSED
        db_session.commit()
        
        payload = {
            "action": "reopened",
            "issue": {
                "html_url": sample_issue.github_url
            }
        }
        
        result = handle_webhook_event_task("issues", payload)
        
        assert result["success"] is True
        assert result["action"] == "reopened"
        
        # Verify issue was marked as available
        db_session.refresh(sample_issue)
        assert sample_issue.status == IssueStatus.AVAILABLE
    
    @patch('app.tasks.pr_tasks.SessionLocal')
    def test_handle_unknown_webhook_event(self, mock_session_local, db_session):
        """Test handling unknown webhook event type"""
        mock_session_local.return_value = db_session
        
        result = handle_webhook_event_task("unknown_event", {})
        
        assert result["success"] is True
        assert "not handled" in result["message"].lower()


class TestPRTasksIntegration:
    """Integration tests for PR tasks"""
    
    @patch('app.tasks.pr_tasks.SessionLocal')
    @patch('asyncio.run')
    def test_pr_lifecycle_workflow(self, mock_asyncio_run, mock_session_local, db_session, sample_contribution, sample_issue):
        """Test complete PR lifecycle from submission to merge"""
        mock_session_local.return_value = db_session
        
        # Initial status: submitted
        assert sample_contribution.status == ContributionStatus.SUBMITTED
        
        # Simulate PR being merged
        async def mock_merged():
            sample_contribution.status = ContributionStatus.MERGED
            sample_contribution.merged_at = datetime.utcnow()
            sample_issue.status = IssueStatus.COMPLETED
            db_session.commit()
            
            return {
                "success": True,
                "contribution_id": sample_contribution.id,
                "old_status": ContributionStatus.SUBMITTED.value,
                "new_status": ContributionStatus.MERGED.value,
                "pr_state": "closed",
                "merged": True
            }
        
        mock_asyncio_run.side_effect = mock_merged
        
        # Update PR status
        result = update_pr_status_task(sample_contribution.id)
        
        assert result["success"] is True
        assert result["new_status"] == ContributionStatus.MERGED.value
        
        # Verify contribution and issue status
        db_session.refresh(sample_contribution)
        db_session.refresh(sample_issue)
        
        assert sample_contribution.status == ContributionStatus.MERGED
        assert sample_contribution.merged_at is not None
        assert sample_issue.status == IssueStatus.COMPLETED
