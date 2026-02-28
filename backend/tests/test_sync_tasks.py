"""
Tests for GitHub issue synchronization tasks
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, AsyncMock
from app.tasks.sync_tasks import (
    sync_all_repositories_task,
    sync_specific_repositories_task,
    check_closed_issues_task
)
from app.models.issue import Issue, IssueStatus
from app.models.repository import Repository


class TestSyncAllRepositoriesTask:
    """Tests for sync_all_repositories_task"""
    
    @patch('app.tasks.sync_tasks.SessionLocal')
    @patch('asyncio.run')
    def test_sync_all_repositories_success(self, mock_asyncio_run, mock_session_local, db_session, sample_repository):
        """Test successful synchronization of all repositories"""
        mock_session_local.return_value = db_session
        
        # Mock sync result
        from app.schemas.issue import SyncResult
        mock_result = SyncResult(
            repositories_synced=1,
            issues_added=5,
            issues_updated=2,
            issues_closed=1,
            errors=[],
            sync_duration_seconds=10.5
        )
        mock_asyncio_run.return_value = mock_result
        
        # Run the task
        result = sync_all_repositories_task()
        
        assert result["success"] is True
        assert result["repositories_synced"] == 1
        assert result["issues_added"] == 5
        assert result["issues_updated"] == 2
        assert result["issues_closed"] == 1
        assert len(result["errors"]) == 0
    
    @patch('app.tasks.sync_tasks.SessionLocal')
    @patch('asyncio.run')
    def test_sync_all_repositories_with_errors(self, mock_asyncio_run, mock_session_local, db_session):
        """Test synchronization with some errors"""
        mock_session_local.return_value = db_session
        
        from app.schemas.issue import SyncResult
        mock_result = SyncResult(
            repositories_synced=2,
            issues_added=3,
            issues_updated=1,
            issues_closed=0,
            errors=["Failed to sync repo1: API rate limit"],
            sync_duration_seconds=15.0
        )
        mock_asyncio_run.return_value = mock_result
        
        result = sync_all_repositories_task()
        
        assert result["success"] is True
        assert len(result["errors"]) == 1
        assert "rate limit" in result["errors"][0]


class TestSyncSpecificRepositoriesTask:
    """Tests for sync_specific_repositories_task"""
    
    @patch('app.tasks.sync_tasks.SessionLocal')
    @patch('asyncio.run')
    def test_sync_specific_repositories_success(self, mock_asyncio_run, mock_session_local, db_session, sample_repository):
        """Test successful synchronization of specific repositories"""
        mock_session_local.return_value = db_session
        
        from app.schemas.issue import SyncResult
        mock_result = SyncResult(
            repositories_synced=1,
            issues_added=3,
            issues_updated=1,
            issues_closed=0,
            errors=[],
            sync_duration_seconds=5.0
        )
        mock_asyncio_run.return_value = mock_result
        
        # Run the task with specific repository IDs
        result = sync_specific_repositories_task([sample_repository.id])
        
        assert result["success"] is True
        assert result["repository_ids"] == [sample_repository.id]
        assert result["repositories_synced"] == 1
        assert result["issues_added"] == 3
    
    @patch('app.tasks.sync_tasks.SessionLocal')
    @patch('asyncio.run')
    def test_sync_specific_repositories_multiple(self, mock_asyncio_run, mock_session_local, db_session):
        """Test synchronization of multiple specific repositories"""
        mock_session_local.return_value = db_session
        
        from app.schemas.issue import SyncResult
        mock_result = SyncResult(
            repositories_synced=3,
            issues_added=10,
            issues_updated=5,
            issues_closed=2,
            errors=[],
            sync_duration_seconds=20.0
        )
        mock_asyncio_run.return_value = mock_result
        
        repo_ids = [1, 2, 3]
        result = sync_specific_repositories_task(repo_ids)
        
        assert result["success"] is True
        assert result["repository_ids"] == repo_ids
        assert result["repositories_synced"] == 3


class TestCheckClosedIssuesTask:
    """Tests for check_closed_issues_task"""
    
    @patch('app.tasks.sync_tasks.SessionLocal')
    @patch('asyncio.run')
    def test_check_closed_issues_finds_closed(self, mock_asyncio_run, mock_session_local, db_session, sample_issue):
        """Test checking issues finds closed ones"""
        mock_session_local.return_value = db_session
        
        # Ensure issue is available
        sample_issue.status = IssueStatus.AVAILABLE
        db_session.commit()
        
        # Mock the async check_issues function
        async def mock_check_issues():
            # Simulate finding the issue is closed
            sample_issue.status = IssueStatus.CLOSED
        
        mock_asyncio_run.side_effect = mock_check_issues
        
        # Run the task
        result = check_closed_issues_task()
        
        # Note: The actual implementation will check GitHub, 
        # but we're testing the task structure
        assert "success" in result
    
    @patch('app.tasks.sync_tasks.SessionLocal')
    def test_check_closed_issues_no_open_issues(self, mock_session_local, db_session):
        """Test checking when there are no open issues"""
        mock_session_local.return_value = db_session
        
        # No issues in database
        result = check_closed_issues_task()
        
        assert result["success"] is True
        assert result["issues_checked"] == 0
        assert result["issues_closed"] == 0
    
    @patch('app.tasks.sync_tasks.SessionLocal')
    @patch('asyncio.run')
    def test_check_closed_issues_with_errors(self, mock_asyncio_run, mock_session_local, db_session, sample_issue):
        """Test checking issues handles errors gracefully"""
        mock_session_local.return_value = db_session
        
        sample_issue.status = IssueStatus.AVAILABLE
        db_session.commit()
        
        # Mock error during check
        async def mock_check_with_error():
            raise Exception("GitHub API error")
        
        mock_asyncio_run.side_effect = mock_check_with_error
        
        result = check_closed_issues_task()
        
        assert result["success"] is False
        assert "error" in result


class TestSyncTasksIntegration:
    """Integration tests for sync tasks"""
    
    @patch('app.tasks.sync_tasks.SessionLocal')
    @patch('asyncio.run')
    def test_full_sync_workflow(self, mock_asyncio_run, mock_session_local, db_session, sample_repository):
        """Test complete sync workflow"""
        mock_session_local.return_value = db_session
        
        # Create some existing issues
        for i in range(3):
            issue = Issue(
                github_issue_id=1000 + i,
                repository_id=sample_repository.id,
                title=f"Issue {i}",
                description="Test",
                labels=["test"],
                programming_language="Python",
                status=IssueStatus.AVAILABLE,
                github_url=f"https://github.com/test/repo/issues/{i}"
            )
            db_session.add(issue)
        db_session.commit()
        
        # Mock sync result that adds, updates, and closes issues
        from app.schemas.issue import SyncResult
        mock_result = SyncResult(
            repositories_synced=1,
            issues_added=2,
            issues_updated=1,
            issues_closed=1,
            errors=[],
            sync_duration_seconds=8.0
        )
        mock_asyncio_run.return_value = mock_result
        
        # Run sync
        result = sync_all_repositories_task()
        
        assert result["success"] is True
        assert result["issues_added"] == 2
        assert result["issues_updated"] == 1
        assert result["issues_closed"] == 1
