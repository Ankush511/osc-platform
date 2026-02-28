import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.services.auth_service import AuthService
from app.models.user import User
from app.schemas.auth import GitHubUserData, TokenResponse
from app.core.security import decode_token


@pytest.fixture
def db_session():
    """Mock database session"""
    return Mock(spec=Session)


@pytest.fixture
def auth_service(db_session):
    """Create auth service instance"""
    return AuthService(db_session)


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
def existing_user():
    """Sample existing user"""
    return User(
        id=1,
        github_username="testuser",
        github_id=12345,
        avatar_url="https://github.com/avatar.jpg",
        email="test@example.com",
        full_name="Test User",
        bio="Test bio",
        location="Test City",
        preferred_languages=[],
        preferred_labels=[],
        total_contributions=0,
        merged_prs=0
    )


class TestAuthService:
    """Test suite for AuthService"""
    
    @pytest.mark.asyncio
    async def test_authenticate_github_user_new_user(self, auth_service, db_session, github_user_data):
        """
        Test authentication creates new user account
        Requirements: 1.1, 1.2
        """
        # Mock GitHub API responses
        with patch.object(auth_service, '_exchange_code_for_token', new_callable=AsyncMock) as mock_exchange, \
             patch.object(auth_service, '_fetch_github_user', new_callable=AsyncMock) as mock_fetch:
            
            mock_exchange.return_value = "github_access_token"
            mock_fetch.return_value = github_user_data
            
            # Mock database query to return no existing user
            db_session.query.return_value.filter.return_value.first.return_value = None
            
            # Execute authentication
            result = await auth_service.authenticate_github_user("test_code")
            
            # Verify result
            assert isinstance(result, TokenResponse)
            assert result.access_token is not None
            assert result.refresh_token is not None
            assert result.token_type == "bearer"
            
            # Verify new user was added to database
            db_session.add.assert_called_once()
            db_session.commit.assert_called()
            
            # Verify token contains correct user data
            payload = decode_token(result.access_token)
            assert payload is not None
            assert payload["github_username"] == "testuser"
            assert payload["github_id"] == 12345
    
    @pytest.mark.asyncio
    async def test_authenticate_github_user_existing_user(self, auth_service, db_session, github_user_data, existing_user):
        """
        Test authentication logs in existing user instead of creating duplicate
        Requirement: 1.4
        """
        # Mock GitHub API responses
        with patch.object(auth_service, '_exchange_code_for_token', new_callable=AsyncMock) as mock_exchange, \
             patch.object(auth_service, '_fetch_github_user', new_callable=AsyncMock) as mock_fetch:
            
            mock_exchange.return_value = "github_access_token"
            mock_fetch.return_value = github_user_data
            
            # Mock database query to return existing user
            db_session.query.return_value.filter.return_value.first.return_value = existing_user
            
            # Execute authentication
            result = await auth_service.authenticate_github_user("test_code")
            
            # Verify result
            assert isinstance(result, TokenResponse)
            assert result.access_token is not None
            
            # Verify no new user was added (existing user was updated)
            db_session.add.assert_not_called()
            db_session.commit.assert_called()
            
            # Verify user profile was updated
            assert existing_user.github_username == github_user_data.login
            assert existing_user.avatar_url == github_user_data.avatar_url
    
    @pytest.mark.asyncio
    async def test_exchange_code_for_token_success(self, auth_service):
        """Test successful OAuth code exchange"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "github_token_123"}
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            
            token = await auth_service._exchange_code_for_token("test_code")
            
            assert token == "github_token_123"
    
    @pytest.mark.asyncio
    async def test_exchange_code_for_token_failure(self, auth_service):
        """Test OAuth code exchange failure"""
        mock_response = Mock()
        mock_response.status_code = 400
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            
            with pytest.raises(HTTPException) as exc_info:
                await auth_service._exchange_code_for_token("invalid_code")
            
            assert exc_info.value.status_code == 400
    
    @pytest.mark.asyncio
    async def test_fetch_github_user_success(self, auth_service, github_user_data):
        """Test successful GitHub user profile fetch"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "login": "testuser",
            "id": 12345,
            "avatar_url": "https://github.com/avatar.jpg",
            "name": "Test User",
            "email": "test@example.com",
            "bio": "Test bio",
            "location": "Test City"
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            result = await auth_service._fetch_github_user("github_token")
            
            assert result.login == "testuser"
            assert result.id == 12345
    
    def test_refresh_token_success(self, auth_service, db_session, existing_user):
        """Test successful token refresh"""
        # Create a valid refresh token
        from app.core.security import create_refresh_token
        refresh_token = create_refresh_token({
            "sub": str(existing_user.id),
            "github_username": existing_user.github_username,
            "github_id": existing_user.github_id
        })
        
        # Mock database query
        db_session.query.return_value.filter.return_value.first.return_value = existing_user
        
        # Execute refresh
        result = auth_service.refresh_token(refresh_token)
        
        # Verify result
        assert isinstance(result, TokenResponse)
        assert result.access_token is not None
        assert result.refresh_token is not None
    
    def test_refresh_token_invalid(self, auth_service):
        """Test token refresh with invalid token"""
        with pytest.raises(HTTPException) as exc_info:
            auth_service.refresh_token("invalid_token")
        
        assert exc_info.value.status_code == 401
    
    def test_validate_token_success(self, auth_service, db_session, existing_user):
        """Test successful token validation"""
        # Create a valid access token
        from app.core.security import create_access_token
        access_token = create_access_token({
            "sub": str(existing_user.id),
            "github_username": existing_user.github_username,
            "github_id": existing_user.github_id
        })
        
        # Mock database query
        db_session.query.return_value.filter.return_value.first.return_value = existing_user
        
        # Execute validation
        result = auth_service.validate_token(access_token)
        
        # Verify result
        assert result == existing_user
    
    def test_validate_token_invalid(self, auth_service):
        """Test token validation with invalid token"""
        with pytest.raises(HTTPException) as exc_info:
            auth_service.validate_token("invalid_token")
        
        assert exc_info.value.status_code == 401
    
    def test_validate_token_expired(self, auth_service):
        """Test token validation with expired token"""
        from app.core.security import create_access_token
        
        # Create an expired token
        expired_token = create_access_token(
            {"sub": "1", "github_username": "test", "github_id": 123},
            expires_delta=timedelta(seconds=-1)
        )
        
        with pytest.raises(HTTPException) as exc_info:
            auth_service.validate_token(expired_token)
        
        assert exc_info.value.status_code == 401
    
    def test_validate_token_user_not_found(self, auth_service, db_session):
        """Test token validation when user doesn't exist"""
        from app.core.security import create_access_token
        access_token = create_access_token({
            "sub": "999",
            "github_username": "nonexistent",
            "github_id": 999
        })
        
        # Mock database query to return None
        db_session.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            auth_service.validate_token(access_token)
        
        assert exc_info.value.status_code == 401
    
    def test_revoke_token(self, auth_service):
        """Test token revocation (placeholder)"""
        result = auth_service.revoke_token("some_token")
        assert result is True
