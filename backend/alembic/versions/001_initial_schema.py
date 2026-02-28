"""Initial schema with users, repositories, issues, and contributions

Revision ID: 001
Revises: 
Create Date: 2024-02-27 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('github_username', sa.String(length=255), nullable=False),
        sa.Column('github_id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('avatar_url', sa.String(length=500), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('preferred_languages', postgresql.ARRAY(sa.String()), nullable=False, server_default='{}'),
        sa.Column('preferred_labels', postgresql.ARRAY(sa.String()), nullable=False, server_default='{}'),
        sa.Column('total_contributions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('merged_prs', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('ix_users_github_username', 'users', ['github_username'], unique=True)
    op.create_index('ix_users_github_id', 'users', ['github_id'], unique=True)

    # Create repositories table
    op.create_table(
        'repositories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('github_repo_id', sa.Integer(), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('primary_language', sa.String(length=100), nullable=True),
        sa.Column('topics', postgresql.ARRAY(sa.String()), nullable=False, server_default='{}'),
        sa.Column('stars', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('forks', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('ai_summary', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('last_synced', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_repositories_id', 'repositories', ['id'])
    op.create_index('ix_repositories_github_repo_id', 'repositories', ['github_repo_id'], unique=True)
    op.create_index('ix_repositories_full_name', 'repositories', ['full_name'], unique=True)
    op.create_index('ix_repositories_primary_language', 'repositories', ['primary_language'])
    op.create_index('ix_repositories_is_active', 'repositories', ['is_active'])

    # Create issues table
    op.create_table(
        'issues',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('github_issue_id', sa.Integer(), nullable=False),
        sa.Column('repository_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('labels', postgresql.ARRAY(sa.String()), nullable=False, server_default='{}'),
        sa.Column('programming_language', sa.String(length=100), nullable=True),
        sa.Column('difficulty_level', sa.String(length=50), nullable=True),
        sa.Column('ai_explanation', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('AVAILABLE', 'CLAIMED', 'COMPLETED', 'CLOSED', name='issuestatus'), nullable=False, server_default='AVAILABLE'),
        sa.Column('claimed_by', sa.Integer(), nullable=True),
        sa.Column('claimed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('claim_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('github_url', sa.String(length=500), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['repository_id'], ['repositories.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['claimed_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_issues_id', 'issues', ['id'])
    op.create_index('ix_issues_github_issue_id', 'issues', ['github_issue_id'])
    op.create_index('ix_issues_repository_id', 'issues', ['repository_id'])
    op.create_index('ix_issues_programming_language', 'issues', ['programming_language'])
    op.create_index('ix_issues_difficulty_level', 'issues', ['difficulty_level'])
    op.create_index('ix_issues_status', 'issues', ['status'])
    op.create_index('ix_issues_claimed_by', 'issues', ['claimed_by'])
    op.create_index('ix_issues_claim_expires_at', 'issues', ['claim_expires_at'])

    # Create contributions table
    op.create_table(
        'contributions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('issue_id', sa.Integer(), nullable=False),
        sa.Column('pr_url', sa.String(length=500), nullable=False),
        sa.Column('pr_number', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('SUBMITTED', 'MERGED', 'CLOSED', name='contributionstatus'), nullable=False, server_default='SUBMITTED'),
        sa.Column('submitted_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('merged_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('points_earned', sa.Integer(), nullable=False, server_default='0'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['issue_id'], ['issues.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_contributions_id', 'contributions', ['id'])
    op.create_index('ix_contributions_user_id', 'contributions', ['user_id'])
    op.create_index('ix_contributions_issue_id', 'contributions', ['issue_id'])
    op.create_index('ix_contributions_status', 'contributions', ['status'])

    # Create composite indexes for common queries
    op.create_index('ix_issues_status_language', 'issues', ['status', 'programming_language'])
    op.create_index('ix_issues_repository_status', 'issues', ['repository_id', 'status'])
    op.create_index('ix_contributions_user_status', 'contributions', ['user_id', 'status'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index('ix_contributions_user_status', table_name='contributions')
    op.drop_index('ix_issues_repository_status', table_name='issues')
    op.drop_index('ix_issues_status_language', table_name='issues')
    
    op.drop_index('ix_contributions_status', table_name='contributions')
    op.drop_index('ix_contributions_issue_id', table_name='contributions')
    op.drop_index('ix_contributions_user_id', table_name='contributions')
    op.drop_index('ix_contributions_id', table_name='contributions')
    op.drop_table('contributions')
    op.execute('DROP TYPE contributionstatus')
    
    op.drop_index('ix_issues_claim_expires_at', table_name='issues')
    op.drop_index('ix_issues_claimed_by', table_name='issues')
    op.drop_index('ix_issues_status', table_name='issues')
    op.drop_index('ix_issues_difficulty_level', table_name='issues')
    op.drop_index('ix_issues_programming_language', table_name='issues')
    op.drop_index('ix_issues_repository_id', table_name='issues')
    op.drop_index('ix_issues_github_issue_id', table_name='issues')
    op.drop_index('ix_issues_id', table_name='issues')
    op.drop_table('issues')
    op.execute('DROP TYPE issuestatus')
    
    op.drop_index('ix_repositories_is_active', table_name='repositories')
    op.drop_index('ix_repositories_primary_language', table_name='repositories')
    op.drop_index('ix_repositories_full_name', table_name='repositories')
    op.drop_index('ix_repositories_github_repo_id', table_name='repositories')
    op.drop_index('ix_repositories_id', table_name='repositories')
    op.drop_table('repositories')
    
    op.drop_index('ix_users_github_id', table_name='users')
    op.drop_index('ix_users_github_username', table_name='users')
    op.drop_index('ix_users_id', table_name='users')
    op.drop_table('users')
