"""
Tests for GitHub API integration service
"""
import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime
import httpx
from app.services.github_service import (
    GitHubService,
    GitHubAPIError,
    RateLimitExceeded,
    ResourceNotFound,
    AuthenticationError
)
from app.schemas.github import (
    GitHubUser,
    GitHubIssue,
    GitHubRepository,
    PRValidation,
    RateLimitInfo
)


@pytest.fixture
def github_service():
    """Create a GitHub service instance for testing"""
    return GitHubService(access_token="test_token")


@pytest.fixture
def mock_response():
    """Create a mock HTTP response"""
    response = Mock(spec=httpx.Response)
    response.status_code = 200
    response.headers = {
        "X-RateLimit-Limit": "5000",
        "X-RateLimit-Remaining": "4999",
        "X-RateLimit-Reset": str(int(datetime.now().timestamp()) + 3600),
        "X-RateLimit-Used": "1"
    }
    return response


class TestGitHubServiceInitialization:
    """Test GitHub service initialization"""
    
    def test_init_with_token(self):
        """Test initialization with access token"""
        service = GitHubService(access_token="test_token")
        assert service.access_token == "test_token"
        assert service.rate_limit_info is None
    
    def test_init_without_token(self):
        """Test initialization without access token"""
        service = GitHubService()
        assert service.access_token is None
    
    def test_get_headers_with_token(self):
        """Test headers include authorization when token is provided"""
        service = GitHubService(access_token="test_token")
        headers = service._get_headers()
        assert headers["Authorization"] == "Bearer test_token"
        assert headers["Accept"] == "application/vnd.github+json"
    
    def test_get_headers_without_token(self):
        """Test headers without authorization when no token"""
        service = GitHubService()
        headers = service._get_headers()
        assert "Authorization" not in headers
        assert headers["Accept"] == "application/vnd.github+json"


class TestRateLimitHandling:
    """Test rate limit handling"""
    
    def test_update_rate_limit(self, github_service, mock_response):
        """Test rate limit info is updated from response headers"""
        github_service._update_rate_limit(mock_response)
        
        assert github_service.rate_limit_info is not None
        assert github_service.rate_limit_info.limit == 5000
        assert github_service.rate_limit_info.remaining == 4999
        assert github_service.rate_limit_info.used == 1
    
    @pytest.mark.asyncio
    async def test_check_rate_limit_ok(self, github_service):
        """Test rate limit check passes when limit is available"""
        github_service.rate_limit_info = RateLimitInfo(
            limit=5000,
            remaining=100,
            reset=datetime.now(),
            used=4900
        )
        # Should not raise
        await github_service._check_rate_limit()
    
    @pytest.mark.asyncio
    async def test_check_rate_limit_exceeded(self, github_service):
        """Test rate limit check raises when limit is exceeded"""
        from datetime import timedelta
        github_service.rate_limit_info = RateLimitInfo(
            limit=5000,
            remaining=0,
            reset=datetime.now() + timedelta(hours=1),
            used=5000
        )
        
        with pytest.raises(RateLimitExceeded):
            await github_service._check_rate_limit()


class TestFetchUserProfile:
    """Test fetching user profile"""
    
    @pytest.mark.asyncio
    async def test_fetch_user_profile_success(self, github_service, mock_response):
        """Test successful user profile fetch"""
        mock_data = {
            "login": "testuser",
            "id": 12345,
            "avatar_url": "https://github.com/avatar.jpg",
            "name": "Test User",
            "email": "test@example.com",
            "bio": "Test bio",
            "location": "Test City",
            "public_repos": 10,
            "followers": 5,
            "following": 3
        }
        
        mock_response.json.return_value = mock_data
        
        with patch.object(github_service, '_make_request', return_value=mock_data):
            user = await github_service.fetch_user_profile()
            
            assert isinstance(user, GitHubUser)
            assert user.login == "testuser"
            assert user.id == 12345
            assert user.email == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_fetch_user_profile_with_token(self, github_service):
        """Test user profile fetch with custom token"""
        mock_data = {
            "login": "testuser",
            "id": 12345,
            "avatar_url": "https://github.com/avatar.jpg",
            "public_repos": 0,
            "followers": 0,
            "following": 0
        }
        
        with patch.object(github_service, '_make_request', return_value=mock_data):
            user = await github_service.fetch_user_profile(token="custom_token")
            assert user.login == "testuser"


