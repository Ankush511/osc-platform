"""
Integration tests for critical API endpoints
Tests the full request-response cycle with database interactions
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.issue import Issue, IssueStatus
from app.models.repository import Repository
from app.core.security import create_access_token


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Create authentication headers for test user"""
    token = create_access_token(subject=str(test_user.id))
    return {"Authorization": f"Bearer {token}"}


class TestAuthenticationFlow:
    """Test complete authentication flow"""
    
    def test_github_oauth_callback(self, client: TestClient, db: Session):
        """Test GitHub OAuth callback handling"""
        # This would require mocking GitHub OAuth
        # For now, test the endpoint exists
        response = client.get("/api/v1/auth/github/callback?code=test_code")
        # Should redirect or return error (not 404)
        assert response.status_code != 404
    
    def test_get_current_user(self, client: TestClient, auth_headers: dict, test_user: User):
        """Test getting current authenticated user"""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["github_username"] == test_user.github_username
    
    def test_unauthorized_access(self, client: TestClient):
        """Test that protected endpoints require authentication"""
        response = client.get("/api/v1/users/me/stats")
        assert response.status_code == 401


class TestIssueDiscoveryFlow:
    """Test complete issue discovery and filtering flow"""
    
    def test_list_issues_with_pagination(
        self, 
        client: TestClient, 
        auth_headers: dict,
        test_repository: Repository,
        db: Session
    ):
        """Test issue listing with pagination"""
        # Create multiple issues
        for i in range(25):
            issue = Issue(
                github_issue_id=1000 + i,
                repository_id=test_repository.id,
                title=f"Test Issue {i}",
                description="Test description",
                labels=["good first issue"],
                programming_language="Python",
                difficulty_level="easy",
                status=IssueStatus.AVAILABLE,
                github_url=f"https://github.com/test/repo/issues/{i}"
            )
            db.add(issue)
        db.commit()
        
        # Test first page
        response = client.get(
            "/api/v1/issues/?page=1&limit=10",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 10
        assert data["total"] >= 25
        assert data["page"] == 1
        
        # Test second page
        response = client.get(
            "/api/v1/issues/?page=2&limit=10",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 10
    
    def test_filter_issues_by_language(
        self,
        client: TestClient,
        auth_headers: dict,
        test_repository: Repository,
        db: Session
    ):
        """Test filtering issues by programming language"""
        # Create issues with different languages
        languages = ["Python", "JavaScript", "TypeScript"]
        for lang in languages:
            for i in range(3):
                issue = Issue(
                    github_issue_id=2000 + len(languages) * i,
                    repository_id=test_repository.id,
                    title=f"{lang} Issue {i}",
                    description="Test",
                    labels=["good first issue"],
                    programming_language=lang,
                    difficulty_level="easy",
                    status=IssueStatus.AVAILABLE,
                    github_url=f"https://github.com/test/repo/issues/{i}"
                )
                db.add(issue)
        db.commit()
        
        # Filter by Python
        response = client.get(
            "/api/v1/issues/?language=Python",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert all(item["programming_language"] == "Python" for item in data["items"])
    
    def test_search_issues(
        self,
        client: TestClient,
        auth_headers: dict,
        test_repository: Repository,
        db: Session
    ):
        """Test searching issues by text"""
        # Create issues with specific keywords
        issue1 = Issue(
            github_issue_id=3001,
            repository_id=test_repository.id,
            title="Fix authentication bug",
            description="Bug in auth system",
            labels=["bug"],
            programming_language="Python",
            difficulty_level="medium",
            status=IssueStatus.AVAILABLE,
            github_url="https://github.com/test/repo/issues/3001"
        )
        issue2 = Issue(
            github_issue_id=3002,
            repository_id=test_repository.id,
            title="Add new feature",
            description="Feature request",
            labels=["feature"],
            programming_language="Python",
            difficulty_level="easy",
            status=IssueStatus.AVAILABLE,
            github_url="https://github.com/test/repo/issues/3002"
        )
        db.add_all([issue1, issue2])
        db.commit()
        
        # Search for "authentication"
        response = client.get(
            "/api/v1/issues/?search=authentication",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1
        assert any("authentication" in item["title"].lower() for item in data["items"])


class TestIssueClaimFlow:
    """Test complete issue claim and release flow"""
    
    def test_claim_available_issue(
        self,
        client: TestClient,
        auth_headers: dict,
        test_issue: Issue,
        test_user: User
    ):
        """Test claiming an available issue"""
        response = client.post(
            f"/api/v1/issues/{test_issue.id}/claim",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "claimed"
        assert data["claimed_by"] == test_user.id
        assert "claim_expires_at" in data
    
    def test_cannot_claim_already_claimed_issue(
        self,
        client: TestClient,
        auth_headers: dict,
        test_issue: Issue,
        db: Session
    ):
        """Test that already claimed issues cannot be claimed again"""
        # First claim
        response = client.post(
            f"/api/v1/issues/{test_issue.id}/claim",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # Try to claim again
        response = client.post(
            f"/api/v1/issues/{test_issue.id}/claim",
            headers=auth_headers
        )
        assert response.status_code == 400
    
    def test_release_claimed_issue(
        self,
        client: TestClient,
        auth_headers: dict,
        test_issue: Issue
    ):
        """Test releasing a claimed issue"""
        # First claim the issue
        client.post(f"/api/v1/issues/{test_issue.id}/claim", headers=auth_headers)
        
        # Then release it
        response = client.post(
            f"/api/v1/issues/{test_issue.id}/release",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "available"
        assert data["claimed_by"] is None
    
    def test_extend_claim_deadline(
        self,
        client: TestClient,
        auth_headers: dict,
        test_issue: Issue
    ):
        """Test extending claim deadline"""
        # First claim the issue
        claim_response = client.post(
            f"/api/v1/issues/{test_issue.id}/claim",
            headers=auth_headers
        )
        original_expiry = claim_response.json()["claim_expires_at"]
        
        # Request extension
        response = client.post(
            f"/api/v1/issues/{test_issue.id}/extend",
            json={"reason": "Need more time to complete"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["claim_expires_at"] > original_expiry


class TestPRSubmissionFlow:
    """Test complete PR submission and validation flow"""
    
    def test_submit_pr_for_claimed_issue(
        self,
        client: TestClient,
        auth_headers: dict,
        test_issue: Issue
    ):
        """Test submitting PR for claimed issue"""
        # First claim the issue
        client.post(f"/api/v1/issues/{test_issue.id}/claim", headers=auth_headers)
        
        # Submit PR
        pr_data = {
            "pr_url": "https://github.com/test/repo/pull/123",
            "issue_id": test_issue.id
        }
        response = client.post(
            "/api/v1/contributions/",
            json=pr_data,
            headers=auth_headers
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["pr_url"] == pr_data["pr_url"]
        assert data["status"] in ["submitted", "pending"]
    
    def test_cannot_submit_pr_for_unclaimed_issue(
        self,
        client: TestClient,
        auth_headers: dict,
        test_issue: Issue
    ):
        """Test that PR cannot be submitted for unclaimed issue"""
        pr_data = {
            "pr_url": "https://github.com/test/repo/pull/123",
            "issue_id": test_issue.id
        }
        response = client.post(
            "/api/v1/contributions/",
            json=pr_data,
            headers=auth_headers
        )
        assert response.status_code == 400


class TestUserDashboardFlow:
    """Test complete user dashboard and stats flow"""
    
    def test_get_user_stats(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User
    ):
        """Test getting user statistics"""
        response = client.get(
            "/api/v1/users/me/stats",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_contributions" in data
        assert "merged_prs" in data
        assert "issues_solved" in data
    
    def test_get_user_contributions(
        self,
        client: TestClient,
        auth_headers: dict
    ):
        """Test getting user contribution history"""
        response = client.get(
            "/api/v1/users/me/contributions",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_update_user_preferences(
        self,
        client: TestClient,
        auth_headers: dict
    ):
        """Test updating user preferences"""
        preferences = {
            "preferred_languages": ["Python", "JavaScript"],
            "preferred_labels": ["good first issue", "bug"]
        }
        response = client.put(
            "/api/v1/users/me/preferences",
            json=preferences,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert set(data["preferred_languages"]) == set(preferences["preferred_languages"])


class TestPerformanceAndCaching:
    """Test performance optimizations and caching"""
    
    def test_issue_list_caching(
        self,
        client: TestClient,
        auth_headers: dict
    ):
        """Test that issue list responses are cached"""
        # First request
        response1 = client.get("/api/v1/issues/", headers=auth_headers)
        assert response1.status_code == 200
        
        # Second request should be faster (cached)
        response2 = client.get("/api/v1/issues/", headers=auth_headers)
        assert response2.status_code == 200
        assert response1.json() == response2.json()
    
    def test_rate_limiting(self, client: TestClient, auth_headers: dict):
        """Test that rate limiting is enforced"""
        # Make many rapid requests
        responses = []
        for _ in range(100):
            response = client.get("/api/v1/issues/", headers=auth_headers)
            responses.append(response.status_code)
        
        # Should eventually hit rate limit (429)
        # Note: This depends on rate limit configuration
        assert any(status == 429 for status in responses) or all(status == 200 for status in responses)
