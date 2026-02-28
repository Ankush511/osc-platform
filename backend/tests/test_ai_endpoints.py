"""
Tests for AI service API endpoints
"""
import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.services.ai_service import AIServiceException, RateLimitException
from app.schemas.ai import DifficultyLevel, LearningResource


client = TestClient(app)


@pytest.fixture
def auth_headers(test_user_token):
    """Get authentication headers"""
    return {"Authorization": f"Bearer {test_user_token}"}


@pytest.fixture
def mock_ai_service():
    """Mock AI service"""
    with patch('app.api.v1.ai.get_ai_service') as mock:
        service = Mock()
        mock.return_value = service
        yield service


class TestRepositorySummaryEndpoint:
    """Test repository summary endpoint"""
    
    def test_generate_summary_success(self, auth_headers, mock_ai_service, sample_repository):
        """Test successful repository summary generation"""
        mock_ai_service.redis_client = None
        mock_ai_service._get_cached_response.return_value = None
        mock_ai_service.generate_repository_summary.return_value = "This is a test repository summary."
        
        response = client.post(
            "/api/v1/ai/repository-summary",
            json={"repository_id": sample_repository.id, "force_regenerate": False},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["repository_id"] == sample_repository.id
        assert data["summary"] == "This is a test repository summary."
        assert data["cached"] is False
    
    def test_generate_summary_from_cache(self, auth_headers, mock_ai_service, sample_repository):
        """Test repository summary retrieval from cache"""
        mock_ai_service.redis_client = Mock()
        mock_ai_service._get_cached_response.return_value = "Cached summary"
        
        response = client.post(
            "/api/v1/ai/repository-summary",
            json={"repository_id": sample_repository.id, "force_regenerate": False},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["summary"] == "Cached summary"
        assert data["cached"] is True
    
    def test_generate_summary_force_regenerate(self, auth_headers, mock_ai_service, sample_repository):
        """Test forced regeneration of repository summary"""
        mock_ai_service.redis_client = None
        mock_ai_service._get_cached_response.return_value = None
        mock_ai_service.generate_repository_summary.return_value = "New summary"
        
        response = client.post(
            "/api/v1/ai/repository-summary",
            json={"repository_id": sample_repository.id, "force_regenerate": True},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["summary"] == "New summary"
        assert data["cached"] is False
        mock_ai_service.generate_repository_summary.assert_called_once_with(
            repository_id=sample_repository.id,
            force_regenerate=True
        )
    
    def test_generate_summary_rate_limit_exceeded(self, auth_headers, mock_ai_service, sample_repository):
        """Test rate limit exceeded error"""
        mock_ai_service.redis_client = None
        mock_ai_service._get_cached_response.return_value = None
        mock_ai_service.generate_repository_summary.side_effect = RateLimitException("Rate limit exceeded")
        
        response = client.post(
            "/api/v1/ai/repository-summary",
            json={"repository_id": sample_repository.id, "force_regenerate": False},
            headers=auth_headers
        )
        
        assert response.status_code == 429
        data = response.json()
        assert data["detail"]["error_code"] == "RATE_LIMIT_EXCEEDED"
    
    def test_generate_summary_ai_service_error(self, auth_headers, mock_ai_service, sample_repository):
        """Test AI service error"""
        mock_ai_service.redis_client = None
        mock_ai_service._get_cached_response.return_value = None
        mock_ai_service.generate_repository_summary.side_effect = AIServiceException("AI service failed")
        
        response = client.post(
            "/api/v1/ai/repository-summary",
            json={"repository_id": sample_repository.id, "force_regenerate": False},
            headers=auth_headers
        )
        
        assert response.status_code == 500
        data = response.json()
        assert data["detail"]["error_code"] == "AI_SERVICE_ERROR"
    
    def test_generate_summary_unauthorized(self, sample_repository):
        """Test unauthorized access"""
        response = client.post(
            "/api/v1/ai/repository-summary",
            json={"repository_id": sample_repository.id, "force_regenerate": False}
        )
        
        assert response.status_code == 401


class TestIssueExplanationEndpoint:
    """Test issue explanation endpoint"""
    
    def test_generate_explanation_success(self, auth_headers, mock_ai_service, sample_issue):
        """Test successful issue explanation generation"""
        mock_ai_service.redis_client = None
        mock_ai_service._get_cached_response.return_value = None
        mock_ai_service.explain_issue.return_value = "This is a test issue explanation."
        mock_ai_service.analyze_difficulty.return_value = DifficultyLevel.EASY
        mock_ai_service.suggest_learning_resources.return_value = [
            LearningResource(
                title="Test Resource",
                url="https://example.com",
                type="tutorial",
                description="A test resource"
            )
        ]
        
        response = client.post(
            "/api/v1/ai/issue-explanation",
            json={"issue_id": sample_issue.id, "force_regenerate": False},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["issue_id"] == sample_issue.id
        assert data["explanation"] == "This is a test issue explanation."
        assert data["difficulty_level"] == "easy"
        assert len(data["learning_resources"]) == 1
        assert data["learning_resources"][0]["title"] == "Test Resource"
        assert data["cached"] is False
    
    def test_generate_explanation_from_cache(self, auth_headers, mock_ai_service, sample_issue):
        """Test issue explanation retrieval from cache"""
        mock_ai_service.redis_client = Mock()
        mock_ai_service._get_cached_response.return_value = "Cached explanation"
        mock_ai_service.analyze_difficulty.return_value = DifficultyLevel.MEDIUM
        mock_ai_service.suggest_learning_resources.return_value = []
        
        response = client.post(
            "/api/v1/ai/issue-explanation",
            json={"issue_id": sample_issue.id, "force_regenerate": False},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["explanation"] == "Cached explanation"
        assert data["difficulty_level"] == "medium"
        assert data["cached"] is True
    
    def test_generate_explanation_force_regenerate(self, auth_headers, mock_ai_service, sample_issue):
        """Test forced regeneration of issue explanation"""
        mock_ai_service.redis_client = None
        mock_ai_service._get_cached_response.return_value = None
        mock_ai_service.explain_issue.return_value = "New explanation"
        mock_ai_service.analyze_difficulty.return_value = DifficultyLevel.HARD
        mock_ai_service.suggest_learning_resources.return_value = []
        
        response = client.post(
            "/api/v1/ai/issue-explanation",
            json={"issue_id": sample_issue.id, "force_regenerate": True},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["explanation"] == "New explanation"
        assert data["difficulty_level"] == "hard"
        assert data["cached"] is False
        mock_ai_service.explain_issue.assert_called_once_with(
            issue_id=sample_issue.id,
            force_regenerate=True
        )
    
    def test_generate_explanation_rate_limit_exceeded(self, auth_headers, mock_ai_service, sample_issue):
        """Test rate limit exceeded error"""
        mock_ai_service.redis_client = None
        mock_ai_service._get_cached_response.return_value = None
        mock_ai_service.explain_issue.side_effect = RateLimitException("Rate limit exceeded")
        
        response = client.post(
            "/api/v1/ai/issue-explanation",
            json={"issue_id": sample_issue.id, "force_regenerate": False},
            headers=auth_headers
        )
        
        assert response.status_code == 429
        data = response.json()
        assert data["detail"]["error_code"] == "RATE_LIMIT_EXCEEDED"
    
    def test_generate_explanation_ai_service_error(self, auth_headers, mock_ai_service, sample_issue):
        """Test AI service error"""
        mock_ai_service.redis_client = None
        mock_ai_service._get_cached_response.return_value = None
        mock_ai_service.explain_issue.side_effect = AIServiceException("AI service failed")
        
        response = client.post(
            "/api/v1/ai/issue-explanation",
            json={"issue_id": sample_issue.id, "force_regenerate": False},
            headers=auth_headers
        )
        
        assert response.status_code == 500
        data = response.json()
        assert data["detail"]["error_code"] == "AI_SERVICE_ERROR"
    
    def test_generate_explanation_unauthorized(self, sample_issue):
        """Test unauthorized access"""
        response = client.post(
            "/api/v1/ai/issue-explanation",
            json={"issue_id": sample_issue.id, "force_regenerate": False}
        )
        
        assert response.status_code == 401
    
    def test_generate_explanation_with_multiple_resources(self, auth_headers, mock_ai_service, sample_issue):
        """Test issue explanation with multiple learning resources"""
        mock_ai_service.redis_client = None
        mock_ai_service._get_cached_response.return_value = None
        mock_ai_service.explain_issue.return_value = "Explanation"
        mock_ai_service.analyze_difficulty.return_value = DifficultyLevel.MEDIUM
        mock_ai_service.suggest_learning_resources.return_value = [
            LearningResource(
                title="Resource 1",
                url="https://example.com/1",
                type="documentation",
                description="First resource"
            ),
            LearningResource(
                title="Resource 2",
                url="https://example.com/2",
                type="tutorial",
                description="Second resource"
            ),
            LearningResource(
                title="Resource 3",
                url="https://example.com/3",
                type="video",
                description="Third resource"
            )
        ]
        
        response = client.post(
            "/api/v1/ai/issue-explanation",
            json={"issue_id": sample_issue.id, "force_regenerate": False},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["learning_resources"]) == 3
        assert data["learning_resources"][0]["type"] == "documentation"
        assert data["learning_resources"][1]["type"] == "tutorial"
        assert data["learning_resources"][2]["type"] == "video"
