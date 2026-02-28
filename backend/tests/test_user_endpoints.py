import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from datetime import datetime

from app.main import app
from app.models.user import User
from app.schemas.user import UserResponse


@pytest.fixture
def client():
    """Test client for API endpoints"""
    # Clear any existing dependency overrides
    app.dependency_overrides = {}
    return TestClient(app)


@pytest.fixture
def sample_user():
    """Sample user instance"""
    return User(
        id=1,
        github_username="testuser",
        github_id=12345,
        avatar_url="https://github.com/avatar.jpg",
        email="test@example.com",
        full_name="Test User",
        bio="Test bio",
        location="Test City",
        preferred_languages=["Python", "JavaScript"],
        preferred_labels=["good first issue"],
        total_contributions=5,
        merged_prs=3,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@pytest.fixture
def auth_headers():
    """Mock authentication headers with valid JWT token"""
    from app.core.security import create_access_token
    
    token = create_access_token({
        "sub": "1",
        "github_username": "testuser",
        "github_id": 12345
    })
    
    return {"Authorization": f"Bearer {token}"}


class TestUserProfileEndpoints:
    """Test suite for user profile endpoints"""
    
    def test_get_current_user_profile_success(self, client, sample_user, auth_headers):
        """
        Test getting current user profile
        Requirement: 1.3
        """
        from app.api.dependencies import get_current_user
        
        # Override the dependency
        app.dependency_overrides[get_current_user] = lambda: sample_user
        
        try:
            response = client.get("/api/v1/users/me", headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == 1
            assert data["github_username"] == "testuser"
            assert data["github_id"] == 12345
            assert data["preferred_languages"] == ["Python", "JavaScript"]
            assert data["preferred_labels"] == ["good first issue"]
            assert data["total_contributions"] == 5
            assert data["merged_prs"] == 3
        finally:
            # Clean up
            app.dependency_overrides = {}
    
    def test_get_current_user_profile_unauthorized(self, client):
        """Test getting profile without authentication"""
        response = client.get("/api/v1/users/me")
        
        assert response.status_code == 403  # No auth header
    
    def test_get_user_by_id_success(self, client, sample_user):
        """Test getting user profile by ID (public endpoint)"""
        with patch('app.services.user_service.UserService.get_user_by_id', return_value=sample_user):
            response = client.get("/api/v1/users/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["github_username"] == "testuser"
    
    def test_get_user_by_id_not_found(self, client):
        """Test getting non-existent user"""
        with patch('app.services.user_service.UserService.get_user_by_id', return_value=None):
            response = client.get("/api/v1/users/999")
        
        assert response.status_code == 404


class TestUserPreferencesEndpoints:
    """Test suite for user preferences endpoints"""
    
    def test_update_preferences_languages(self, client, sample_user, auth_headers):
        """
        Test updating user language preferences
        Requirements: 2.4, 2.5
        """
        from app.api.dependencies import get_current_user, get_db, get_redis_client
        from app.services.user_service import UserService
        
        updated_user = sample_user
        updated_user.preferred_languages = ["Python", "TypeScript", "Go"]
        
        # Mock dependencies
        mock_db = Mock()
        mock_redis = Mock()
        
        def mock_update_preferences(user_id, preferences):
            return updated_user
        
        app.dependency_overrides[get_current_user] = lambda: sample_user
        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_redis_client] = lambda: mock_redis
        
        try:
            with patch.object(UserService, 'update_preferences', side_effect=mock_update_preferences):
                response = client.put(
                    "/api/v1/users/me/preferences",
                    headers=auth_headers,
                    json={
                        "preferred_languages": ["Python", "TypeScript", "Go"]
                    }
                )
            
            assert response.status_code == 200
            data = response.json()
            assert data["preferred_languages"] == ["Python", "TypeScript", "Go"]
        finally:
            app.dependency_overrides = {}
    
    def test_update_preferences_labels(self, client, sample_user, auth_headers):
        """
        Test updating user label preferences
        Requirements: 2.4, 2.5
        """
        from app.api.dependencies import get_current_user, get_db, get_redis_client
        from app.services.user_service import UserService
        
        updated_user = sample_user
        updated_user.preferred_labels = ["beginner-friendly", "documentation"]
        
        # Mock dependencies
        mock_db = Mock()
        mock_redis = Mock()
        
        def mock_update_preferences(user_id, preferences):
            return updated_user
        
        app.dependency_overrides[get_current_user] = lambda: sample_user
        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_redis_client] = lambda: mock_redis
        
        try:
            with patch.object(UserService, 'update_preferences', side_effect=mock_update_preferences):
                response = client.put(
                    "/api/v1/users/me/preferences",
                    headers=auth_headers,
                    json={
                        "preferred_labels": ["beginner-friendly", "documentation"]
                    }
                )
            
            assert response.status_code == 200
            data = response.json()
            assert data["preferred_labels"] == ["beginner-friendly", "documentation"]
        finally:
            app.dependency_overrides = {}
    
    def test_update_preferences_both(self, client, sample_user, auth_headers):
        """Test updating both language and label preferences"""
        from app.api.dependencies import get_current_user, get_db, get_redis_client
        from app.services.user_service import UserService
        
        updated_user = sample_user
        updated_user.preferred_languages = ["Rust"]
        updated_user.preferred_labels = ["good first issue"]
        
        # Mock dependencies
        mock_db = Mock()
        mock_redis = Mock()
        
        def mock_update_preferences(user_id, preferences):
            return updated_user
        
        app.dependency_overrides[get_current_user] = lambda: sample_user
        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_redis_client] = lambda: mock_redis
        
        try:
            with patch.object(UserService, 'update_preferences', side_effect=mock_update_preferences):
                response = client.put(
                    "/api/v1/users/me/preferences",
                    headers=auth_headers,
                    json={
                        "preferred_languages": ["Rust"],
                        "preferred_labels": ["good first issue"]
                    }
                )
            
            assert response.status_code == 200
            data = response.json()
            assert data["preferred_languages"] == ["Rust"]
            assert data["preferred_labels"] == ["good first issue"]
        finally:
            app.dependency_overrides = {}
    
    def test_update_preferences_unauthorized(self, client):
        """Test updating preferences without authentication"""
        response = client.put(
            "/api/v1/users/me/preferences",
            json={"preferred_languages": ["Python"]}
        )
        
        assert response.status_code == 403


