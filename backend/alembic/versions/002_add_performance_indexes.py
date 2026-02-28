"""Add performance indexes

Revision ID: 002_add_performance_indexes
Revises: 5c272fa3c1c3
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_add_performance_indexes'
down_revision = '5c272fa3c1c3'
branch_labels = None
depends_on = None


def upgrade():
    """Add indexes for frequently queried columns to improve performance."""
    
    # Issues table indexes
    op.create_index('idx_issues_status', 'issues', ['status'])
    op.create_index('idx_issues_programming_language', 'issues', ['programming_language'])
    op.create_index('idx_issues_difficulty_level', 'issues', ['difficulty_level'])
    op.create_index('idx_issues_repository_id', 'issues', ['repository_id'])
    op.create_index('idx_issues_claimed_by', 'issues', ['claimed_by'])
    op.create_index('idx_issues_claim_expires_at', 'issues', ['claim_expires_at'])
    op.create_index('idx_issues_created_at', 'issues', ['created_at'])
    
    # Composite index for common query patterns
    op.create_index(
        'idx_issues_status_language',
        'issues',
        ['status', 'programming_language']
    )
    op.create_index(
        'idx_issues_status_difficulty',
        'issues',
        ['status', 'difficulty_level']
    )
    
    # Users table indexes
    op.create_index('idx_users_github_id', 'users', ['github_id'])
    op.create_index('idx_users_github_username', 'users', ['github_username'])
    
    # Contributions table indexes
    op.create_index('idx_contributions_user_id', 'contributions', ['user_id'])
    op.create_index('idx_contributions_issue_id', 'contributions', ['issue_id'])
    op.create_index('idx_contributions_status', 'contributions', ['status'])
    op.create_index('idx_contributions_submitted_at', 'contributions', ['submitted_at'])
    
    # Composite index for user contribution queries
    op.create_index(
        'idx_contributions_user_status',
        'contributions',
        ['user_id', 'status']
    )
    
    # Repositories table indexes
    op.create_index('idx_repositories_is_active', 'repositories', ['is_active'])
    op.create_index('idx_repositories_primary_language', 'repositories', ['primary_language'])
    op.create_index('idx_repositories_last_synced', 'repositories', ['last_synced'])
    
    # User achievements table indexes (if exists)
    op.create_index('idx_user_achievements_user_id', 'user_achievements', ['user_id'])
    op.create_index('idx_user_achievements_achievement_id', 'user_achievements', ['achievement_id'])
    op.create_index('idx_user_achievements_earned_at', 'user_achievements', ['earned_at'])


def downgrade():
    """Remove performance indexes."""
    
    # Issues table indexes
    op.drop_index('idx_issues_status')
    op.drop_index('idx_issues_programming_language')
    op.drop_index('idx_issues_difficulty_level')
    op.drop_index('idx_issues_repository_id')
    op.drop_index('idx_issues_claimed_by')
    op.drop_index('idx_issues_claim_expires_at')
    op.drop_index('idx_issues_created_at')
    op.drop_index('idx_issues_status_language')
    op.drop_index('idx_issues_status_difficulty')
    
    # Users table indexes
    op.drop_index('idx_users_github_id')
    op.drop_index('idx_users_github_username')
    
    # Contributions table indexes
    op.drop_index('idx_contributions_user_id')
    op.drop_index('idx_contributions_issue_id')
    op.drop_index('idx_contributions_status')
    op.drop_index('idx_contributions_submitted_at')
    op.drop_index('idx_contributions_user_status')
    
    # Repositories table indexes
    op.drop_index('idx_repositories_is_active')
    op.drop_index('idx_repositories_primary_language')
    op.drop_index('idx_repositories_last_synced')
    
    # User achievements table indexes
    op.drop_index('idx_user_achievements_user_id')
    op.drop_index('idx_user_achievements_achievement_id')
    op.drop_index('idx_user_achievements_earned_at')
