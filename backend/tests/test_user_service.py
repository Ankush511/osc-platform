import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException
import json

from app.services.user_service import UserService
from app.models.user import User
from app.models.contribution import Contribution
from app.models.issue import Issue
from app.models.repository import Repository
from app.schemas.auth import GitHubUserData
from app.schemas.user import UserUpdate


@pytest.fixture
def db_session():
    """Mock database session"""
    return Mock(spec=Session)


@pytest.fixture
def redis_client():
    """Mock Redis client"""
    mock_redis = Mock()
    mock_redis.get.return_value = None
    mock_redis.setex.return_value = True
    mock_redis.delete.return_value = True
    return mock_redis


@pytest.fixture
def user_service(db_session, redis_client):
    """Create user service instance"""
    return UserService(db_session, redis_client)


@pytest.fixture
def github_user_data():
    """Sample GitHub user data"""
    return GitHubUserData(
        login="testuser",
        id=12345,
        avatar_url="https://github.com/avatar.jpg",
        name="Test User",
        email="test@example.com",
        bio="Test bio",
        location="Test City"
    )


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
        preferred_labels=["good first issue", "help wanted"],
        total_contributions=5,
        merged_prs=3,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


class TestUserServiceRegistration:
    """Test suite for user registration functionality"""
    
    def test_create_user_success(self, user_service, db_session, github_user_data):
        """
        Test successful user creation from GitHub profile data
        Requirements: 1.2, 1.3
        """
        # Mock database query to return no existing user
        db_session.query.return_value.filter.return_value.first.return_value = None
        
        # Execute user creation
        result = user_service.create_user(github_user_data)
        
        # Verify user was added to database
        db_session.add.assert_called_once()
        db_session.commit.assert_called_once()
        db_session.refresh.assert_called_once()
        
        # Verify user data
        added_user = db_session.add.call_args[0][0]
        assert added_user.github_username == "testuser"
        assert added_user.github_id == 12345
        assert added_user.avatar_url == "https://github.com/avatar.jpg"
        assert added_user.email == "test@example.com"
        assert added_user.full_name == "Test User"
        assert added_user.bio == "Test bio"
        assert added_user.location == "Test City"
        assert added_user.preferred_languages == []
        assert added_user.preferred_labels == []
        assert added_user.total_contributions == 0
        assert added_user.merged_prs == 0
    
    def test_create_user_duplicate(self, user_service, db_session, github_user_data, sample_user):
        """
        Test user creation fails when user already exists
        Requirement: 1.4
        """
        # Mock database query to return existing user
        db_session.query.return_value.filter.return_value.first.return_value = sample_user
        
        # Execute and verify exception
        with pytest.raises(HTTPException) as exc_info:
            user_service.create_user(github_user_data)
        
        assert exc_info.value.status_code == 400
        assert "already exists" in exc_info.value.detail
        
        # Verify no user was added
        db_session.add.assert_not_called()


class TestUserServiceRetrieval:
    """Test suite for user retrieval operations"""
    
    def test_get_user_by_id_success(self, user_service, db_session, sample_user):
        """Test successful user retrieval by ID"""
        db_session.query.return_value.filter.return_value.first.return_value = sample_user
        
        result = user_service.get_user_by_id(1)
        
        assert result == sample_user
        db_session.query.assert_called_once()
    
    def test_get_user_by_id_not_found(self, user_service, db_session):
        """Test user retrieval when user doesn't exist"""
        db_session.query.return_value.filter.return_value.first.return_value = None
        
        result = user_service.get_user_by_id(999)
        
        assert result is None
    
    def test_get_user_by_github_id_success(self, user_service, db_session, sample_user):
        """Test successful user retrieval by GitHub ID"""
        db_session.query.return_value.filter.return_value.first.return_value = sample_user
        
        result = user_service.get_user_by_github_id(12345)
        
        assert result == sample_user
    
    def test_get_user_by_username_success(self, user_service, db_session, sample_user):
        """Test successful user retrieval by GitHub username"""
        db_session.query.return_value.filter.return_value.first.return_value = sample_user
        
        result = user_service.get_user_by_username("testuser")
        
        assert result == sample_user


