"""
Integration tests for GitHub service
Tests more complex scenarios and interactions
"""
import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime
from app.services.github_service import GitHubService, RateLimitExceeded
from app.schemas.github import GitHubIssue, GitHubLabel


@pytest.fixture
def github_service():
    """Create a GitHub service instance for testing"""
    return GitHubService(access_token="test_token")


class TestIssueWorkflow:
    """Test complete issue workflow scenarios"""
    
    @pytest.mark.asyncio
    async def test_fetch_and_filter_beginner_issues(self, github_service):
        """Test fetching issues with beginner-friendly labels"""
        mock_issues = [
            {
                "id": 1,
                "number": 100,
                "title": "Add documentation",
                "body": "Need to add docs",
                "state": "open",
                "html_url": "https://github.com/owner/repo/issues/100",
                "labels": [
                    {"name": "good first issue", "color": "7057ff", "description": "Good for newcomers"},
                    {"name": "documentation", "color": "0075ca", "description": "Improvements or additions to documentation"}
                ],
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "user": {"login": "maintainer"}
            },
            {
                "id": 2,
                "number": 101,
                "title": "Fix typo",
                "body": "Simple typo fix",
                "state": "open",
                "html_url": "https://github.com/owner/repo/issues/101",
                "labels": [
                    {"name": "help wanted", "color": "008672", "description": "Extra attention is needed"}
                ],
                "created_at": "2024-01-02T00:00:00Z",
                "updated_at": "2024-01-02T00:00:00Z",
                "user": {"login": "maintainer"}
            }
        ]
        
        with patch.object(github_service, '_make_request', return_value=mock_issues):
            issues = await github_service.fetch_repository_issues(
                "owner/repo",
                labels=["good first issue", "help wanted"]
            )
            
            assert len(issues) == 2
            assert all(isinstance(issue, GitHubIssue) for issue in issues)
            
            # Check first issue has correct labels
            first_issue = issues[0]
            label_names = [label.name for label in first_issue.labels]
            assert "good first issue" in label_names
    
    @pytest.mark.asyncio
    async def test_check_multiple_issues_status(self, github_service):
        """Test checking status of multiple issues"""
        issue_data = {
            100: {"state": "open"},
            101: {"state": "closed"},
            102: None  # Not found
        }
        
        async def mock_get_issue(repo, issue_number):
            data = issue_data.get(issue_number)
            if data is None:
                return None
            if data["state"] == "open":
                return GitHubIssue(
                    id=issue_number,
                    number=issue_number,
                    title="Test",
                    state="open",
                    html_url=f"https://github.com/{repo}/issues/{issue_number}",
                    labels=[],
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    user={"login": "test"}
                )
            return None
        
        with patch.object(github_service, 'get_issue', side_effect=mock_get_issue):
            status_100 = await github_service.check_issue_status("owner/repo", 100)
            status_101 = await github_service.check_issue_status("owner/repo", 101)
            status_102 = await github_service.check_issue_status("owner/repo", 102)
            
            assert status_100 == "open"
            assert status_101 is None
            assert status_102 is None