class TestFetchRepositoryIssues:
    """Test fetching repository issues"""
    
    @pytest.mark.asyncio
    async def test_fetch_issues_success(self, github_service):
        """Test successful issue fetching"""
        mock_data = [
            {
                "id": 1,
                "number": 100,
                "title": "Test Issue",
                "body": "Test body",
                "state": "open",
                "html_url": "https://github.com/owner/repo/issues/100",
                "labels": [
                    {"name": "good first issue", "color": "7057ff", "description": "Good for newcomers"}
                ],
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "user": {"login": "testuser"}
            }
        ]
        
        with patch.object(github_service, '_make_request', return_value=mock_data):
            issues = await github_service.fetch_repository_issues("owner/repo")
            
            assert len(issues) == 1
            assert isinstance(issues[0], GitHubIssue)
            assert issues[0].title == "Test Issue"
            assert issues[0].number == 100
    
    @pytest.mark.asyncio
    async def test_fetch_issues_with_labels(self, github_service):
        """Test issue fetching with label filtering"""
        mock_data = []
        
        with patch.object(github_service, '_make_request', return_value=mock_data) as mock_request:
            await github_service.fetch_repository_issues(
                "owner/repo",
                labels=["good first issue", "help wanted"]
            )
            
            # Verify labels were passed in params
            call_args = mock_request.call_args
            assert "labels" in call_args[1]["params"]
            assert call_args[1]["params"]["labels"] == "good first issue,help wanted"
    
    @pytest.mark.asyncio
    async def test_fetch_issues_filters_pull_requests(self, github_service):
        """Test that pull requests are filtered out from issues"""
        mock_data = [
            {
                "id": 1,
                "number": 100,
                "title": "Test Issue",
                "body": "Test body",
                "state": "open",
                "html_url": "https://github.com/owner/repo/issues/100",
                "labels": [],
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "user": {"login": "testuser"}
            },
            {
                "id": 2,
                "number": 101,
                "title": "Test PR",
                "body": "Test PR body",
                "state": "open",
                "html_url": "https://github.com/owner/repo/pull/101",
                "labels": [],
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "user": {"login": "testuser"},
                "pull_request": {"url": "https://api.github.com/repos/owner/repo/pulls/101"}
            }
        ]
        
        with patch.object(github_service, '_make_request', return_value=mock_data):
            issues = await github_service.fetch_repository_issues("owner/repo")
            
            # Should only return the issue, not the PR
            assert len(issues) == 1
            assert issues[0].number == 100


class TestGetRepositoryInfo:
    """Test getting repository information"""
    
    @pytest.mark.asyncio
    async def test_get_repository_info_success(self, github_service):
        """Test successful repository info fetch"""
        mock_data = {
            "id": 123,
            "name": "test-repo",
            "full_name": "owner/test-repo",
            "description": "Test repository",
            "html_url": "https://github.com/owner/test-repo",
            "language": "Python",
            "stargazers_count": 100,
            "forks_count": 20,
            "topics": ["python", "testing"],
            "default_branch": "main"
        }
        
        with patch.object(github_service, '_make_request', return_value=mock_data):
            repo = await github_service.get_repository_info("owner/test-repo")
            
            assert isinstance(repo, GitHubRepository)
            assert repo.name == "test-repo"
            assert repo.full_name == "owner/test-repo"
            assert repo.language == "Python"
            assert repo.stargazers_count == 100


class TestValidatePullRequest:
    """Test pull request validation"""
    
    @pytest.mark.asyncio
    async def test_validate_pr_success(self, github_service):
        """Test successful PR validation"""
        mock_data = {
            "id": 1,
            "number": 123,
            "title": "Test PR",
            "body": "Fixes #100",
            "state": "open",
            "html_url": "https://github.com/owner/repo/pull/123",
            "user": {"login": "testuser"},
            "head": {},
            "base": {},
            "merged": False,
            "created_at": "2024-01-01T00:00:00Z"
        }
        
        with patch.object(github_service, '_make_request', return_value=mock_data):
            validation = await github_service.validate_pull_request(
                "https://github.com/owner/repo/pull/123",
                "testuser"
            )
            
            assert isinstance(validation, PRValidation)
            assert validation.is_valid is True
            assert validation.pr_number == 123
            assert validation.author == "testuser"
            assert validation.linked_issue == 100
    
    @pytest.mark.asyncio
    async def test_validate_pr_wrong_author(self, github_service):
        """Test PR validation fails for wrong author"""
        mock_data = {
            "id": 1,
            "number": 123,
            "title": "Test PR",
            "body": "Test",
            "state": "open",
            "html_url": "https://github.com/owner/repo/pull/123",
            "user": {"login": "wronguser"},
            "head": {},
            "base": {},
            "merged": False,
            "created_at": "2024-01-01T00:00:00Z"
        }
        
        with patch.object(github_service, '_make_request', return_value=mock_data):
            validation = await github_service.validate_pull_request(
                "https://github.com/owner/repo/pull/123",
                "testuser"
            )
            
            assert validation.is_valid is False
            assert validation.author == "wronguser"
            assert "does not match" in validation.error_message
    
    @pytest.mark.asyncio
    async def test_validate_pr_invalid_url(self, github_service):
        """Test PR validation with invalid URL"""
        validation = await github_service.validate_pull_request(
            "https://invalid-url.com",
            "testuser"
        )
        
        assert validation.is_valid is False
        assert "Invalid PR URL format" in validation.error_message
    
    @pytest.mark.asyncio
    async def test_validate_pr_not_found(self, github_service):
        """Test PR validation when PR doesn't exist"""
        with patch.object(github_service, '_make_request', side_effect=ResourceNotFound("Not found")):
            validation = await github_service.validate_pull_request(
                "https://github.com/owner/repo/pull/999",
                "testuser"
            )
            
            assert validation.is_valid is False
            assert "not found" in validation.error_message.lower()


