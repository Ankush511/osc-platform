import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base
from app.api.dependencies import get_db
from app.models.user import User
from app.schemas.auth import GitHubUserData


# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override the dependency
app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test and drop after"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


class TestAuthEndpoints:
    """Integration tests for authentication endpoints"""
    
    @pytest.mark.asyncio
    async def test_github_callback_new_user(self):
        """
        Test GitHub OAuth callback creates new user
        Requirements: 1.1, 1.2
        """
        github_user_data = GitHubUserData(
            login="newuser",
            id=54321,
            avatar_url="https://github.com/newuser.jpg",
            name="New User",
            email="newuser@example.com",
            bio="New user bio",
            location="New City"
        )
        
        with patch('app.services.auth_service.AuthService._exchange_code_for_token', new_callable=AsyncMock) as mock_exchange, \
             patch('app.services.auth_service.AuthService._fetch_github_user', new_callable=AsyncMock) as mock_fetch:
            
            mock_exchange.return_value = "github_token"
            mock_fetch.return_value = github_user_data
            
            response = client.post(
                "/api/v1/auth/github/callback",
                json={"code": "test_oauth_code"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data
            assert data["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_github_callback_existing_user(self):
        """
        Test GitHub OAuth callback logs in existing user
        Requirement: 1.4
        """
        # Create existing user in database
        db = TestingSessionLocal()
        existing_user = User(
            github_username="existinguser",
            github_id=99999,
            avatar_url="https://github.com/existing.jpg",
            email="existing@example.com",
            full_name="Existing User",
            preferred_languages=[],
            preferred_labels=[],
            total_contributions=5,
            merged_prs=3
        )
        db.add(existing_user)
        db.commit()
        db.close()
        
        github_user_data = GitHubUserData(
            login="existinguser",
            id=99999,
            avatar_url="https://github.com/existing_updated.jpg",
            name="Existing User Updated",
            email="existing@example.com"
        )
        
        with patch('app.services.auth_service.AuthService._exchange_code_for_token', new_callable=AsyncMock) as mock_exchange, \
             patch('app.services.auth_service.AuthService._fetch_github_user', new_callable=AsyncMock) as mock_fetch:
            
            mock_exchange.return_value = "github_token"
            mock_fetch.return_value = github_user_data
            
            response = client.post(
                "/api/v1/auth/github/callback",
                json={"code": "test_oauth_code"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            
            # Verify user stats were preserved
            db = TestingSessionLocal()
            user = db.query(User).filter(User.github_id == 99999).first()
            assert user.total_contributions == 5
            assert user.merged_prs == 3
            db.close()
    
    def test_get_current_user_authenticated(self):
        """Test getting current user info with valid token"""
        # Create user and generate token
        db = TestingSessionLocal()
        user = User(
            github_username="testuser",
            github_id=12345,
            avatar_url="https://github.com/test.jpg",
            email="test@example.com",
            full_name="Test User",
            preferred_languages=["Python", "JavaScript"],
            preferred_labels=["good first issue"],
            total_contributions=0,
            merged_prs=0
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        from app.core.security import create_access_token
        token = create_access_token({
            "sub": str(user.id),
            "github_username": user.github_username,
            "github_id": user.github_id
        })
        db.close()
        
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["github_username"] == "testuser"
        assert data["github_id"] == 12345
        assert data["email"] == "test@example.com"
        assert "Python" in data["preferred_languages"]
    
    def test_get_current_user_unauthenticated(self):
        """Test getting current user info without token"""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == 403  # No credentials provided
    
    def test_get_current_user_invalid_token(self):
        """Test getting current user info with invalid token"""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401
    
    def test_refresh_token_success(self):
        """Test token refresh with valid refresh token"""
        # Create user and generate tokens
        db = TestingSessionLocal()
        user = User(
            github_username="testuser",
            github_id=12345,
            avatar_url="https://github.com/test.jpg",
            email="test@example.com",
            full_name="Test User",
            preferred_languages=[],
            preferred_labels=[],
            total_contributions=0,
            merged_prs=0
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        from app.core.security import create_refresh_token
        refresh_token = create_refresh_token({
            "sub": str(user.id),
            "github_username": user.github_username,
            "github_id": user.github_id
        })
        db.close()
        
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    def test_refresh_token_invalid(self):
        """Test token refresh with invalid refresh token"""
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid_refresh_token"}
        )
        
        assert response.status_code == 401
    
    def test_logout(self):
        """Test logout endpoint"""
        # Create user and generate token
        db = TestingSessionLocal()
        user = User(
            github_username="testuser",
            github_id=12345,
            avatar_url="https://github.com/test.jpg",
            email="test@example.com",
            full_name="Test User",
            preferred_languages=[],
            preferred_labels=[],
            total_contributions=0,
            merged_prs=0
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        from app.core.security import create_access_token
        token = create_access_token({
            "sub": str(user.id),
            "github_username": user.github_username,
            "github_id": user.github_id
        })
        db.close()
        
        response = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
