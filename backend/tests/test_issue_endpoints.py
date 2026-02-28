"""
Tests for issue API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from app.main import app
from app.models.issue import Issue, IssueStatus
from app.models.repository import Repository
from app.api.v1.issues import get_issue_service


# Mock issue service for all tests
@pytest.fixture
def mock_issue_service():
    """Mock issue service"""
    return Mock()


@pytest.fixture
def client(mock_issue_service):
    """Test client with mocked issue service"""
    # Override the get_issue_service dependency
    app.dependency_overrides[get_issue_service] = lambda: mock_issue_service
    
    client = TestClient(app)
    yield client
    
    # Clean up overrides
    app.dependency_overrides.clear()


@pytest.fixture
def sample_issue():
    """Sample issue for testing"""
    issue = Mock(spec=Issue)
    issue.id = 1
    issue.github_issue_id = 67890
    issue.repository_id = 1
    issue.title = "Test Issue"
    issue.description = "This is a test issue"
    issue.labels = ["good first issue", "help wanted"]
    issue.programming_language = "Python"
    issue.difficulty_level = "easy"
    issue.ai_explanation = None
    issue.status = IssueStatus.AVAILABLE
    issue.claimed_by = None
    issue.claimed_at = None
    issue.claim_expires_at = None
    issue.github_url = "https://github.com/test/repo/issues/1"
    issue.created_at = datetime.utcnow()
    issue.updated_at = datetime.utcnow()
    
    # Mock repository relationship
    repo = Mock(spec=Repository)
    repo.name = "repo"
    repo.full_name = "test/repo"
    issue.repository = repo
    
    return issue


class TestGetIssuesEndpoint:
    """Test GET /api/v1/issues/ endpoint"""
    
    def test_get_issues_success(self, mock_issue_service, client, sample_issue):
        """Test getting issues successfully"""
        # Setup mock service
        mock_issue_service.get_filtered_issues.return_value = ([sample_issue], 1)
        
        # Execute
        response = client.get("/api/v1/issues/")
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == "Test Issue"
    
    def test_get_issues_with_filters(self, mock_issue_service, client, sample_issue):
        """Test getting issues with filters"""
        # Setup mock service
        mock_issue_service.get_filtered_issues.return_value = ([sample_issue], 1)
        
        # Execute
        response = client.get(
            "/api/v1/issues/",
            params={
                "programming_languages": "Python",
                "labels": "good first issue",
                "difficulty_levels": "easy",
                "page": 1,
                "page_size": 20
            }
        )
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        mock_issue_service.get_filtered_issues.assert_called_once()
    
    def test_get_issues_with_search(self, mock_issue_service, client, sample_issue):
        """Test getting issues with search query"""
        # Setup mock service
        mock_issue_service.get_filtered_issues.return_value = ([sample_issue], 1)
        
        # Execute
        response = client.get(
            "/api/v1/issues/",
            params={"search_query": "test"}
        )
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
    
    def test_get_issues_pagination(self, mock_issue_service, client, sample_issue):
        """Test pagination"""
        # Setup mock service
        mock_issue_service.get_filtered_issues.return_value = ([sample_issue], 50)
        
        # Execute
        response = client.get(
            "/api/v1/issues/",
            params={"page": 2, "page_size": 10}
        )
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 2
        assert data["page_size"] == 10
        assert data["total"] == 50
        assert data["total_pages"] == 5
    
    def test_get_issues_empty_result(self, mock_issue_service, client):
        """Test getting issues with no results"""
        # Setup mock service
        mock_issue_service.get_filtered_issues.return_value = ([], 0)
        
        # Execute
        response = client.get("/api/v1/issues/")
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["items"]) == 0
        assert data["total_pages"] == 0


class TestSearchIssuesEndpoint:
    """Test POST /api/v1/issues/search endpoint"""
    
    def test_search_issues_success(self, mock_issue_service, client, sample_issue):
        """Test searching issues successfully"""
        # Setup mock service
        mock_issue_service.search_issues.return_value = ([sample_issue], 1)
        
        # Execute
        response = client.post(
            "/api/v1/issues/search",
            json={
                "query": "test",
                "pagination": {"page": 1, "page_size": 20}
            }
        )
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        mock_issue_service.search_issues.assert_called_once()
    
    def test_search_issues_with_filters(self, mock_issue_service, client, sample_issue):
        """Test searching with additional filters"""
        # Setup mock service
        mock_issue_service.search_issues.return_value = ([sample_issue], 1)
        
        # Execute
        response = client.post(
            "/api/v1/issues/search",
            json={
                "query": "test",
                "filters": {
                    "programming_languages": ["Python"],
                    "difficulty_levels": ["easy"]
                },
                "pagination": {"page": 1, "page_size": 20}
            }
        )
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1


class TestGetIssueByIdEndpoint:
    """Test GET /api/v1/issues/{issue_id} endpoint"""
    
    def test_get_issue_by_id_success(self, mock_issue_service, client, sample_issue):
        """Test getting issue by ID successfully"""
        # Setup mock service
        mock_issue_service.get_issue_by_id.return_value = sample_issue
        
        # Execute
        response = client.get("/api/v1/issues/1")
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["title"] == "Test Issue"
    
    def test_get_issue_by_id_not_found(self, mock_issue_service, client):
        """Test getting non-existent issue"""
        # Setup mock service
        mock_issue_service.get_issue_by_id.return_value = None
        
        # Execute
        response = client.get("/api/v1/issues/999")
        
        # Verify
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestGetAvailableFiltersEndpoint:
    """Test GET /api/v1/issues/filters/available endpoint"""
    
    def test_get_available_filters(self, mock_issue_service, client):
        """Test getting available filter options"""
        # Setup mock service
        mock_issue_service.get_available_filters.return_value = {
            "languages": ["Python", "JavaScript", "Go"],
            "difficulties": ["easy", "medium", "hard"],
            "labels": ["good first issue", "help wanted", "bug"]
        }
        
        # Execute
        response = client.get("/api/v1/issues/filters/available")
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert "languages" in data
        assert "difficulties" in data
        assert "labels" in data
        assert len(data["languages"]) == 3
        assert len(data["difficulties"]) == 3
        assert len(data["labels"]) == 3


class TestSyncIssuesEndpoint:
    """Test POST /api/v1/issues/sync endpoint"""
    
    @pytest.mark.asyncio
    async def test_sync_issues_success(self, mock_issue_service, client):
        """Test syncing issues successfully"""
        # Setup mock service
        from app.schemas.issue import SyncResult
        mock_issue_service.sync_issues = AsyncMock(return_value=SyncResult(
            repositories_synced=2,
            issues_added=5,
            issues_updated=3,
            issues_closed=1,
            errors=[],
            sync_duration_seconds=2.5
        ))
        
        # Execute
        response = client.post("/api/v1/issues/sync")
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["repositories_synced"] == 2
        assert data["issues_added"] == 5
        assert data["issues_updated"] == 3
        assert data["issues_closed"] == 1
    
    @pytest.mark.asyncio
    async def test_sync_issues_with_repository_ids(self, mock_issue_service, client):
        """Test syncing specific repositories"""
        # Setup mock service
        from app.schemas.issue import SyncResult
        mock_issue_service.sync_issues = AsyncMock(return_value=SyncResult(
            repositories_synced=1,
            issues_added=2,
            issues_updated=1,
            issues_closed=0,
            errors=[],
            sync_duration_seconds=1.2
        ))
        
        # Execute
        response = client.post(
            "/api/v1/issues/sync",
            json=[1, 2]
        )
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["repositories_synced"] == 1


class TestIssueEndpointsIntegration:
    """Integration tests for issue endpoints"""
    
    def test_filter_and_pagination_together(self, mock_issue_service, client, sample_issue):
        """Test combining filters and pagination"""
        # Setup mock service
        mock_issue_service.get_filtered_issues.return_value = ([sample_issue], 15)
        
        # Execute
        response = client.get(
            "/api/v1/issues/",
            params={
                "programming_languages": "Python,JavaScript",
                "labels": "good first issue",
                "difficulty_levels": "easy,medium",
                "page": 2,
                "page_size": 10
            }
        )
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 2
        assert data["page_size"] == 10
        assert data["total"] == 15
        assert data["total_pages"] == 2
    
    def test_multiple_filters_applied(self, mock_issue_service, client, sample_issue):
        """Test applying multiple filters simultaneously"""
        # Setup mock service
        mock_issue_service.get_filtered_issues.return_value = ([sample_issue], 1)
        
        # Execute
        response = client.get(
            "/api/v1/issues/",
            params={
                "programming_languages": "Python",
                "labels": "good first issue,help wanted",
                "difficulty_levels": "easy",
                "status": "available",
                "search_query": "test",
                "repository_id": 1
            }
        )
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        
        # Verify service was called with correct filters
        call_args = mock_issue_service.get_filtered_issues.call_args
        filters = call_args.kwargs['filters']
        assert filters.programming_languages == ["Python"]
        assert filters.labels == ["good first issue", "help wanted"]
        assert filters.difficulty_levels == ["easy"]
        assert filters.status == "available"
        assert filters.search_query == "test"
        assert filters.repository_id == 1