class TestWebhookSetup:
    """Test webhook setup"""
    
    @pytest.mark.asyncio
    async def test_setup_webhooks_success(self, github_service):
        """Test successful webhook setup"""
        mock_data = {"id": 1, "active": True}
        
        with patch.object(github_service, '_make_request', return_value=mock_data):
            result = await github_service.setup_webhooks(
                "owner/repo",
                "https://example.com/webhook"
            )
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_setup_webhooks_custom_events(self, github_service):
        """Test webhook setup with custom events"""
        mock_data = {"id": 1, "active": True}
        
        with patch.object(github_service, '_make_request', return_value=mock_data) as mock_request:
            await github_service.setup_webhooks(
                "owner/repo",
                "https://example.com/webhook",
                events=["issues", "pull_request", "push"]
            )
            
            # Verify events were passed
            call_args = mock_request.call_args
            assert call_args[1]["json_data"]["events"] == ["issues", "pull_request", "push"]


class TestErrorHandling:
    """Test error handling"""
    
    @pytest.mark.asyncio
    async def test_authentication_error(self, github_service):
        """Test authentication error handling"""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_response.headers = {}
        
        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response
        
        with patch.object(github_service, '_get_client', return_value=mock_client):
            with pytest.raises(AuthenticationError):
                await github_service._make_request("GET", "/user")
    
    @pytest.mark.asyncio
    async def test_resource_not_found(self, github_service):
        """Test resource not found error handling"""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_response.headers = {}
        
        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response
        
        with patch.object(github_service, '_get_client', return_value=mock_client):
            with pytest.raises(ResourceNotFound):
                await github_service._make_request("GET", "/repos/owner/nonexistent")
    
    @pytest.mark.asyncio
    async def test_rate_limit_error(self, github_service):
        """Test rate limit error handling"""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 403
        mock_response.text = "rate limit exceeded"
        mock_response.headers = {}
        
        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response
        
        with patch.object(github_service, '_get_client', return_value=mock_client):
            with pytest.raises(RateLimitExceeded):
                await github_service._make_request("GET", "/user")


class TestIssueStatusCheck:
    """Test issue status checking"""
    
    @pytest.mark.asyncio
    async def test_check_issue_status_open(self, github_service):
        """Test checking status of open issue"""
        mock_issue = GitHubIssue(
            id=1,
            number=100,
            title="Test",
            state="open",
            html_url="https://github.com/owner/repo/issues/100",
            labels=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            user={"login": "test"}
        )
        
        with patch.object(github_service, 'get_issue', return_value=mock_issue):
            status = await github_service.check_issue_status("owner/repo", 100)
            assert status == "open"
    
    @pytest.mark.asyncio
    async def test_check_issue_status_not_found(self, github_service):
        """Test checking status of non-existent issue"""
        with patch.object(github_service, 'get_issue', return_value=None):
            status = await github_service.check_issue_status("owner/repo", 999)
            assert status is None


class TestClientManagement:
    """Test HTTP client management"""
    
    @pytest.mark.asyncio
    async def test_client_creation(self, github_service):
        """Test HTTP client is created on first use"""
        assert github_service._client is None
        client = await github_service._get_client()
        assert client is not None
        assert isinstance(client, httpx.AsyncClient)
    
    @pytest.mark.asyncio
    async def test_client_reuse(self, github_service):
        """Test HTTP client is reused"""
        client1 = await github_service._get_client()
        client2 = await github_service._get_client()
        assert client1 is client2
    
    @pytest.mark.asyncio
    async def test_client_close(self, github_service):
        """Test HTTP client can be closed"""
        await github_service._get_client()
        assert github_service._client is not None
        
        await github_service.close()
        assert github_service._client is None
