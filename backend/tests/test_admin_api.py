"""
Tests for admin API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from app.main import app
from app.models.user import User
from app.api.dependencies import get_current_user


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def admin_user():
    """Create mock admin user"""
    user = Mock(spec=User)
    user.id = 1
    user.github_username = "admin"
    user.is_admin = True
    return user


@pytest.fixture
def regular_user():
    """Create mock regular user"""
    user = Mock(spec=User)
    user.id = 2
    user.github_username = "user"
    user.is_admin = False
    return user


class TestAdminAuthentication:
    """Tests for admin authentication"""
    
    def test_admin_endpoint_requires_auth(self, client):
        """Test that admin endpoints require authentication"""
        response = client.get("/api/v1/admin/stats")
        assert response.status_code == 403
    
    def test_admin_endpoint_requires_admin_role(self, client, regular_user):
        """Test that admin endpoints require admin role"""
        app.dependency_overrides[get_current_user] = lambda: regular_user
        try:
            response = client.get("/api/v1/admin/stats")
            assert response.status_code == 403
        finally:
            app.dependency_overrides.clear()


class TestPlatformStats:
    """Tests for platform statistics endpoint"""
    
    def test_get_platform_stats(self, client, admin_user):
        """Test getting platform statistics"""
        mock_stats = {
            "total_users": 100,
            "active_users_last_30_days": 50,
            "total_repositories": 20,
            "active_repositories": 15,
            "total_issues": 500,
            "available_issues": 200,
            "claimed_issues": 150,
            "completed_issues": 100,
            "total_contributions": 300,
            "merged_prs": 250,
            "pending_prs": 50
        }
        
        app.dependency_overrides[get_current_user] = lambda: admin_user
        
        try:
            with patch('app.api.v1.admin.AdminService') as MockAdminService:
                mock_service = Mock()
                mock_service.get_platform_stats.return_value = Mock(**mock_stats)
                MockAdminService.return_value = mock_service
                
                response = client.get("/api/v1/admin/stats")
                
                assert response.status_code == 200
                data = response.json()
                assert data["total_users"] == 100
                assert data["active_users_last_30_days"] == 50
        finally:
            app.dependency_overrides.clear()


class TestRepositoryManagement:
    """Tests for repository management endpoints"""
    
    def test_get_repositories(self, client, admin_user):
        """Test getting repositories"""
        app.dependency_overrides[get_current_user] = lambda: admin_user
        
        try:
            with patch('app.api.v1.admin.AdminService') as MockAdminService:
                mock_service = Mock()
                mock_service.get_repositories.return_value = ([], 0)
                MockAdminService.return_value = mock_service
                
                response = client.get("/api/v1/admin/repositories")
                
                assert response.status_code == 200
                data = response.json()
                assert "repositories" in data
                assert "total" in data
        finally:
            app.dependency_overrides.clear()
    
    @pytest.mark.asyncio
    async def test_add_repository(self, client, admin_user):
        """Test adding a repository"""
        app.dependency_overrides[get_current_user] = lambda: admin_user
        
        try:
            with patch('app.api.v1.admin.AdminService') as MockAdminService:
                mock_service = Mock()
                mock_repo = Mock()
                mock_repo.id = 1
                mock_repo.full_name = "facebook/react"
                mock_repo.name = "react"
                mock_repo.description = "A JavaScript library"
                mock_repo.primary_language = "JavaScript"
                mock_repo.stars = 50000
                mock_repo.forks = 10000
                mock_repo.is_active = True
                mock_repo.last_synced = None
                mock_repo.created_at = datetime.utcnow()
                
                mock_service.add_repository = AsyncMock(return_value=mock_repo)
                MockAdminService.return_value = mock_service
                
                response = client.post(
                    "/api/v1/admin/repositories",
                    json={"full_name": "facebook/react"}
                )
                
                assert response.status_code == 201
                data = response.json()
                assert data["full_name"] == "facebook/react"
        finally:
            app.dependency_overrides.clear()
    
    def test_update_repository(self, client, admin_user):
        """Test updating repository"""
        app.dependency_overrides[get_current_user] = lambda: admin_user
        
        # Mock the database dependency
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.scalar.return_value = 10
        from app.api.dependencies import get_db
        app.dependency_overrides[get_db] = lambda: mock_db
        
        try:
            with patch('app.api.v1.admin.AdminService') as MockAdminService:
                mock_service = Mock()
                mock_repo = Mock()
                mock_repo.id = 1
                mock_repo.full_name = "facebook/react"
                mock_repo.name = "react"
                mock_repo.description = "A JavaScript library"
                mock_repo.primary_language = "JavaScript"
                mock_repo.stars = 50000
                mock_repo.forks = 10000
                mock_repo.is_active = False
                mock_repo.last_synced = None
                mock_repo.created_at = datetime.utcnow()
                
                mock_service.update_repository.return_value = mock_repo
                MockAdminService.return_value = mock_service
                
                response = client.patch(
                    "/api/v1/admin/repositories/1",
                    json={"is_active": False}
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["is_active"] == False
        finally:
            app.dependency_overrides.clear()
    
    def test_delete_repository(self, client, admin_user):
        """Test deleting repository"""
        app.dependency_overrides[get_current_user] = lambda: admin_user
        
        try:
            with patch('app.api.v1.admin.AdminService') as MockAdminService:
                mock_service = Mock()
                mock_service.delete_repository.return_value = True
                MockAdminService.return_value = mock_service
                
                response = client.delete("/api/v1/admin/repositories/1")
                
                assert response.status_code == 204
        finally:
            app.dependency_overrides.clear()


class TestUserManagement:
    """Tests for user management endpoints"""
    
    def test_get_users(self, client, admin_user):
        """Test getting users"""
        app.dependency_overrides[get_current_user] = lambda: admin_user
        
        try:
            with patch('app.api.v1.admin.AdminService') as MockAdminService:
                mock_service = Mock()
                mock_service.get_users.return_value = ([], 0)
                MockAdminService.return_value = mock_service
                
                response = client.get("/api/v1/admin/users")
                
                assert response.status_code == 200
                data = response.json()
                assert "users" in data
                assert "total" in data
        finally:
            app.dependency_overrides.clear()
    
    def test_update_user_role(self, client, admin_user):
        """Test updating user role"""
        app.dependency_overrides[get_current_user] = lambda: admin_user
        
        # Mock the database dependency
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.scalar.return_value = 2
        from app.api.dependencies import get_db
        app.dependency_overrides[get_db] = lambda: mock_db
        
        try:
            with patch('app.api.v1.admin.AdminService') as MockAdminService:
                mock_service = Mock()
                mock_user = Mock()
                mock_user.id = 2
                mock_user.github_username = "testuser"
                mock_user.email = "test@example.com"
                mock_user.full_name = "Test User"
                mock_user.is_admin = True
                mock_user.total_contributions = 10
                mock_user.merged_prs = 5
                mock_user.created_at = datetime.utcnow()
                
                mock_service.update_user_role.return_value = mock_user
                MockAdminService.return_value = mock_service
                
                response = client.patch(
                    "/api/v1/admin/users/2/role",
                    json={"is_admin": True}
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["is_admin"] == True
        finally:
            app.dependency_overrides.clear()


class TestSystemHealth:
    """Tests for system health endpoint"""
    
    @pytest.mark.asyncio
    async def test_check_system_health(self, client, admin_user):
        """Test checking system health"""
        app.dependency_overrides[get_current_user] = lambda: admin_user
        
        try:
            with patch('app.api.v1.admin.AdminService') as MockAdminService:
                mock_service = Mock()
                mock_health = Mock()
                mock_health.status = "healthy"
                mock_health.database = {"status": "healthy", "details": {}}
                mock_health.redis = {"status": "healthy", "details": {}}
                mock_health.github_api = {"status": "healthy", "details": {}}
                mock_health.ai_service = {"status": "configured", "details": {}}
                mock_health.celery = {"status": "unknown", "details": {}}
                mock_health.timestamp = datetime.utcnow()
                
                mock_service.check_system_health = AsyncMock(return_value=mock_health)
                MockAdminService.return_value = mock_service
                
                response = client.get("/api/v1/admin/health")
                
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "healthy"
        finally:
            app.dependency_overrides.clear()


class TestConfiguration:
    """Tests for configuration endpoints"""
    
    def test_get_configuration(self, client, admin_user):
        """Test getting configuration"""
        app.dependency_overrides[get_current_user] = lambda: admin_user
        
        try:
            with patch('app.api.v1.admin.AdminService') as MockAdminService:
                mock_service = Mock()
                mock_config = Mock()
                mock_config.github_client_id = "test-client-id"
                mock_config.openai_configured = True
                mock_config.email_enabled = True
                mock_config.claim_timeout_easy_days = 7
                mock_config.claim_timeout_medium_days = 14
                mock_config.claim_timeout_hard_days = 21
                mock_config.claim_grace_period_hours = 24
                mock_config.environment = "development"
                
                mock_service.get_configuration.return_value = mock_config
                MockAdminService.return_value = mock_service
                
                response = client.get("/api/v1/admin/config")
                
                assert response.status_code == 200
                data = response.json()
                assert data["github_client_id"] == "test-client-id"
        finally:
            app.dependency_overrides.clear()
    
    def test_update_configuration(self, client, admin_user):
        """Test updating configuration"""
        app.dependency_overrides[get_current_user] = lambda: admin_user
        
        try:
            with patch('app.api.v1.admin.AdminService') as MockAdminService:
                mock_service = Mock()
                mock_config = Mock()
                mock_config.github_client_id = "test-client-id"
                mock_config.openai_configured = True
                mock_config.email_enabled = True
                mock_config.claim_timeout_easy_days = 10
                mock_config.claim_timeout_medium_days = 14
                mock_config.claim_timeout_hard_days = 21
                mock_config.claim_grace_period_hours = 24
                mock_config.environment = "development"
                
                mock_service.update_configuration.return_value = mock_config
                MockAdminService.return_value = mock_service
                
                response = client.patch(
                    "/api/v1/admin/config",
                    json={"claim_timeout_easy_days": 10}
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["claim_timeout_easy_days"] == 10
        finally:
            app.dependency_overrides.clear()
