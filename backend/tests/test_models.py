"""
Tests for database models and utilities.
Run with: python -m pytest tests/test_models.py -v
Or directly: python tests/test_models.py
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_model_imports():
    """Test that all models can be imported."""
    from app.models import User, Repository, Issue, Contribution
    from app.models.issue import IssueStatus
    from app.models.contribution import ContributionStatus
    assert User is not None
    assert Repository is not None
    assert Issue is not None
    assert Contribution is not None
    assert IssueStatus is not None
    assert ContributionStatus is not None


def test_enum_values():
    """Test that enums have correct values."""
    from app.models.issue import IssueStatus
    from app.models.contribution import ContributionStatus
    
    issue_statuses = [s.value for s in IssueStatus]
    assert issue_statuses == ['available', 'claimed', 'completed', 'closed']
    
    contrib_statuses = [s.value for s in ContributionStatus]
    assert contrib_statuses == ['submitted', 'merged', 'closed']


def test_model_instantiation():
    """Test that models can be instantiated."""
    from app.models import User, Repository, Issue, Contribution
    from app.models.issue import IssueStatus
    from app.models.contribution import ContributionStatus
    
    user = User(
        github_username='testuser',
        github_id=12345,
        avatar_url='https://example.com/avatar.png'
    )
    assert user.github_username == 'testuser'
    assert user.github_id == 12345
    
    repo = Repository(
        github_repo_id=67890,
        full_name='owner/repo',
        name='repo'
    )
    assert repo.full_name == 'owner/repo'
    
    issue = Issue(
        github_issue_id=111,
        repository_id=1,
        title='Test Issue',
        github_url='https://github.com/owner/repo/issues/111',
        status=IssueStatus.AVAILABLE
    )
    assert issue.title == 'Test Issue'
    assert issue.status == IssueStatus.AVAILABLE
    
    contrib = Contribution(
        user_id=1,
        issue_id=1,
        pr_url='https://github.com/owner/repo/pull/1',
        pr_number=1,
        status=ContributionStatus.SUBMITTED
    )
    assert contrib.pr_number == 1
    assert contrib.status == ContributionStatus.SUBMITTED


def test_database_utilities():
    """Test that database utilities can be imported."""
    from app.db import Base, engine, SessionLocal, get_db, init_db, drop_db, reset_db
    assert Base is not None
    assert engine is not None
    assert SessionLocal is not None
    assert get_db is not None
    assert init_db is not None
    assert drop_db is not None
    assert reset_db is not None


def test_model_relationships():
    """Test that model relationships are defined."""
    from app.models import User, Repository, Issue, Contribution
    
    assert hasattr(User, 'contributions')
    assert hasattr(User, 'claimed_issues')
    assert hasattr(Repository, 'issues')
    assert hasattr(Issue, 'repository')
    assert hasattr(Issue, 'claimer')
    assert hasattr(Issue, 'contributions')
    assert hasattr(Contribution, 'user')
    assert hasattr(Contribution, 'issue')


def test_model_fields():
    """Test that models have required fields."""
    from app.models import User, Repository, Issue, Contribution
    
    # User fields
    user_fields = ['github_username', 'github_id', 'avatar_url', 'preferred_languages', 
                  'preferred_labels', 'total_contributions', 'merged_prs']
    for field in user_fields:
        assert hasattr(User, field), f"User missing field: {field}"
    
    # Repository fields
    repo_fields = ['github_repo_id', 'full_name', 'name', 'primary_language', 
                  'topics', 'stars', 'forks', 'ai_summary', 'is_active']
    for field in repo_fields:
        assert hasattr(Repository, field), f"Repository missing field: {field}"
    
    # Issue fields
    issue_fields = ['github_issue_id', 'repository_id', 'title', 'labels', 
                   'programming_language', 'difficulty_level', 'ai_explanation', 
                   'status', 'claimed_by', 'claim_expires_at', 'github_url']
    for field in issue_fields:
        assert hasattr(Issue, field), f"Issue missing field: {field}"
    
    # Contribution fields
    contrib_fields = ['user_id', 'issue_id', 'pr_url', 'pr_number', 
                     'status', 'submitted_at', 'merged_at', 'points_earned']
    for field in contrib_fields:
        assert hasattr(Contribution, field), f"Contribution missing field: {field}"


if __name__ == '__main__':
    """Run tests directly without pytest."""
    print("Running model tests...")
    print("-" * 60)
    
    tests = [
        ("Model imports", test_model_imports),
        ("Enum values", test_enum_values),
        ("Model instantiation", test_model_instantiation),
        ("Model fields", test_model_fields),
        ("Model relationships", test_model_relationships),
        ("Database utilities", test_database_utilities),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            print(f"✓ {name}")
            passed += 1
        except Exception as e:
            print(f"✗ {name}: {e}")
            failed += 1
    
    print("-" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✓ All tests passed!")
        sys.exit(0)
    else:
        print("✗ Some tests failed")
        sys.exit(1)
