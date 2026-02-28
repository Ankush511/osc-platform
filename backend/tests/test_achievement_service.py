"""
Tests for achievement service
"""
import pytest
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.repository import Repository
from app.models.issue import Issue, IssueStatus
from app.models.contribution import Contribution, ContributionStatus
from app.models.achievement import Achievement, UserAchievement
from app.services.achievement_service import AchievementService


class TestAchievementService:
    """Test achievement service functionality"""
    
    def test_initialize_achievements(self, db_session: Session):
        """Test initializing predefined achievements"""
        service = AchievementService(db_session)
        achievements = service.initialize_achievements()
        
        # Should create all predefined achievements
        assert len(achievements) > 0
        
        # Verify achievements are in database
        all_achievements = service.get_all_achievements()
        assert len(all_achievements) >= len(AchievementService.ACHIEVEMENTS)
        
        # Verify achievement structure
        first_achievement = all_achievements[0]
        assert first_achievement.name is not None
        assert first_achievement.description is not None
        assert first_achievement.badge_icon is not None
        assert first_achievement.category is not None
        assert first_achievement.threshold > 0
    
    def test_get_user_achievements_no_contributions(self, db_session: Session, test_user: User):
        """Test getting achievements for user with no contributions"""
        service = AchievementService(db_session)
        service.initialize_achievements()
        
        achievements = service.get_user_achievements(test_user.id)
        
        # Should return all achievements with zero progress
        assert len(achievements) > 0
        
        for achievement in achievements:
            assert achievement.progress == 0
            assert achievement.is_unlocked is False
            assert achievement.earned_at is None
            assert achievement.percentage == 0.0
    
    def test_milestone_achievement_first_pr(
        self,
        db: Session,
        test_user: User,
        test_repository: Repository,
        test_issue: Issue
    ):
        """Test milestone achievement for first PR submission"""
        service = AchievementService(db_session)
        service.initialize_achievements()
        
        # Create a contribution
        contribution = Contribution(
            user_id=test_user.id,
            issue_id=test_issue.id,
            pr_url="https://github.com/test/repo/pull/1",
            pr_number=1,
            status=ContributionStatus.SUBMITTED,
            points_earned=10
        )
        db.add(contribution)
        db.commit()
        
        # Check and award achievements
        newly_awarded = service.check_and_award_achievements(test_user.id)
        
        # Should award "First Steps" achievement
        assert len(newly_awarded) > 0
        first_steps = next((a for a in newly_awarded if a.name == "First Steps"), None)
        assert first_steps is not None
        
        # Verify achievement is unlocked
        achievements = service.get_user_achievements(test_user.id)
        first_steps_progress = next(
            (a for a in achievements if a.achievement.name == "First Steps"),
            None
        )
        assert first_steps_progress is not None
        assert first_steps_progress.is_unlocked is True
        assert first_steps_progress.progress >= 1
    
    def test_milestone_achievement_first_merge(
        self,
        db: Session,
        test_user: User,
        test_repository: Repository,
        test_issue: Issue
    ):
        """Test milestone achievement for first merged PR"""
        service = AchievementService(db_session)
        service.initialize_achievements()
        
        # Create a merged contribution
        contribution = Contribution(
            user_id=test_user.id,
            issue_id=test_issue.id,
            pr_url="https://github.com/test/repo/pull/1",
            pr_number=1,
            status=ContributionStatus.MERGED,
            merged_at=datetime.utcnow(),
            points_earned=100
        )
        db.add(contribution)
        db.commit()
        
        # Check and award achievements
        newly_awarded = service.check_and_award_achievements(test_user.id)
        
        # Should award both "First Steps" and "Getting Started"
        assert len(newly_awarded) >= 2
        
        achievement_names = [a.name for a in newly_awarded]
        assert "First Steps" in achievement_names
        assert "Getting Started" in achievement_names
    
    def test_milestone_achievement_multiple_prs(
        self,
        db: Session,
        test_user: User,
        test_repository: Repository
    ):
        """Test milestone achievements for multiple PRs"""
        service = AchievementService(db_session)
        service.initialize_achievements()
        
        # Create 5 issues and contributions
        for i in range(5):
            issue = Issue(
                github_issue_id=1000 + i,
                repository_id=test_repository.id,
                title=f"Test Issue {i}",
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
        
        # Check and award achievements
        newly_awarded = service.check_and_award_achievements(test_user.id)
        
        # Should award "Contributor" and "Active Contributor"
        achievement_names = [a.name for a in newly_awarded]
        assert "Contributor" in achievement_names
        assert "Active Contributor" in achievement_names
        
        # Verify progress
        achievements = service.get_user_achievements(test_user.id)
        contributor = next(
            (a for a in achievements if a.achievement.name == "Contributor"),
            None
        )
        assert contributor is not None
        assert contributor.is_unlocked is True
        assert contributor.progress == 5
    
    def test_language_achievement_python(
        self,
        db: Session,
        test_user: User,
        test_repository: Repository
    ):
        """Test language-specific achievement for Python"""
        service = AchievementService(db_session)
        service.initialize_achievements()
        
        # Create 5 Python contributions
        for i in range(5):
            issue = Issue(
                github_issue_id=2000 + i,
                repository_id=test_repository.id,
                title=f"Python Issue {i}",
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
        
        # Check and award achievements
        newly_awarded = service.check_and_award_achievements(test_user.id)
        
        # Should award "Python Pioneer"
        achievement_names = [a.name for a in newly_awarded]
        assert "Python Pioneer" in achievement_names
    
    def test_polyglot_achievement(
        self,
        db: Session,
        test_user: User,
        test_repository: Repository
    ):
        """Test polyglot achievement for multiple languages"""
        service = AchievementService(db_session)
        service.initialize_achievements()
        
        languages = ["Python", "JavaScript", "TypeScript"]
        
        # Create contributions in different languages
        for i, language in enumerate(languages):
            issue = Issue(
                github_issue_id=3000 + i,
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
                status=ContributionStatus.MERGED,
                merged_at=datetime.utcnow(),
                points_earned=100
            )
            db.add(contribution)
        
        db.commit()
        
        # Check and award achievements
        newly_awarded = service.check_and_award_achievements(test_user.id)
        
        # Should award "Polyglot"
        achievement_names = [a.name for a in newly_awarded]
        assert "Polyglot" in achievement_names
        
        # Verify progress
        achievements = service.get_user_achievements(test_user.id)
        polyglot = next(
            (a for a in achievements if a.achievement.name == "Polyglot"),
            None
        )
        assert polyglot is not None
        assert polyglot.is_unlocked is True
        assert polyglot.progress == 3
    
    def test_achievement_progress_tracking(
        self,
        db: Session,
        test_user: User,
        test_repository: Repository,
        test_issue: Issue
    ):
        """Test achievement progress tracking"""
        service = AchievementService(db_session)
        service.initialize_achievements()
        
        # Create 3 contributions (not enough for 5-threshold achievements)
        for i in range(3):
            issue = Issue(
                github_issue_id=4000 + i,
                repository_id=test_repository.id,
                title=f"Test Issue {i}",
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
        
        # Check achievements
        service.check_and_award_achievements(test_user.id)
        
        # Get achievement progress
        achievements = service.get_user_achievements(test_user.id)
        
        # "Contributor" (5 PRs) should be in progress
        contributor = next(
            (a for a in achievements if a.achievement.name == "Contributor"),
            None
        )
        assert contributor is not None
        assert contributor.is_unlocked is False
        assert contributor.progress == 3
        assert contributor.percentage == 60.0  # 3/5 * 100
    
    def test_get_achievement_stats(
        self,
        db: Session,
        test_user: User,
        test_repository: Repository,
        test_issue: Issue
    ):
        """Test getting achievement statistics"""
        service = AchievementService(db_session)
        service.initialize_achievements()
        
        # Create one contribution to unlock some achievements
        contribution = Contribution(
            user_id=test_user.id,
            issue_id=test_issue.id,
            pr_url="https://github.com/test/repo/pull/1",
            pr_number=1,
            status=ContributionStatus.MERGED,
            merged_at=datetime.utcnow(),
            points_earned=100
        )
        db.add(contribution)
        db.commit()
        
        # Award achievements
        service.check_and_award_achievements(test_user.id)
        
        # Get stats
        stats = service.get_achievement_stats(test_user.id)
        
        assert stats["total_achievements"] > 0
        assert stats["unlocked_achievements"] > 0
        assert stats["completion_percentage"] > 0
        assert stats["completion_percentage"] <= 100
    
    def test_get_unlocked_achievements(
        self,
        db: Session,
        test_user: User,
        test_repository: Repository,
        test_issue: Issue
    ):
        """Test getting only unlocked achievements"""
        service = AchievementService(db_session)
        service.initialize_achievements()
        
        # Create a merged contribution
        contribution = Contribution(
            user_id=test_user.id,
            issue_id=test_issue.id,
            pr_url="https://github.com/test/repo/pull/1",
            pr_number=1,
            status=ContributionStatus.MERGED,
            merged_at=datetime.utcnow(),
            points_earned=100
        )
        db.add(contribution)
        db.commit()
        
        # Award achievements
        service.check_and_award_achievements(test_user.id)
        
        # Get unlocked achievements
        unlocked = service.get_unlocked_achievements(test_user.id)
        
        assert len(unlocked) > 0
        for achievement in unlocked:
            assert achievement.is_unlocked is True
            assert achievement.earned_at is not None


@pytest.fixture
def test_user(db_session: Session) -> User:
    """Create a test user"""
    user = User(
        github_username="testuser",
        github_id=12345,
        email="test@example.com",
        avatar_url="https://example.com/avatar.jpg",
        full_name="Test User",
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
        github_repo_id=67890,
        full_name="test/repo",
        name="repo",
        description="Test repository",
        primary_language="Python",
        stars=100,
        forks=10,
        is_active=True
    )
    db.add(repo)
    db.commit()
    db.refresh(repo)
    return repo


@pytest.fixture
def test_issue(db_session: Session, test_repository: Repository) -> Issue:
    """Create a test issue"""
    issue = Issue(
        github_issue_id=999,
        repository_id=test_repository.id,
        title="Test Issue",
        description="Test description",
        programming_language="Python",
        difficulty_level="easy",
        status=IssueStatus.AVAILABLE,
        github_url="https://github.com/test/repo/issues/999"
    )
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue
