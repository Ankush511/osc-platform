"""
Tests for user statistics calculation
"""
import pytest
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.repository import Repository
from app.models.issue import Issue, IssueStatus
from app.models.contribution import Contribution, ContributionStatus
from app.services.user_service import UserService


class TestUserStatistics:
    """Test user statistics calculation"""
    
    def test_calculate_stats_no_contributions(self, db_session: Session, test_user: User):
        """Test statistics for user with no contributions"""
        service = UserService(db_session)
        stats = service.get_user_stats(test_user.id, use_cache=False)
        
        assert stats["user_id"] == test_user.id
        assert stats["total_contributions"] == 0
        assert stats["total_prs_submitted"] == 0
        assert stats["merged_prs"] == 0
        assert len(stats["contributions_by_language"]) == 0
        assert len(stats["contributions_by_repo"]) == 0
        assert len(stats["recent_contributions"]) == 0
    
    def test_calculate_stats_with_contributions(
        self,
        db: Session,
        test_user: User,
        test_repository: Repository
    ):
        """Test statistics calculation with contributions"""
        # Create 5 contributions
        for i in range(5):
            issue = Issue(
                github_issue_id=7000 + i,
                repository_id=test_repository.id,
                title=f"Stats Test Issue {i}",
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
                status=ContributionStatus.MERGED if i < 3 else ContributionStatus.SUBMITTED,
                merged_at=datetime.utcnow() if i < 3 else None,
                points_earned=100 if i < 3 else 10
            )
            db.add(contribution)
        
        # Update user stats
        test_user.total_contributions = 5
        test_user.merged_prs = 3
        db.commit()
        
        service = UserService(db_session)
        stats = service.get_user_stats(test_user.id, use_cache=False)
        
        assert stats["total_contributions"] == 5
        assert stats["total_prs_submitted"] == 5
        assert stats["merged_prs"] == 3
        assert len(stats["recent_contributions"]) == 5
    
    def test_contributions_by_language(
        self,
        db: Session,
        test_user: User,
        test_repository: Repository
    ):
        """Test contributions grouped by language"""
        languages = {
            "Python": 3,
            "JavaScript": 2,
            "TypeScript": 1
        }
        
        issue_id = 8000
        for language, count in languages.items():
            for i in range(count):
                issue = Issue(
                    github_issue_id=issue_id,
                    repository_id=test_repository.id,
                    title=f"{language} Issue {i}",
                    description="Test description",
                    programming_language=language,
                    difficulty_level="easy",
                    status=IssueStatus.COMPLETED,
                    github_url=f"https://github.com/test/repo/issues/{issue_id}"
                )
                db.add(issue)
                db.flush()
                
                contribution = Contribution(
                    user_id=test_user.id,
                    issue_id=issue.id,
                    pr_url=f"https://github.com/test/repo/pull/{issue_id}",
                    pr_number=issue_id,
                    status=ContributionStatus.MERGED,
                    merged_at=datetime.utcnow(),
                    points_earned=100
                )
                db.add(contribution)
                issue_id += 1
        
        db.commit()
        
        service = UserService(db_session)
        stats = service.get_user_stats(test_user.id, use_cache=False)
        
        by_language = stats["contributions_by_language"]
        assert by_language["Python"] == 3
        assert by_language["JavaScript"] == 2
        assert by_language["TypeScript"] == 1
    
    def test_contributions_by_repository(
        self,
        db: Session,
        test_user: User
    ):
        """Test contributions grouped by repository"""
        # Create multiple repositories
        repos = []
        for i in range(3):
            repo = Repository(
                github_repo_id=90000 + i,
                full_name=f"test/repo{i}",
                name=f"repo{i}",
                description=f"Test repository {i}",
                primary_language="Python",
                stars=100,
                forks=10,
                is_active=True
            )
            db.add(repo)
            db.flush()
            repos.append(repo)
        
        # Create contributions across repositories
        issue_id = 9000
        for i, repo in enumerate(repos):
            count = i + 1  # repo0: 1, repo1: 2, repo2: 3
            for j in range(count):
                issue = Issue(
                    github_issue_id=issue_id,
                    repository_id=repo.id,
                    title=f"Issue {j} in {repo.full_name}",
                    description="Test description",
                    programming_language="Python",
                    difficulty_level="easy",
                    status=IssueStatus.COMPLETED,
                    github_url=f"https://github.com/{repo.full_name}/issues/{issue_id}"
                )
                db.add(issue)
                db.flush()
                
                contribution = Contribution(
                    user_id=test_user.id,
                    issue_id=issue.id,
                    pr_url=f"https://github.com/{repo.full_name}/pull/{issue_id}",
                    pr_number=issue_id,
                    status=ContributionStatus.MERGED,
                    merged_at=datetime.utcnow(),
                    points_earned=100
                )
                db.add(contribution)
                issue_id += 1
        
        db.commit()
        
        service = UserService(db_session)
        stats = service.get_user_stats(test_user.id, use_cache=False)
        
        by_repo = stats["contributions_by_repo"]
        assert by_repo["test/repo0"] == 1
        assert by_repo["test/repo1"] == 2
        assert by_repo["test/repo2"] == 3
    
    def test_recent_contributions_limit(
        self,
        db: Session,
        test_user: User,
        test_repository: Repository
    ):
        """Test recent contributions are limited to 10"""
        # Create 15 contributions
        for i in range(15):
            issue = Issue(
                github_issue_id=10000 + i,
                repository_id=test_repository.id,
                title=f"Recent Test Issue {i}",
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
        
        service = UserService(db_session)
        stats = service.get_user_stats(test_user.id, use_cache=False)
        
        # Should only return 10 most recent
        assert len(stats["recent_contributions"]) == 10
    
    def test_recent_contributions_order(
        self,
        db: Session,
        test_user: User,
        test_repository: Repository
    ):
        """Test recent contributions are ordered by submission date"""
        # Create contributions with different timestamps
        contributions = []
        for i in range(5):
            issue = Issue(
                github_issue_id=11000 + i,
                repository_id=test_repository.id,
                title=f"Order Test Issue {i}",
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
            contributions.append(contribution)
        
        db.commit()
        
        service = UserService(db_session)
        stats = service.get_user_stats(test_user.id, use_cache=False)
        
        recent = stats["recent_contributions"]
        
        # Should be ordered by submitted_at descending (most recent first)
        for i in range(len(recent) - 1):
            current_date = datetime.fromisoformat(recent[i]["submitted_at"])
            next_date = datetime.fromisoformat(recent[i + 1]["submitted_at"])
            assert current_date >= next_date
    
    def test_increment_contribution_count(self, db_session: Session, test_user: User):
        """Test incrementing user contribution count"""
        service = UserService(db_session)
        
        initial_count = test_user.total_contributions
        service.increment_contribution_count(test_user.id)
        
        db.refresh(test_user)
        assert test_user.total_contributions == initial_count + 1
    
    def test_increment_merged_pr_count(self, db_session: Session, test_user: User):
        """Test incrementing user merged PR count"""
        service = UserService(db_session)
        
        initial_count = test_user.merged_prs
        service.increment_merged_pr_count(test_user.id)
        
        db.refresh(test_user)
        assert test_user.merged_prs == initial_count + 1
    
    def test_stats_only_count_verified_contributions(
        self,
        db: Session,
        test_user: User,
        test_repository: Repository
    ):
        """Test that statistics only count verified and completed contributions"""
        # Create contributions with different statuses
        statuses = [
            ContributionStatus.SUBMITTED,
            ContributionStatus.MERGED,
            ContributionStatus.CLOSED
        ]
        
        for i, status in enumerate(statuses):
            issue = Issue(
                github_issue_id=12000 + i,
                repository_id=test_repository.id,
                title=f"Status Test Issue {i}",
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
                status=status,
                merged_at=datetime.utcnow() if status == ContributionStatus.MERGED else None,
                points_earned=100 if status == ContributionStatus.MERGED else 10
            )
            db.add(contribution)
        
        db.commit()
        
        service = UserService(db_session)
        stats = service.get_user_stats(test_user.id, use_cache=False)
        
        # All contributions are counted in total
        assert stats["total_prs_submitted"] == 3
        
        # Only merged PRs are counted in merged_prs
        assert stats["merged_prs"] == 1


@pytest.fixture
def test_user(db_session: Session) -> User:
    """Create a test user"""
    user = User(
        github_username="statsuser",
        github_id=77777,
        email="stats@example.com",
        avatar_url="https://example.com/avatar.jpg",
        full_name="Stats User",
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
        github_repo_id=66666,
        full_name="test/stats-repo",
        name="stats-repo",
        description="Test repository for stats",
        primary_language="Python",
        stars=150,
        forks=15,
        is_active=True
    )
    db.add(repo)
    db.commit()
    db.refresh(repo)
    return repo
