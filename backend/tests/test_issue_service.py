"""
Tests for issue service functionality
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch
from sqlalchemy.orm import Session

from app.services.issue_service import IssueService
from app.models.issue import Issue, IssueStatus
from app.models.repository import Repository
from app.schemas.issue import IssueFilters, PaginationParams
from app.schemas.github import GitHubIssue, GitHubLabel


@pytest.fixture
def mock_db():
    """Mock database session"""
    return Mock(spec=Session)


@pytest.fixture
def mock_redis():
    """Mock Redis client"""
    redis_mock = Mock()
    redis_mock.get.return_value = None
    redis_mock.setex.return_value = True
    redis_mock.keys.return_value = []
    redis_mock.delete.return_value = True
    return redis_mock


@pytest.fixture
def issue_service(mock_db, mock_redis):
    """Create issue service instance"""
    return IssueService(db=mock_db, redis_client=mock_redis)


@pytest.fixture
def sample_repository():
    """Sample repository for testing"""
    return Repository(
        id=1,
        github_repo_id=12345,
        full_name="test/repo",
        name="repo",
        description="Test repository",
        primary_language="Python",
        topics=["testing", "python"],
        stars=100,
        forks=20,
        is_active=True,
        last_synced=None
    )


@pytest.fixture
def sample_issue():
    """Sample issue for testing"""
    return Issue(
        id=1,
        github_issue_id=67890,
        repository_id=1,
        title="Test Issue",
        description="This is a test issue",
        labels=["good first issue", "help wanted"],
        programming_language="Python",
        difficulty_level="easy",
        status=IssueStatus.AVAILABLE,
        github_url="https://github.com/test/repo/issues/1",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


class TestIssueServiceFiltering:
    """Test issue filtering functionality"""
    
    def test_get_filtered_issues_no_filters(self, issue_service, mock_db, sample_issue):
        """Test getting issues without filters"""
        # Setup mock query chain
        mock_query = Mock()
        mock_query.options.return_value = mock_query
        mock_query.count.return_value = 1
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [sample_issue]
        
        mock_db.query.return_value = mock_query
        
        # Execute
        issues, total = issue_service.get_filtered_issues()
        
        # Verify
        assert len(issues) == 1
        assert total == 1
        assert issues[0].title == "Test Issue"
    
    def test_get_filtered_issues_by_language(self, issue_service, mock_db, sample_issue):
        """Test filtering by programming language"""
        filters = IssueFilters(programming_languages=["Python"])
        
        # Setup mock query chain
        mock_query = Mock()
        mock_query.options.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 1
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [sample_issue]
        
        mock_db.query.return_value = mock_query
        
        # Execute
        issues, total = issue_service.get_filtered_issues(filters=filters)
        
        # Verify
        assert len(issues) == 1
        assert total == 1
        mock_query.filter.assert_called()
    
    def test_get_filtered_issues_by_labels(self, issue_service, mock_db, sample_issue):
        """Test filtering by labels"""
        filters = IssueFilters(labels=["good first issue"])
        
        # Setup mock query chain
        mock_query = Mock()
        mock_query.options.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 1
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [sample_issue]
        
        mock_db.query.return_value = mock_query
        
        # Execute
        issues, total = issue_service.get_filtered_issues(filters=filters)
        
        # Verify
        assert len(issues) == 1
        assert total == 1
    
    def test_get_filtered_issues_by_difficulty(self, issue_service, mock_db, sample_issue):
        """Test filtering by difficulty level"""
        filters = IssueFilters(difficulty_levels=["easy"])
        
        # Setup mock query chain
        mock_query = Mock()
        mock_query.options.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 1
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [sample_issue]
        
        mock_db.query.return_value = mock_query
        
        # Execute
        issues, total = issue_service.get_filtered_issues(filters=filters)
        
        # Verify
        assert len(issues) == 1
        assert total == 1
    
    def test_get_filtered_issues_with_search(self, issue_service, mock_db, sample_issue):
        """Test text search in title and description"""
        filters = IssueFilters(search_query="test")
        
        # Setup mock query chain
        mock_query = Mock()
        mock_query.options.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 1
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [sample_issue]
        
        mock_db.query.return_value = mock_query
        
        # Execute
        issues, total = issue_service.get_filtered_issues(filters=filters)
        
        # Verify
        assert len(issues) == 1
        assert total == 1
    
    def test_get_filtered_issues_with_pagination(self, issue_service, mock_db, sample_issue):
        """Test pagination"""
        pagination = PaginationParams(page=2, page_size=10)
        
        # Setup mock query chain
        mock_query = Mock()
        mock_query.options.return_value = mock_query
        mock_query.count.return_value = 25
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [sample_issue]
        
        mock_db.query.return_value = mock_query
        
        # Execute
        issues, total = issue_service.get_filtered_issues(pagination=pagination)
        
        # Verify
        assert total == 25
        mock_query.offset.assert_called_with(10)  # (page 2 - 1) * 10
        mock_query.limit.assert_called_with(10)


class TestIssueServiceSearch:
    """Test issue search functionality"""
    
    def test_search_issues(self, issue_service, mock_db, sample_issue):
        """Test searching issues by query"""
        # Setup mock query chain
        mock_query = Mock()
        mock_query.options.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 1
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [sample_issue]
        
        mock_db.query.return_value = mock_query
        
        # Execute
        issues, total = issue_service.search_issues("test")
        
        # Verify
        assert len(issues) == 1
        assert total == 1
        assert issues[0].title == "Test Issue"
    
    def test_search_issues_with_filters(self, issue_service, mock_db, sample_issue):
        """Test searching with additional filters"""
        filters = IssueFilters(programming_languages=["Python"])
        
        # Setup mock query chain
        mock_query = Mock()
        mock_query.options.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 1
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [sample_issue]
        
        mock_db.query.return_value = mock_query
        
        # Execute
        issues, total = issue_service.search_issues("test", filters=filters)
        
        # Verify
        assert len(issues) == 1
        assert total == 1


class TestIssueServiceCaching:
    """Test caching functionality"""
    
    def test_cache_hit(self, issue_service, mock_db, mock_redis):
        """Test cache hit scenario"""
        # Setup cache hit
        import json
        cache_data = {"issue_ids": [1], "total": 1}
        mock_redis.get.return_value = json.dumps(cache_data, default=str)
        
        # Setup mock query for fetching by IDs
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [Mock(id=1, title="Cached Issue")]
        mock_db.query.return_value = mock_query
        
        # Execute
        issues, total = issue_service.get_filtered_issues()
        
        # Verify cache was checked
        assert mock_redis.get.called
        assert total == 1
    
    def test_cache_miss(self, issue_service, mock_db, mock_redis, sample_issue):
        """Test cache miss scenario"""
        # Setup cache miss
        mock_redis.get.return_value = None
        
        # Setup mock query chain
        mock_query = Mock()
        mock_query.options.return_value = mock_query
        mock_query.count.return_value = 1
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [sample_issue]
        
        mock_db.query.return_value = mock_query
        
        # Execute
        issues, total = issue_service.get_filtered_issues()
        
        # Verify cache was set
        assert mock_redis.setex.called
        assert len(issues) == 1


class TestIssueServiceSync:
    """Test issue synchronization"""
    
    @pytest.mark.asyncio
    async def test_sync_issues_success(self, issue_service, mock_db, sample_repository):
        """Test successful issue synchronization"""
        # Setup mock repository query
        mock_repo_query = Mock()
        mock_repo_query.filter.return_value = mock_repo_query
        mock_repo_query.all.return_value = [sample_repository]
        
        # Setup mock issue query for existing issues
        mock_issue_query = Mock()
        mock_issue_query.filter.return_value = mock_issue_query
        mock_issue_query.all.return_value = []
        
        # Mock db.query to return different queries based on model type
        def query_side_effect(model):
            if model == Repository:
                return mock_repo_query
            elif model == Issue:
                return mock_issue_query
            return Mock()
        
        mock_db.query.side_effect = query_side_effect
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        
        # Mock GitHub service
        mock_github_label = GitHubLabel(name="good first issue", color="7057ff")
        mock_github_issue = GitHubIssue(
            id=67890,
            number=1,
            title="Test Issue",
            body="Test description",
            state="open",
            html_url="https://github.com/test/repo/issues/1",
            labels=[mock_github_label],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            user={"login": "testuser"}
        )
        
        with patch('app.services.issue_service.GitHubService') as MockGitHubService:
            mock_service = AsyncMock()
            mock_service.fetch_repository_issues.return_value = [mock_github_issue]
            mock_service.close.return_value = None
            MockGitHubService.return_value = mock_service
            
            # Execute
            result = await issue_service.sync_issues()
            
            # Verify
            assert result.repositories_synced == 1
            assert result.issues_added >= 0
            assert mock_db.commit.called
    
    @pytest.mark.asyncio
    async def test_sync_issues_no_repositories(self, issue_service, mock_db):
        """Test sync with no active repositories"""
        # Setup empty repository query
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = []
        mock_db.query.return_value = mock_query
        
        # Execute
        result = await issue_service.sync_issues()
        
        # Verify
        assert result.repositories_synced == 0
        assert result.issues_added == 0


class TestIssueServiceHelpers:
    """Test helper methods"""
    
    def test_infer_difficulty_easy(self, issue_service):
        """Test difficulty inference for easy issues"""
        labels = [
            GitHubLabel(name="good first issue", color="7057ff"),
            GitHubLabel(name="help wanted", color="008672")
        ]
        
        difficulty = issue_service._infer_difficulty(labels)
        assert difficulty == "easy"
    
    def test_infer_difficulty_medium(self, issue_service):
        """Test difficulty inference for medium issues"""
        labels = [
            GitHubLabel(name="medium", color="fbca04"),
            GitHubLabel(name="enhancement", color="a2eeef")
        ]
        
        difficulty = issue_service._infer_difficulty(labels)
        assert difficulty == "medium"
    
    def test_infer_difficulty_hard(self, issue_service):
        """Test difficulty inference for hard issues"""
        labels = [
            GitHubLabel(name="hard", color="d93f0b"),
            GitHubLabel(name="advanced", color="0052cc")
        ]
        
        difficulty = issue_service._infer_difficulty(labels)
        assert difficulty == "hard"
    
    def test_infer_difficulty_default(self, issue_service):
        """Test difficulty inference with no matching labels"""
        labels = [
            GitHubLabel(name="bug", color="d73a4a"),
            GitHubLabel(name="documentation", color="0075ca")
        ]
        
        difficulty = issue_service._infer_difficulty(labels)
        assert difficulty == "easy"  # Default for beginner-friendly issues
    
    def test_get_issue_by_id(self, issue_service, mock_db, sample_issue):
        """Test getting issue by ID"""
        # Setup mock query
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_issue
        mock_db.query.return_value = mock_query
        
        # Execute
        issue = issue_service.get_issue_by_id(1)
        
        # Verify
        assert issue is not None
        assert issue.id == 1
        assert issue.title == "Test Issue"
    
    def test_get_issue_by_id_not_found(self, issue_service, mock_db):
        """Test getting non-existent issue"""
        # Setup mock query
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_db.query.return_value = mock_query
        
        # Execute
        issue = issue_service.get_issue_by_id(999)
        
        # Verify
        assert issue is None
    
    def test_get_available_filters(self, issue_service, mock_db):
        """Test getting available filter options"""
        # Setup mock queries
        mock_lang_query = Mock()
        mock_lang_query.filter.return_value = mock_lang_query
        mock_lang_query.distinct.return_value = mock_lang_query
        mock_lang_query.all.return_value = [("Python",), ("JavaScript",)]
        
        mock_diff_query = Mock()
        mock_diff_query.filter.return_value = mock_diff_query
        mock_diff_query.distinct.return_value = mock_diff_query
        mock_diff_query.all.return_value = [("easy",), ("medium",)]
        
        mock_label_query = Mock()
        mock_label_query.filter.return_value = mock_label_query
        mock_label_query.all.return_value = [
            (["good first issue", "help wanted"],),
            (["bug", "documentation"],)
        ]
        
        # Mock query to return different results based on what's being queried
        def query_side_effect(model):
            mock_q = Mock()
            if hasattr(model, 'programming_language'):
                return mock_lang_query
            elif hasattr(model, 'difficulty_level'):
                return mock_diff_query
            else:
                return mock_label_query
        
        mock_db.query.side_effect = [mock_lang_query, mock_diff_query, mock_label_query]
        
        # Execute
        filters = issue_service.get_available_filters()
        
        # Verify
        assert "languages" in filters
        assert "difficulties" in filters
        assert "labels" in filters
        assert len(filters["languages"]) == 2
        assert len(filters["difficulties"]) == 2
