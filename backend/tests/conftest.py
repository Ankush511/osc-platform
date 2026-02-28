import pytest
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set test environment variables
os.environ["DATABASE_URL"] = "postgresql://test:test@localhost:5432/test_db"
os.environ["REDIS_URL"] = "redis://localhost:6379/1"
os.environ["GITHUB_CLIENT_ID"] = "test_client_id"
os.environ["GITHUB_CLIENT_SECRET"] = "test_client_secret"
os.environ["SECRET_KEY"] = "test_secret_key_for_testing_only"
os.environ["OPENAI_API_KEY"] = "test_openai_key"

# Monkey patch ARRAY to use JSON for SQLite testing BEFORE importing models
import sqlalchemy
from sqlalchemy import JSON as JSON_TYPE
from sqlalchemy.dialects import postgresql

# Store original ARRAY
_original_array = sqlalchemy.ARRAY

# Create a mock ARRAY class that returns JSON
class MockArray:
    def __init__(self, *args, **kwargs):
        pass
    
    def __call__(self, *args, **kwargs):
        return JSON_TYPE()

# Replace ARRAY in both sqlalchemy and postgresql dialect
mock_array_instance = JSON_TYPE()
sqlalchemy.ARRAY = lambda *args, **kwargs: JSON_TYPE()
postgresql.ARRAY = lambda *args, **kwargs: JSON_TYPE()

# Now import SQLAlchemy and models
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.models.user import User
from app.models.repository import Repository
from app.models.issue import Issue, IssueStatus
from app.models.contribution import Contribution, ContributionStatus
from app.core.security import create_access_token


# Create test database engine
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db_session):
    """Create a test user"""
    user = User(
        github_username="testuser",
        github_id=12345,
        email="test@example.com",
        avatar_url="https://example.com/avatar.png",
        full_name="Test User",
        preferred_languages=[],
        preferred_labels=[]
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def second_user(db_session):
    """Create a second test user"""
    user = User(
        github_username="seconduser",
        github_id=67890,
        email="second@example.com",
        avatar_url="https://example.com/avatar2.png",
        full_name="Second User",
        preferred_languages=[],
        preferred_labels=[]
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_user_token(test_user):
    """Create an access token for test user"""
    return create_access_token(data={"sub": str(test_user.id)})


@pytest.fixture
def sample_repository(db_session):
    """Create a sample repository for testing"""
    repo = Repository(
        github_repo_id=12345,
        full_name="test-org/test-repo",
        name="test-repo",
        description="A test repository",
        primary_language="Python",
        topics=["testing", "python"],
        stars=100,
        forks=20,
        is_active=True
    )
    db_session.add(repo)
    db_session.commit()
    db_session.refresh(repo)
    return repo


@pytest.fixture
def sample_issue(db_session, sample_repository):
    """Create a sample issue for testing"""
    issue = Issue(
        github_issue_id=67890,
        repository_id=sample_repository.id,
        title="Add unit tests",
        description="We need unit tests for the authentication module",
        labels=["good first issue", "testing"],
        programming_language="Python",
        status=IssueStatus.AVAILABLE,
        github_url="https://github.com/test-org/test-repo/issues/1"
    )
    db_session.add(issue)
    db_session.commit()
    db_session.refresh(issue)
    return issue


@pytest.fixture
def client(db_session):
    """Create a test client with database session override"""
    from fastapi.testclient import TestClient
    from app.main import app
    from app.api.dependencies import get_db
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()