class TestPRValidationWorkflow:
    """Test PR validation workflow scenarios"""
    
    @pytest.mark.asyncio
    async def test_validate_pr_with_issue_link(self, github_service):
        """Test PR validation extracts linked issue"""
        pr_bodies = [
            ("Fixes #100", 100),
            ("Closes #200", 200),
            ("Resolves #300", 300),
            ("This PR fixes #400 and improves performance", 400),
            ("Related to #500", 500)
        ]
        
        for body, expected_issue in pr_bodies:
            mock_data = {
                "id": 1,
                "number": 123,
                "title": "Test PR",
                "body": body,
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
                
                assert validation.is_valid is True
                assert validation.linked_issue == expected_issue
    
    @pytest.mark.asyncio
    async def test_validate_merged_pr(self, github_service):
        """Test validation of merged PR"""
        mock_data = {
            "id": 1,
            "number": 123,
            "title": "Test PR",
            "body": "Fixes #100",
            "state": "closed",
            "html_url": "https://github.com/owner/repo/pull/123",
            "user": {"login": "testuser"},
            "head": {},
            "base": {},
            "merged": True,
            "merged_at": "2024-01-02T00:00:00Z",
            "created_at": "2024-01-01T00:00:00Z"
        }
        
        with patch.object(github_service, '_make_request', return_value=mock_data):
            validation = await github_service.validate_pull_request(
                "https://github.com/owner/repo/pull/123",
                "testuser"
            )
            
            assert validation.is_valid is True
            assert validation.is_merged is True
            assert validation.linked_issue == 100


class TestRateLimitScenarios:
    """Test rate limit handling scenarios"""
    
    @pytest.mark.asyncio
    async def test_rate_limit_recovery(self, github_service):
        """Test that service can recover after rate limit"""
        from datetime import timedelta
        from app.schemas.github import RateLimitInfo
        
        # Set rate limit to exceeded
        github_service.rate_limit_info = RateLimitInfo(
            limit=5000,
            remaining=0,
            reset=datetime.now() + timedelta(hours=1),
            used=5000
        )
        
        # Should raise rate limit error
        with pytest.raises(RateLimitExceeded):
            await github_service._check_rate_limit()
        
        # Simulate rate limit reset
        github_service.rate_limit_info = RateLimitInfo(
            limit=5000,
            remaining=5000,
            reset=datetime.now() + timedelta(hours=1),
            used=0
        )
        
        # Should not raise now
        await github_service._check_rate_limit()


class TestMultipleRepositories:
    """Test handling multiple repositories"""
    
    @pytest.mark.asyncio
    async def test_fetch_issues_from_multiple_repos(self, github_service):
        """Test fetching issues from multiple repositories"""
        repos = ["owner1/repo1", "owner2/repo2", "owner3/repo3"]
        
        async def mock_fetch_issues(repo, labels=None, state="open", per_page=100):
            # Return different number of issues for each repo
            repo_num = int(repo.split("repo")[1])
            return [
                GitHubIssue(
                    id=i,
                    number=i,
                    title=f"Issue {i} from {repo}",
                    state="open",
                    html_url=f"https://github.com/{repo}/issues/{i}",
                    labels=[],
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    user={"login": "test"}
                )
                for i in range(repo_num)
            ]
        
        all_issues = []
        for repo in repos:
            with patch.object(github_service, 'fetch_repository_issues', side_effect=mock_fetch_issues):
                issues = await github_service.fetch_repository_issues(repo)
                all_issues.extend(issues)
        
        # Should have fetched issues from all repos
        assert len(all_issues) > 0


class TestErrorRecovery:
    """Test error recovery scenarios"""
    
    @pytest.mark.asyncio
    async def test_continue_after_not_found_error(self, github_service):
        """Test service continues working after not found error"""
        # First request fails with not found
        with patch.object(github_service, '_make_request', side_effect=Exception("Not found")):
            with pytest.raises(Exception):
                await github_service.get_repository_info("owner/nonexistent")
        
        # Second request should work
        mock_data = {
            "id": 123,
            "name": "test-repo",
            "full_name": "owner/test-repo",
            "description": "Test",
            "html_url": "https://github.com/owner/test-repo",
            "language": "Python",
            "stargazers_count": 100,
            "forks_count": 20,
            "topics": [],
            "default_branch": "main"
        }
        
        with patch.object(github_service, '_make_request', return_value=mock_data):
            repo = await github_service.get_repository_info("owner/test-repo")
            assert repo.name == "test-repo"


class TestWebhookManagement:
    """Test webhook management scenarios"""
    
    @pytest.mark.asyncio
    async def test_setup_webhooks_for_multiple_repos(self, github_service):
        """Test setting up webhooks for multiple repositories"""
        repos = ["owner1/repo1", "owner2/repo2"]
        webhook_url = "https://example.com/webhook"
        
        mock_data = {"id": 1, "active": True}
        
        results = []
        for repo in repos:
            with patch.object(github_service, '_make_request', return_value=mock_data):
                result = await github_service.setup_webhooks(repo, webhook_url)
                results.append(result)
        
        assert all(results)
        assert len(results) == len(repos)


class TestConcurrentRequests:
    """Test handling concurrent requests"""
    
    @pytest.mark.asyncio
    async def test_multiple_concurrent_user_fetches(self, github_service):
        """Test fetching multiple user profiles concurrently"""
        import asyncio
        
        mock_data = {
            "login": "testuser",
            "id": 12345,
            "avatar_url": "https://github.com/avatar.jpg",
            "public_repos": 10,
            "followers": 5,
            "following": 3
        }
        
        with patch.object(github_service, '_make_request', return_value=mock_data):
            # Fetch user profile multiple times concurrently
            tasks = [github_service.fetch_user_profile() for _ in range(5)]
            users = await asyncio.gather(*tasks)
            
            assert len(users) == 5
            assert all(user.login == "testuser" for user in users)
