"""
Tests for admin service
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from sqlalchemy.orm import Session

from app.services.admin_service import AdminService
from app.models.user import User
from app.models.repository import Repository
from app.models.issue import Issue, IssueStatus
from app.models.contribution import Contribution, ContributionStatus


@pytest.fixture
def mock_db():
    """Mock database session"""
    return Mock(spec=Session)


@pytest.fixture
def mock_redis():
    """Mock Redis client"""
    redis_mock = Mock()
    redis_mock.ping.return_value = True
    redis_mock.info.return_value = {
        'connected_clients': 5,
        'used_memory_human': '1.5M'
    }
    return redis_mock


@pytest.fixture
def admin_service(mock_db, mock_redis):
    """Create admin service instance"""
    return AdminService(mock_db, mock_redis)


class TestPlatformStats:
    """Tests for platform statistics"""
    
    def test_get_platform_stats_success(self, admin_service, mock_db):
        """Test getting platform statistics"""
        # Create a mock query chain that returns proper values
        mock_query = Mock()
        
        # Set up the query chain to return different values for each call
        call_count = [0]
        def mock_scalar():
            values = [
                100,  # total_users
                50,   # active_users
                20,   # total_repositories
                15,   # active_repositories
                500,  # total_issues
                200,  # available_issues
                150,  # claimed_issues
                100,  # completed_issues
                300,  # total_contributions
                250,  # merged_prs
                50    # pending_prs
            ]
            result = values[call_count[0]]
            call_count[0] += 1
            return result
        
        mock_query.scalar = mock_scalar
        mock_query.filter.return_value = mock_query
        mock_db.query.return_value = mock_query
        
        stats = admin_service.get_platform_stats()
        
        assert stats.total_users == 100
        assert stats.active_users_last_30_days == 50
        assert stats.total_repositories == 20
        assert stats.active_repositories == 15
        assert stats.total_issues == 500
        assert stats.available_issues == 200
        assert stats.claimed_issues == 150
        assert stats.completed_issues == 100
        assert stats.total_contributions == 300
        assert stats.merged_prs == 250
        assert stats.pending_prs == 50


class TestRepositoryManagement:
    """Tests for repository management"""
    
    def test_get_repositories(self, admin_service, mock_db):
        """Test getting repositories with pagination"""
        # Mock repository data
        mock_repo = Mock(spec=Repository)
        mock_repo.id = 1
        mock_repo.full_name = "test/repo"
        mock_repo.name = "repo"
        mock_repo.description = "Test repository"
        mock_repo.primary_language = "Python"
        mock_repo.stars = 100
        mock_repo.forks = 50
        mock_repo.is_active = True
        mock_repo.last_synced = datetime.utcnow()
        mock_repo.created_at = datetime.utcnow()
        
        mock_query = Mock()
        mock_query.count.return_value = 1
        mock_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_repo]
        mock_db.query.return_value = mock_query
        
        # Mock issue count
        mock_db.query.return_value.filter.return_value.scalar.return_value = 10
        
        repositories, total = admin_service.get_repositories(page=1, page_size=20)
        
        assert total == 1
        assert len(repositories) == 1
        assert repositories[0].full_name == "test/repo"
        assert repositories[0].issue_count == 10
    
    @pytest.mark.asyncio
    async def test_add_repository_success(self, admin_service, mock_db):
        """Test adding a new repository"""
        # Mock GitHub service
        mock_repo_info = Mock()
        mock_repo_info.id = 12345
        mock_repo_info.full_name = "facebook/react"
        mock_repo_info.name = "react"
        mock_repo_info.description = "A JavaScript library"
        mock_repo_info.language = "JavaScript"
        mock_repo_info.topics = ["javascript", "react"]
        mock_repo_info.stargazers_count = 50000
        mock_repo_info.forks_count = 10000
        
        with patch('app.services.admin_service.GitHubService') as MockGitHubService:
            mock_github = AsyncMock()
            mock_github.get_repository_info.return_value = mock_repo_info
            mock_github.close = AsyncMock()
            MockGitHubService.return_value = mock_github
            
            # Mock database query
            mock_db.query.return_value.filter.return_value.first.return_value = None
            
            repo = await admin_service.add_repository("facebook/react")
            
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_add_repository_already_exists(self, admin_service, mock_db):
        """Test adding a repository that already exists"""
        # Mock existing repository
        mock_db.query.return_value.filter.return_value.first.return_value = Mock()
        
        with pytest.raises(ValueError, match="already exists"):
            await admin_service.add_repository("facebook/react")
    
    def test_update_repository(self, admin_service, mock_db):
        """Test updating repository settings"""
        mock_repo = Mock(spec=Repository)
        mock_repo.id = 1
        mock_repo.full_name = "test/repo"
        mock_repo.is_active = True
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_repo
        
        updated_repo = admin_service.update_repository(1, False)
        
        assert updated_repo.is_active == False
        mock_db.commit.assert_called_once()
    
    def test_delete_repository(self, admin_service, mock_db):
        """Test deleting a repository"""
        mock_repo = Mock(spec=Repository)
        mock_repo.id = 1
        mock_repo.full_name = "test/repo"
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_repo
        
        result = admin_service.delete_repository(1)
        
        assert result == True
        mock_db.delete.assert_called_once_with(mock_repo)
        mock_db.commit.assert_called_once()


class TestUserManagement:
    """Tests for user management"""
    
    def test_get_users(self, admin_service, mock_db):
        """Test getting users with pagination"""
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.github_username = "testuser"
        mock_user.email = "test@example.com"
        mock_user.full_name = "Test User"
        mock_user.is_admin = False
        mock_user.total_contributions = 10
        mock_user.merged_prs = 5
        mock_user.created_at = datetime.utcnow()
        
        mock_query = Mock()
        mock_query.count.return_value = 1
        mock_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_user]
        mock_db.query.return_value = mock_query
        
        # Mock claimed issues count
        mock_db.query.return_value.filter.return_value.scalar.return_value = 2
        
        users, total = admin_service.get_users(page=1, page_size=20)
        
        assert total == 1
        assert len(users) == 1
        assert users[0].github_username == "testuser"
        assert users[0].claimed_issues_count == 2
    
    def test_update_user_role(self, admin_service, mock_db):
        """Test updating user admin role"""
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.github_username = "testuser"
        mock_user.is_admin = False
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        updated_user = admin_service.update_user_role(1, True)
        
        assert updated_user.is_admin == True
        mock_db.commit.assert_called_once()


class TestSystemHealth:
    """Tests for system health checks"""
    
    @pytest.mark.asyncio
    async def test_check_system_health_all_healthy(self, admin_service, mock_db, mock_redis):
        """Test system health check when all components are healthy"""
        # Mock database check
        mock_db.execute.return_value = None
        
        # Mock GitHub service
        mock_rate_limit = Mock()
        mock_rate_limit.remaining = 5000
        mock_rate_limit.limit = 5000
        mock_rate_limit.reset_at = datetime.utcnow()
        
        with patch('app.services.admin_service.GitHubService') as MockGitHubService:
            mock_github = AsyncMock()
            mock_github.get_rate_limit.return_value = mock_rate_limit
            mock_github.close = AsyncMock()
            MockGitHubService.return_value = mock_github
            
            with patch('app.services.admin_service.settings') as mock_settings:
                mock_settings.OPENAI_API_KEY = "test-key"
                
                health = await admin_service.check_system_health()
                
                assert health.status == "healthy"
                assert health.database["status"] == "healthy"
                assert health.redis["status"] == "healthy"
                assert health.github_api["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_check_system_health_database_unhealthy(self, admin_service, mock_db, mock_redis):
        """Test system health check when database is unhealthy"""
        # Mock database failure
        mock_db.execute.side_effect = Exception("Database connection failed")
        
        # Mock GitHub service
        mock_rate_limit = Mock()
        mock_rate_limit.remaining = 5000
        mock_rate_limit.limit = 5000
        mock_rate_limit.reset_at = datetime.utcnow()
        
        with patch('app.services.admin_service.GitHubService') as MockGitHubService:
            mock_github = AsyncMock()
            mock_github.get_rate_limit.return_value = mock_rate_limit
            mock_github.close = AsyncMock()
            MockGitHubService.return_value = mock_github
            
            with patch('app.services.admin_service.settings') as mock_settings:
                mock_settings.OPENAI_API_KEY = "test-key"
                
                health = await admin_service.check_system_health()
                
                assert health.status == "unhealthy"
                assert health.database["status"] == "unhealthy"


class TestConfiguration:
    """Tests for configuration management"""
    
    def test_get_configuration(self, admin_service):
        """Test getting current configuration"""
        with patch('app.services.admin_service.settings') as mock_settings:
            mock_settings.GITHUB_CLIENT_ID = "test-client-id"
            mock_settings.OPENAI_API_KEY = "test-key"
            mock_settings.EMAIL_ENABLED = True
            mock_settings.CLAIM_TIMEOUT_EASY_DAYS = 7
            mock_settings.CLAIM_TIMEOUT_MEDIUM_DAYS = 14
            mock_settings.CLAIM_TIMEOUT_HARD_DAYS = 21
            mock_settings.CLAIM_GRACE_PERIOD_HOURS = 24
            mock_settings.ENVIRONMENT = "development"
            
            config = admin_service.get_configuration()
            
            assert config.github_client_id == "test-client-id"
            assert config.openai_configured == True
            assert config.email_enabled == True
            assert config.claim_timeout_easy_days == 7
    
    def test_update_configuration(self, admin_service):
        """Test updating configuration"""
        with patch('app.services.admin_service.settings') as mock_settings:
            mock_settings.GITHUB_CLIENT_ID = "test-client-id"
            mock_settings.OPENAI_API_KEY = "test-key"
            mock_settings.EMAIL_ENABLED = False
            mock_settings.CLAIM_TIMEOUT_EASY_DAYS = 7
            mock_settings.CLAIM_TIMEOUT_MEDIUM_DAYS = 14
            mock_settings.CLAIM_TIMEOUT_HARD_DAYS = 21
            mock_settings.CLAIM_GRACE_PERIOD_HOURS = 24
            mock_settings.ENVIRONMENT = "development"
            
            updates = {
                "claim_timeout_easy_days": 10,
                "email_enabled": True
            }
            
            config = admin_service.update_configuration(updates)
            
            assert mock_settings.CLAIM_TIMEOUT_EASY_DAYS == 10
            assert mock_settings.EMAIL_ENABLED == True


class TestRateLimit:
    """Tests for rate limit status"""
    
    @pytest.mark.asyncio
    async def test_get_rate_limit_status(self, admin_service):
        """Test getting GitHub API rate limit status"""
        mock_rate_limit = Mock()
        mock_rate_limit.limit = 5000
        mock_rate_limit.remaining = 4000
        mock_rate_limit.reset_at = datetime.utcnow()
        
        with patch('app.services.admin_service.GitHubService') as MockGitHubService:
            mock_github = AsyncMock()
            mock_github.get_rate_limit.return_value = mock_rate_limit
            mock_github.close = AsyncMock()
            MockGitHubService.return_value = mock_github
            
            rate_limit = await admin_service.get_rate_limit_status()
            
            assert rate_limit.limit == 5000
            assert rate_limit.remaining == 4000
            assert rate_limit.used == 1000
            assert rate_limit.percentage_used == 20.0