class TestUserServicePreferences:
    """Test suite for user preference management"""
    
    def test_update_preferences_languages(self, user_service, db_session, sample_user, redis_client):
        """
        Test updating user language preferences
        Requirements: 2.4, 2.5
        """
        db_session.query.return_value.filter.return_value.first.return_value = sample_user
        
        preferences = UserUpdate(
            preferred_languages=["Python", "TypeScript", "Go"],
            preferred_labels=None
        )
        
        result = user_service.update_preferences(1, preferences)
        
        # Verify preferences were updated
        assert sample_user.preferred_languages == ["Python", "TypeScript", "Go"]
        db_session.commit.assert_called_once()
        db_session.refresh.assert_called_once()
        
        # Verify cache was invalidated
        redis_client.delete.assert_called_once_with("user_stats:1")
    
    def test_update_preferences_labels(self, user_service, db_session, sample_user, redis_client):
        """
        Test updating user label preferences
        Requirements: 2.4, 2.5
        """
        db_session.query.return_value.filter.return_value.first.return_value = sample_user
        
        preferences = UserUpdate(
            preferred_languages=None,
            preferred_labels=["beginner-friendly", "documentation"]
        )
        
        result = user_service.update_preferences(1, preferences)
        
        # Verify preferences were updated
        assert sample_user.preferred_labels == ["beginner-friendly", "documentation"]
        db_session.commit.assert_called_once()
    
    def test_update_preferences_both(self, user_service, db_session, sample_user):
        """Test updating both language and label preferences"""
        db_session.query.return_value.filter.return_value.first.return_value = sample_user
        
        preferences = UserUpdate(
            preferred_languages=["Rust"],
            preferred_labels=["good first issue"]
        )
        
        result = user_service.update_preferences(1, preferences)
        
        assert sample_user.preferred_languages == ["Rust"]
        assert sample_user.preferred_labels == ["good first issue"]
    
    def test_update_preferences_user_not_found(self, user_service, db_session):
        """Test preference update when user doesn't exist"""
        db_session.query.return_value.filter.return_value.first.return_value = None
        
        preferences = UserUpdate(preferred_languages=["Python"])
        
        with pytest.raises(HTTPException) as exc_info:
            user_service.update_preferences(999, preferences)
        
        assert exc_info.value.status_code == 404


class TestUserServiceProfile:
    """Test suite for user profile updates"""
    
    def test_update_profile_success(self, user_service, db_session, sample_user, github_user_data):
        """Test successful profile update with GitHub data"""
        db_session.query.return_value.filter.return_value.first.return_value = sample_user
        
        # Update GitHub data
        github_user_data.login = "newusername"
        github_user_data.bio = "Updated bio"
        
        result = user_service.update_profile(1, github_user_data)
        
        # Verify profile was updated
        assert sample_user.github_username == "newusername"
        assert sample_user.bio == "Updated bio"
        db_session.commit.assert_called_once()
    
    def test_update_profile_user_not_found(self, user_service, db_session, github_user_data):
        """Test profile update when user doesn't exist"""
        db_session.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            user_service.update_profile(999, github_user_data)
        
        assert exc_info.value.status_code == 404


class TestUserServiceStatistics:
    """Test suite for user statistics calculation"""
    
    def test_get_user_stats_without_cache(self, user_service, db_session, sample_user, redis_client):
        """
        Test statistics calculation without cache
        Requirement: 6.1
        """
        # Mock the helper methods directly instead of complex query mocking
        with patch.object(user_service, 'get_user_by_id', return_value=sample_user), \
             patch.object(user_service, '_calculate_contributions_by_language', return_value={"Python": 3, "JavaScript": 2}), \
             patch.object(user_service, '_calculate_contributions_by_repo', return_value={"owner/repo1": 4, "owner/repo2": 1}), \
             patch.object(user_service, '_get_recent_contributions', return_value=[]):
            
            # Mock contributions query
            mock_contributions = [
                Mock(id=1, user_id=1, issue_id=1, status="merged"),
                Mock(id=2, user_id=1, issue_id=2, status="submitted"),
                Mock(id=3, user_id=1, issue_id=3, status="merged")
            ]
            
            db_session.query.return_value.filter.return_value.all.return_value = mock_contributions
            
            # Redis returns no cache
            redis_client.get.return_value = None
            
            # Execute
            result = user_service.get_user_stats(1, use_cache=True)
            
            # Verify result structure
            assert result["user_id"] == 1
            assert result["total_contributions"] == 5
            assert result["total_prs_submitted"] == 3
            assert result["merged_prs"] == 2
            assert result["contributions_by_language"] == {"Python": 3, "JavaScript": 2}
            assert result["contributions_by_repo"] == {"owner/repo1": 4, "owner/repo2": 1}
            assert result["recent_contributions"] == []
            assert "calculated_at" in result
            
            # Verify cache was written
            redis_client.setex.assert_called_once()
    
    def test_get_user_stats_with_cache(self, user_service, db_session, redis_client):
        """Test statistics retrieval from cache"""
        cached_stats = {
            "user_id": 1,
            "total_contributions": 5,
            "total_prs_submitted": 3,
            "merged_prs": 2,
            "contributions_by_language": {"Python": 2},
            "contributions_by_repo": {"owner/repo": 2},
            "recent_contributions": [],
            "calculated_at": datetime.utcnow().isoformat()
        }
        
        redis_client.get.return_value = json.dumps(cached_stats)
        
        result = user_service.get_user_stats(1, use_cache=True)
        
        # Verify cached data was returned
        assert result == cached_stats
        
        # Verify database was not queried
        db_session.query.assert_not_called()
    
    def test_get_user_stats_user_not_found(self, user_service, db_session, redis_client):
        """Test statistics calculation when user doesn't exist"""
        redis_client.get.return_value = None
        db_session.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            user_service.get_user_stats(999)
        
        assert exc_info.value.status_code == 404


