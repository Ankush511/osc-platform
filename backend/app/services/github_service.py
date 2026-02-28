"""
GitHub API integration service with rate limiting and error handling
"""
import httpx
import time
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.schemas.github import (
    GitHubUser,
    GitHubIssue,
    GitHubRepository,
    GitHubPullRequest,
    PRValidation,
    WebhookConfig,
    RateLimitInfo,
    GitHubLabel
)
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class GitHubAPIError(Exception):
    """Base exception for GitHub API errors"""
    pass


class RateLimitExceeded(GitHubAPIError):
    """Raised when GitHub API rate limit is exceeded"""
    pass


class ResourceNotFound(GitHubAPIError):
    """Raised when a GitHub resource is not found"""
    pass


class AuthenticationError(GitHubAPIError):
    """Raised when GitHub authentication fails"""
    pass


class GitHubService:
    """
    GitHub API integration service with rate limiting and error handling.
    
    Implements:
    - User profile fetching
    - Repository and issue retrieval with label filtering
    - Pull request validation
    - Webhook management
    - Rate limit handling
    """
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize GitHub service with optional access token.
        
        Args:
            access_token: GitHub personal access token or OAuth token
        """
        self.access_token = access_token
        self.rate_limit_info: Optional[RateLimitInfo] = None
        self._client: Optional[httpx.AsyncClient] = None
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for GitHub API requests"""
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=30.0,
                follow_redirects=True
            )
        return self._client
    
    async def close(self):
        """Close HTTP client"""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    def _update_rate_limit(self, response: httpx.Response):
        """Update rate limit information from response headers"""
        try:
            self.rate_limit_info = RateLimitInfo(
                limit=int(response.headers.get("X-RateLimit-Limit", 0)),
                remaining=int(response.headers.get("X-RateLimit-Remaining", 0)),
                reset=datetime.fromtimestamp(int(response.headers.get("X-RateLimit-Reset", 0))),
                used=int(response.headers.get("X-RateLimit-Used", 0))
            )
            
            # Log warning if rate limit is low
            if self.rate_limit_info.remaining < 100:
                logger.warning(
                    f"GitHub API rate limit low: {self.rate_limit_info.remaining} remaining, "
                    f"resets at {self.rate_limit_info.reset}"
                )
        except (ValueError, KeyError) as e:
            logger.error(f"Failed to parse rate limit headers: {e}")
    
    async def _check_rate_limit(self):
        """Check if rate limit allows making requests"""
        if self.rate_limit_info and self.rate_limit_info.remaining == 0:
            wait_time = (self.rate_limit_info.reset - datetime.now()).total_seconds()
            if wait_time > 0:
                raise RateLimitExceeded(
                    f"GitHub API rate limit exceeded. Resets in {wait_time:.0f} seconds."
                )
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to GitHub API with error handling.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            params: Query parameters
            json_data: JSON body data
            
        Returns:
            Response data as dictionary
            
        Raises:
            RateLimitExceeded: When rate limit is exceeded
            ResourceNotFound: When resource is not found
            AuthenticationError: When authentication fails
            GitHubAPIError: For other API errors
        """
        await self._check_rate_limit()
        
        client = await self._get_client()
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            response = await client.request(
                method=method,
                url=url,
                headers=self._get_headers(),
                params=params,
                json=json_data
            )
            
            # Update rate limit info
            self._update_rate_limit(response)
            
            # Handle different status codes
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 201:
                return response.json()
            elif response.status_code == 204:
                return {}
            elif response.status_code == 401:
                raise AuthenticationError("GitHub authentication failed. Invalid or expired token.")
            elif response.status_code == 403:
                if "rate limit" in response.text.lower():
                    raise RateLimitExceeded("GitHub API rate limit exceeded.")
                raise GitHubAPIError(f"GitHub API forbidden: {response.text}")
            elif response.status_code == 404:
                raise ResourceNotFound(f"GitHub resource not found: {endpoint}")
            elif response.status_code == 422:
                raise GitHubAPIError(f"GitHub API validation error: {response.text}")
            else:
                raise GitHubAPIError(
                    f"GitHub API error: {response.status_code} - {response.text}"
                )
                
        except httpx.TimeoutException:
            raise GitHubAPIError("GitHub API request timed out")
        except httpx.RequestError as e:
            raise GitHubAPIError(f"GitHub API request failed: {str(e)}")

    
    async def fetch_user_profile(self, token: Optional[str] = None) -> GitHubUser:
        """
        Fetch GitHub user profile data.
        
        Args:
            token: Optional GitHub token (uses instance token if not provided)
            
        Returns:
            GitHubUser object with user profile data
            
        Raises:
            AuthenticationError: If authentication fails
            GitHubAPIError: For other API errors
        """
        # Use provided token or instance token
        original_token = self.access_token
        if token:
            self.access_token = token
        
        try:
            data = await self._make_request("GET", "/user")
            return GitHubUser(**data)
        finally:
            # Restore original token
            self.access_token = original_token
    
    async def fetch_repository_issues(
        self,
        repo: str,
        labels: Optional[List[str]] = None,
        state: str = "open",
        per_page: int = 100
    ) -> List[GitHubIssue]:
        """
        Fetch issues from a GitHub repository with optional label filtering.
        
        Args:
            repo: Repository in format "owner/repo"
            labels: List of labels to filter by (e.g., ["good first issue", "help wanted"])
            state: Issue state ("open", "closed", "all")
            per_page: Number of issues per page (max 100)
            
        Returns:
            List of GitHubIssue objects
            
        Raises:
            ResourceNotFound: If repository is not found
            GitHubAPIError: For other API errors
        """
        params = {
            "state": state,
            "per_page": min(per_page, 100),
            "sort": "created",
            "direction": "desc"
        }
        
        # Add label filtering if provided
        if labels:
            params["labels"] = ",".join(labels)
        
        endpoint = f"/repos/{repo}/issues"
        
        try:
            data = await self._make_request("GET", endpoint, params=params)
            
            # Filter out pull requests (GitHub API returns PRs as issues)
            issues = []
            for item in data:
                if "pull_request" not in item:
                    # Parse labels
                    parsed_labels = [
                        GitHubLabel(
                            name=label["name"],
                            color=label["color"],
                            description=label.get("description")
                        )
                        for label in item.get("labels", [])
                    ]
                    item["labels"] = parsed_labels
                    issues.append(GitHubIssue(**item))
            
            logger.info(f"Fetched {len(issues)} issues from {repo}")
            return issues
            
        except Exception as e:
            logger.error(f"Failed to fetch issues from {repo}: {str(e)}")
            raise
    
    async def get_repository_info(self, repo: str) -> GitHubRepository:
        """
        Get repository information.
        
        Args:
            repo: Repository in format "owner/repo"
            
        Returns:
            GitHubRepository object with repository data
            
        Raises:
            ResourceNotFound: If repository is not found
            GitHubAPIError: For other API errors
        """
        endpoint = f"/repos/{repo}"
        
        try:
            data = await self._make_request("GET", endpoint)
            return GitHubRepository(**data)
        except Exception as e:
            logger.error(f"Failed to fetch repository info for {repo}: {str(e)}")
            raise
    
    async def validate_pull_request(
        self,
        pr_url: str,
        expected_user: str
    ) -> PRValidation:
        """
        Validate a pull request and check if it's created by the expected user.
        
        Args:
            pr_url: Full GitHub PR URL (e.g., https://github.com/owner/repo/pull/123)
            expected_user: Expected GitHub username of PR author
            
        Returns:
            PRValidation object with validation results
            
        Raises:
            GitHubAPIError: For API errors
        """
        try:
            # Parse PR URL to extract owner, repo, and PR number
            # Expected format: https://github.com/owner/repo/pull/123
            parts = pr_url.rstrip("/").split("/")
            if len(parts) < 7 or parts[5] != "pull":
                return PRValidation(
                    is_valid=False,
                    pr_number=0,
                    pr_url=pr_url,
                    author="",
                    is_merged=False,
                    error_message="Invalid PR URL format"
                )
            
            owner = parts[3]
            repo_name = parts[4]
            pr_number = int(parts[6])
            
            # Fetch PR data
            endpoint = f"/repos/{owner}/{repo_name}/pulls/{pr_number}"
            data = await self._make_request("GET", endpoint)
            
            pr = GitHubPullRequest(**data)
            author = pr.user.get("login", "")
            
            # Validate author
            is_valid = author.lower() == expected_user.lower()
            
            # Try to extract linked issue from PR body
            linked_issue = None
            if pr.body:
                # Look for common patterns: "Fixes #123", "Closes #123", etc.
                import re
                issue_patterns = [
                    r"(?:fix|fixes|fixed|close|closes|closed|resolve|resolves|resolved)\s+#(\d+)",
                    r"#(\d+)"
                ]
                for pattern in issue_patterns:
                    match = re.search(pattern, pr.body, re.IGNORECASE)
                    if match:
                        linked_issue = int(match.group(1))
                        break
            
            error_message = None
            if not is_valid:
                error_message = f"PR author '{author}' does not match expected user '{expected_user}'"
            
            return PRValidation(
                is_valid=is_valid,
                pr_number=pr_number,
                pr_url=pr_url,
                author=author,
                is_merged=pr.merged,
                linked_issue=linked_issue,
                error_message=error_message
            )
            
        except ResourceNotFound:
            return PRValidation(
                is_valid=False,
                pr_number=0,
                pr_url=pr_url,
                author="",
                is_merged=False,
                error_message="Pull request not found"
            )
        except ValueError as e:
            return PRValidation(
                is_valid=False,
                pr_number=0,
                pr_url=pr_url,
                author="",
                is_merged=False,
                error_message=f"Invalid PR URL: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Failed to validate PR {pr_url}: {str(e)}")
            return PRValidation(
                is_valid=False,
                pr_number=0,
                pr_url=pr_url,
                author="",
                is_merged=False,
                error_message=f"Validation error: {str(e)}"
            )
    
    async def setup_webhooks(
        self,
        repo: str,
        webhook_url: str,
        events: Optional[List[str]] = None
    ) -> bool:
        """
        Setup GitHub webhooks for a repository.
        
        Args:
            repo: Repository in format "owner/repo"
            webhook_url: URL to receive webhook events
            events: List of events to subscribe to (default: ["issues", "pull_request"])
            
        Returns:
            True if webhook was created successfully
            
        Raises:
            AuthenticationError: If authentication fails
            GitHubAPIError: For other API errors
        """
        if events is None:
            events = ["issues", "pull_request"]
        
        endpoint = f"/repos/{repo}/hooks"
        
        payload = {
            "name": "web",
            "active": True,
            "events": events,
            "config": {
                "url": webhook_url,
                "content_type": "json",
                "insecure_ssl": "0"
            }
        }
        
        try:
            await self._make_request("POST", endpoint, json_data=payload)
            logger.info(f"Successfully created webhook for {repo}")
            return True
        except Exception as e:
            logger.error(f"Failed to create webhook for {repo}: {str(e)}")
            raise
    
    async def get_issue(self, repo: str, issue_number: int) -> Optional[GitHubIssue]:
        """
        Get a specific issue by number.
        
        Args:
            repo: Repository in format "owner/repo"
            issue_number: Issue number
            
        Returns:
            GitHubIssue object or None if not found
        """
        endpoint = f"/repos/{repo}/issues/{issue_number}"
        
        try:
            data = await self._make_request("GET", endpoint)
            
            # Check if it's a pull request
            if "pull_request" in data:
                return None
            
            # Parse labels
            parsed_labels = [
                GitHubLabel(
                    name=label["name"],
                    color=label["color"],
                    description=label.get("description")
                )
                for label in data.get("labels", [])
            ]
            data["labels"] = parsed_labels
            
            return GitHubIssue(**data)
        except ResourceNotFound:
            return None
        except Exception as e:
            logger.error(f"Failed to fetch issue {repo}#{issue_number}: {str(e)}")
            return None
    
    async def check_issue_status(self, repo: str, issue_number: int) -> Optional[str]:
        """
        Check if an issue is still open.
        
        Args:
            repo: Repository in format "owner/repo"
            issue_number: Issue number
            
        Returns:
            Issue state ("open" or "closed") or None if not found
        """
        issue = await self.get_issue(repo, issue_number)
        return issue.state if issue else None
    
    def get_rate_limit_info(self) -> Optional[RateLimitInfo]:
        """
        Get current rate limit information.
        
        Returns:
            RateLimitInfo object or None if not available
        """
        return self.rate_limit_info