class TestUserStatisticsEndpoints:
    """Test suite for user statistics endpoints"""
    
    def test_get_current_user_stats_success(self, client, sample_user, auth_headers):
        """
        Test getting current user statistics
        Requirement: 6.1
        """
        from app.api.dependencies import get_current_user, get_db, get_redis_client
        from app.services.user_service import UserService
        
        mock_stats = {
            "user_id": 1,
            "total_contributions": 5,
            "total_prs_submitted": 8,
            "merged_prs": 3,
            "contributions_by_language": {
                "Python": 3,
                "JavaScript": 2
            },
            "contributions_by_repo": {
                "owner/repo1": 4,
                "owner/repo2": 1
            },
            "recent_contributions": [
                {
                    "contribution_id": 1,
                    "issue_title": "Fix bug in auth",
                    "repository": "owner/repo1",
                    "status": "merged",
                    "pr_url": "https://github.com/owner/repo1/pull/1",
                    "submitted_at": "2024-01-01T00:00:00",
                    "merged_at": "2024-01-02T00:00:00"
                }
            ],
            "calculated_at": "2024-01-01T00:00:00"
        }
        
        # Mock dependencies
        mock_db = Mock()
        mock_redis = Mock()
        
        app.dependency_overrides[get_current_user] = lambda: sample_user
        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_redis_client] = lambda: mock_redis
        
        try:
            with patch.object(UserService, 'get_user_stats', return_value=mock_stats):
                response = client.get("/api/v1/users/me/stats", headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == 1
            assert data["total_contributions"] == 5
            assert data["total_prs_submitted"] == 8
            assert data["merged_prs"] == 3
            assert "contributions_by_language" in data
            assert "contributions_by_repo" in data
            assert "recent_contributions" in data
            assert len(data["recent_contributions"]) == 1
        finally:
            app.dependency_overrides = {}
    
    def test_get_current_user_stats_unauthorized(self, client):
        """Test getting stats without authentication"""
        response = client.get("/api/v1/users/me/stats")
        
        assert response.status_code == 403
    
    def test_get_user_stats_by_id_success(self, client):
        """Test getting user statistics by ID (public endpoint)"""
        mock_stats = {
            "user_id": 1,
            "total_contributions": 5,
            "total_prs_submitted": 8,
            "merged_prs": 3,
            "contributions_by_language": {"Python": 3},
            "contributions_by_repo": {"owner/repo": 3},
            "recent_contributions": [],
            "calculated_at": "2024-01-01T00:00:00"
        }
        
        with patch('app.services.user_service.UserService.get_user_stats', return_value=mock_stats):
            response = client.get("/api/v1/users/1/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == 1
        assert data["total_contributions"] == 5


class TestUserEndpointsIntegration:
    """Integration tests for user endpoints"""
    
    def test_user_workflow_complete(self, client, sample_user, auth_headers):
        """Test complete user workflow: get profile, update preferences, get stats"""
        from app.api.dependencies import get_current_user, get_db, get_redis_client
        from app.services.user_service import UserService
        
        # Mock dependencies
        mock_db = Mock()
        mock_redis = Mock()
        
        app.dependency_overrides[get_current_user] = lambda: sample_user
        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_redis_client] = lambda: mock_redis
        
        try:
            # Step 1: Get current user profile
            profile_response = client.get("/api/v1/users/me", headers=auth_headers)
            
            assert profile_response.status_code == 200
            assert profile_response.json()["github_username"] == "testuser"
            
            # Step 2: Update preferences
            updated_user = sample_user
            updated_user.preferred_languages = ["Python", "Go"]
            
            with patch.object(UserService, 'update_preferences', return_value=updated_user):
                prefs_response = client.put(
                    "/api/v1/users/me/preferences",
                    headers=auth_headers,
                    json={"preferred_languages": ["Python", "Go"]}
                )
            
            assert prefs_response.status_code == 200
            assert prefs_response.json()["preferred_languages"] == ["Python", "Go"]
            
            # Step 3: Get user statistics
            mock_stats = {
                "user_id": 1,
                "total_contributions": 5,
                "total_prs_submitted": 8,
                "merged_prs": 3,
                "contributions_by_language": {"Python": 5},
                "contributions_by_repo": {"owner/repo": 5},
                "recent_contributions": [],
                "calculated_at": "2024-01-01T00:00:00"
            }
            
            with patch.object(UserService, 'get_user_stats', return_value=mock_stats):
                stats_response = client.get("/api/v1/users/me/stats", headers=auth_headers)
            
            assert stats_response.status_code == 200
            assert stats_response.json()["total_contributions"] == 5
        finally:
            app.dependency_overrides = {}