class TestUserServiceContributions:
    """Test suite for contribution count management"""
    
    def test_increment_contribution_count(self, user_service, db_session, sample_user, redis_client):
        """Test incrementing user contribution count"""
        db_session.query.return_value.filter.return_value.first.return_value = sample_user
        
        initial_count = sample_user.total_contributions
        
        result = user_service.increment_contribution_count(1)
        
        # Verify count was incremented
        assert sample_user.total_contributions == initial_count + 1
        db_session.commit.assert_called_once()
        
        # Verify cache was invalidated
        redis_client.delete.assert_called_once_with("user_stats:1")
    
    def test_increment_contribution_count_user_not_found(self, user_service, db_session):
        """Test increment when user doesn't exist"""
        db_session.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            user_service.increment_contribution_count(999)
        
        assert exc_info.value.status_code == 404
    
    def test_increment_merged_pr_count(self, user_service, db_session, sample_user, redis_client):
        """Test incrementing user merged PR count"""
        db_session.query.return_value.filter.return_value.first.return_value = sample_user
        
        initial_count = sample_user.merged_prs
        
        result = user_service.increment_merged_pr_count(1)
        
        # Verify count was incremented
        assert sample_user.merged_prs == initial_count + 1
        db_session.commit.assert_called_once()
        
        # Verify cache was invalidated
        redis_client.delete.assert_called_once_with("user_stats:1")
    
    def test_increment_merged_pr_count_user_not_found(self, user_service, db_session):
        """Test increment when user doesn't exist"""
        db_session.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            user_service.increment_merged_pr_count(999)
        
        assert exc_info.value.status_code == 404


class TestUserServiceCaching:
    """Test suite for Redis caching functionality"""
    
    def test_cache_stats_success(self, user_service, redis_client):
        """Test successful statistics caching"""
        stats = {
            "user_id": 1,
            "total_contributions": 5,
            "calculated_at": datetime.utcnow().isoformat()
        }
        
        user_service._cache_stats(1, stats)
        
        # Verify Redis setex was called with correct parameters
        redis_client.setex.assert_called_once()
        call_args = redis_client.setex.call_args[0]
        assert call_args[0] == "user_stats:1"
        assert call_args[1] == UserService.STATS_CACHE_TTL
        assert json.loads(call_args[2]) == stats
    
    def test_cache_stats_redis_failure(self, user_service):
        """Test caching handles Redis failures gracefully"""
        failing_redis = Mock()
        failing_redis.setex.side_effect = Exception("Redis error")
        
        user_service.redis_client = failing_redis
        
        stats = {"user_id": 1}
        
        # Should not raise exception
        user_service._cache_stats(1, stats)
    
    def test_invalidate_cache_success(self, user_service, redis_client):
        """Test successful cache invalidation"""
        user_service._invalidate_stats_cache(1)
        
        redis_client.delete.assert_called_once_with("user_stats:1")
    
    def test_invalidate_cache_redis_failure(self, user_service):
        """Test cache invalidation handles Redis failures gracefully"""
        failing_redis = Mock()
        failing_redis.delete.side_effect = Exception("Redis error")
        
        user_service.redis_client = failing_redis
        
        # Should not raise exception
        user_service._invalidate_stats_cache(1)
    
    def test_get_cached_stats_success(self, user_service, redis_client):
        """Test successful cache retrieval"""
        cached_data = {"user_id": 1, "total_contributions": 5}
        redis_client.get.return_value = json.dumps(cached_data)
        
        result = user_service._get_cached_stats(1)
        
        assert result == cached_data
        redis_client.get.assert_called_once_with("user_stats:1")
    
    def test_get_cached_stats_miss(self, user_service, redis_client):
        """Test cache miss returns None"""
        redis_client.get.return_value = None
        
        result = user_service._get_cached_stats(1)
        
        assert result is None
    
    def test_get_cached_stats_redis_failure(self, user_service):
        """Test cache retrieval handles Redis failures gracefully"""
        failing_redis = Mock()
        failing_redis.get.side_effect = Exception("Redis error")
        
        user_service.redis_client = failing_redis
        
        result = user_service._get_cached_stats(1)
        
        assert result is None


class TestUserServiceWithoutRedis:
    """Test suite for user service without Redis"""
    
    def test_user_service_without_redis(self, db_session):
        """Test user service works without Redis client"""
        user_service = UserService(db_session, redis_client=None)
        
        assert user_service.redis_client is None
        
        # Cache operations should not fail
        user_service._cache_stats(1, {"user_id": 1})
        user_service._invalidate_stats_cache(1)
        result = user_service._get_cached_stats(1)
        
        assert result is None
