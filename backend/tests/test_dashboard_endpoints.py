"""
Tests for dashboard endpoints
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from sqlalchemy.orm import Session

from app.main import app
from app.models.user import User
from app.models.repository import Repository
from app.models.issue import Issue, IssueStatus
from app.models.contribution import Contribution, ContributionStatus
from app.services.achievement_service import AchievementService


client = TestClient(app)


class TestDashboardEndpoints:
    """Test dashboard API endpoints"""
    
    def test_get_user_stats(
        self,
        db: Session,
        test_user: User,
        auth_headers: dict
    ):
        """Test getting user statistics"""
        response = client.get(
            "/api/v1/users/me/stats",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "user_id" in data
        assert "total_contributions" in data
        assert "total_prs_submitted" in data
        assert "merged_prs" in data
        assert "contributions_by_language" in data
        assert "contributions_by_repo" in data
        assert "recent_contributions" in data
        assert "calculated_at" in data
    
    def test_get_user_achievements(
        self,
        db: Session,
        test_user: User,
        auth_headers: dict
    ):
        """Test getting user achievements"""
        # Initialize achievements
        service = AchievementService(db)
        service.initialize_achievements()
        
        response = client.get(
            "/api/v1/users/me/achievements",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Verify achievement structure
        achievement = data[0]
        assert "achievement" in achievement
        assert "progress" in achievement
        assert "is_unlocked" in achievement
        assert "percentage" in achievement
        
        # Verify nested achievement details
        assert "id" in achievement["achievement"]
        assert "name" in achievement["achievement"]
        assert "description" in achievement["achievement"]
        assert "badge_icon" in achievement["achievement"]
        assert "category" in achievement["achievement"]
        assert "threshold" in achievement["achievement"]
    
    def test_get_user_dashboard(
        self,
        db: Session,
        test_user: User,
        test_repository: Repository,
        auth_headers: dict
    ):
        """Test getting comprehensive dashboard data"""
        # Initialize achievements
        service = AchievementService(db)
        service.initialize_achievements()
        
        # Create some contributions
        for i in range(3):
            issue = Issue(
                github_issue_id=5000 + i,
                repository_id=test_repository.id,
                title=f"Dashboard Test Issue {i}",
                description="Test description",
                programming_language="Python",
                difficulty_level="easy",
                status=IssueStatus.COMPLETED,
                github_url=f"https://github.com/test/repo/issues/{i}"
            )
            db.add(issue)
            db.flush()
            
            contribution = Contribution(
                user_id=test_user.id,
                issue_id=issue.id,
                pr_url=f"https://github.com/test/repo/pull/{i}",
                pr_number=i,
                status=ContributionStatus.MERGED,
                merged_at=datetime.utcnow(),
                points_earned=100
            )
            db.add(contribution)
        
        db.commit()
        
        # Award achievements
        service.check_and_award_achievements(test_user.id)
        
        response = client.get(
            "/api/v1/users/me/dashboard",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify top-level structure
        assert "user" in data
        assert "statistics" in data
        assert "achievements" in data
        assert "achievement_stats" in data
        
        # Verify user data
        user_data = data["user"]
        assert user_data["id"] == test_user.id
        assert user_data["github_username"] == test_user.github_username
        
        # Verify statistics
        stats = data["statistics"]
        assert stats["total_contributions"] >= 3
        assert stats["merged_prs"] >= 3
        assert len(stats["recent_contributions"]) > 0
        
        # Verify achievements
        achievements = data["achievements"]
        assert isinstance(achievements, list)
        assert len(achievements) > 0
        
        # Verify achievement stats
        achievement_stats = data["achievement_stats"]
        assert achievement_stats["total_achievements"] > 0
        assert achievement_stats["unlocked_achievements"] > 0
        assert achievement_stats["completion_percentage"] > 0
    
    def test_get_user_stats_with_contributions(
        self,
        db: Session,
        test_user: User,
        test_repository: Repository,
        auth_headers: dict
    ):
        """Test user stats calculation with actual contributions"""
        # Create contributions in different languages
        languages = ["Python", "JavaScript", "TypeScript"]
        
        for i, language in enumerate(languages):
            issue = Issue(
                github_issue_id=6000 + i,
                repository_id=test_repository.id,
                title=f"{language} Issue",
                description="Test description",
                programming_language=language,
                difficulty_level="easy",
                status=IssueStatus.COMPLETED,
                github_url=f"https://github.com/test/repo/issues/{i}"
            )
            db.add(issue)
            db.flush()
            
            contribution = Contribution(
                user_id=test_user.id,
                issue_id=issue.id,
                pr_url=f"https://github.com/test/repo/pull/{i}",
                pr_number=i,
                status=ContributionStatus.MERGED if i < 2 else ContributionStatus.SUBMITTED,
                merged_at=datetime.utcnow() if i < 2 else None,
                points_earned=100 if i < 2 else 10
            )
            db.add(contribution)
        
        db.commit()
        
        response = client.get(
            "/api/v1/users/me/stats",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify counts
        assert data["total_prs_submitted"] == 3
        assert data["merged_prs"] == 2
        
        # Verify language breakdown
        assert "Python" in data["contributions_by_language"]
        assert "JavaScript" in data["contributions_by_language"]
        assert "TypeScript" in data["contributions_by_language"]
        
        # Verify repository breakdown
        assert "test/repo" in data["contributions_by_repo"]
        assert data["contributions_by_repo"]["test/repo"] == 3
    
    def test_get_public_user_stats(
        self,
        db: Session,
        test_user: User
    ):
        """Test getting public user statistics by ID"""
        response = client.get(f"/api/v1/users/{test_user.id}/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["user_id"] == test_user.id
        assert "total_contributions" in data
        assert "total_prs_submitted" in data
        assert "merged_prs" in data
    
    def test_get_public_user_achievements(
        self,
        db: Session,
        test_user: User
    ):
        """Test getting public user achievements by ID"""
        # Initialize achievements
        service = AchievementService(db)
        service.initialize_achievements()
        
        response = client.get(f"/api/v1/users/{test_user.id}/achievements")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_dashboard_unauthorized(self):
        """Test dashboard endpoints require authentication"""
        response = client.get("/api/v1/users/me/dashboard")
        assert response.status_code == 401
        
        response = client.get("/api/v1/users/me/stats")
        assert response.status_code == 401
        
        response = client.get("/api/v1/users/me/achievements")
        assert response.status_code == 401
    
    def test_dashboard_with_no_data(
        self,
        db: Session,
        test_user: User,
        auth_headers: dict
    ):
        """Test dashboard with user who has no contributions"""
        # Initialize achievements
        service = AchievementService(db)
        service.initialize_achievements()
        
        response = client.get(
            "/api/v1/users/me/dashboard",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should still return valid structure with zero values
        assert data["statistics"]["total_contributions"] == 0
        assert data["statistics"]["merged_prs"] == 0
        assert len(data["statistics"]["recent_contributions"]) == 0
        assert len(data["statistics"]["contributions_by_language"]) == 0
        
        # All achievements should be locked
        achievements = data["achievements"]
        unlocked = [a for a in achievements if a["is_unlocked"]]
        assert len(unlocked) == 0


@pytest.fixture
def test_user(db_session: Session) -> User:
    """Create a test user"""
    user = User(
        github_username="dashboarduser",
        github_id=99999,
        email="dashboard@example.com",
        avatar_url="https://example.com/avatar.jpg",
        full_name="Dashboard User",
        total_contributions=0,
        merged_prs=0
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_repository(db_session: Session) -> Repository:
    """Create a test repository"""
    repo = Repository(
        github_repo_id=88888,
        full_name="test/dashboard-repo",
        name="dashboard-repo",
        description="Test repository for dashboard",
        primary_language="Python",
        stars=200,
        forks=20,
        is_active=True
    )
    db.add(repo)
    db.commit()
    db.refresh(repo)
    return repo


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Create authentication headers for test user"""
    # This is a simplified version - in real tests, you'd generate a proper JWT token
    return {
        "Authorization": f"Bearer test_token_for_user_{test_user.id}"
    }
