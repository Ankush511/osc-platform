"""
Load testing configuration for the Open Source Contribution Platform API
Run with: locust -f locustfile.py --host=http://localhost:8000
"""

from locust import HttpUser, task, between, SequentialTaskSet
import random
import json


class UserBehavior(SequentialTaskSet):
    """Simulates realistic user behavior patterns"""
    
    def on_start(self):
        """Setup: Authenticate user"""
        # Mock authentication token
        self.token = "mock-test-token"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        self.issue_id = None
    
    @task(1)
    def view_homepage(self):
        """User visits homepage"""
        self.client.get("/")
    
    @task(5)
    def browse_issues(self):
        """User browses available issues"""
        params = {
            "page": random.randint(1, 5),
            "limit": 20,
            "language": random.choice(["", "Python", "JavaScript", "TypeScript", "Go"])
        }
        
        with self.client.get(
            "/api/v1/issues/",
            params=params,
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("items"):
                    # Store an issue ID for later use
                    self.issue_id = data["items"][0]["id"]
                response.success()
            else:
                response.failure(f"Failed to fetch issues: {response.status_code}")
    
    @task(3)
    def view_issue_detail(self):
        """User views issue details"""
        if not self.issue_id:
            self.issue_id = random.randint(1, 100)
        
        with self.client.get(
            f"/api/v1/issues/{self.issue_id}",
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code in [200, 404]:
                response.success()
            else:
                response.failure(f"Unexpected status: {response.status_code}")
    
    @task(2)
    def search_issues(self):
        """User searches for issues"""
        search_terms = ["bug", "feature", "documentation", "test", "refactor"]
        params = {
            "search": random.choice(search_terms),
            "page": 1,
            "limit": 20
        }
        
        self.client.get(
            "/api/v1/issues/",
            params=params,
            headers=self.headers
        )
    
    @task(1)
    def view_user_dashboard(self):
        """User views their dashboard"""
        self.client.get(
            "/api/v1/users/me/stats",
            headers=self.headers
        )
    
    @task(1)
    def get_user_contributions(self):
        """User views their contributions"""
        self.client.get(
            "/api/v1/users/me/contributions",
            headers=self.headers
        )
    
    @task(1)
    def claim_issue(self):
        """User attempts to claim an issue"""
        if not self.issue_id:
            return
        
        with self.client.post(
            f"/api/v1/issues/{self.issue_id}/claim",
            headers=self.headers,
            catch_response=True
        ) as response:
            # Accept both success and already claimed responses
            if response.status_code in [200, 400, 409]:
                response.success()
            else:
                response.failure(f"Unexpected status: {response.status_code}")


class AdminBehavior(SequentialTaskSet):
    """Simulates admin user behavior"""
    
    def on_start(self):
        """Setup: Authenticate admin"""
        self.token = "mock-admin-token"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    @task(3)
    def view_admin_dashboard(self):
        """Admin views dashboard"""
        self.client.get(
            "/api/v1/admin/stats",
            headers=self.headers
        )
    
    @task(2)
    def view_all_users(self):
        """Admin views user list"""
        params = {"page": 1, "limit": 50}
        self.client.get(
            "/api/v1/admin/users",
            params=params,
            headers=self.headers
        )
    
    @task(2)
    def view_all_issues(self):
        """Admin views all issues"""
        params = {"page": 1, "limit": 50}
        self.client.get(
            "/api/v1/admin/issues",
            params=params,
            headers=self.headers
        )
    
    @task(1)
    def sync_repositories(self):
        """Admin triggers repository sync"""
        with self.client.post(
            "/api/v1/admin/sync",
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code in [200, 202]:
                response.success()
            else:
                response.failure(f"Sync failed: {response.status_code}")


class RegularUser(HttpUser):
    """Regular user simulation"""
    tasks = [UserBehavior]
    wait_time = between(1, 5)  # Wait 1-5 seconds between tasks
    weight = 9  # 90% of users are regular users


class AdminUser(HttpUser):
    """Admin user simulation"""
    tasks = [AdminBehavior]
    wait_time = between(2, 8)  # Admins take more time between actions
    weight = 1  # 10% of users are admins


class QuickUser(HttpUser):
    """Quick browsing user - just views issues"""
    wait_time = between(0.5, 2)
    weight = 5  # 50% of regular users are quick browsers
    
    def on_start(self):
        self.token = "mock-test-token"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    @task(10)
    def browse_issues(self):
        """Quick browsing of issues"""
        params = {
            "page": random.randint(1, 3),
            "limit": 20
        }
        self.client.get(
            "/api/v1/issues/",
            params=params,
            headers=self.headers
        )
    
    @task(3)
    def view_issue(self):
        """Quick view of issue detail"""
        issue_id = random.randint(1, 50)
        self.client.get(
            f"/api/v1/issues/{issue_id}",
            headers=self.headers
        )
