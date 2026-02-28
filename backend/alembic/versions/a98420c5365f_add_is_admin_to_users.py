"""add_is_admin_to_users

Revision ID: a98420c5365f
Revises: 002_add_performance_indexes
Create Date: 2026-02-28 16:23:26.708374

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a98420c5365f'
down_revision = '002_add_performance_indexes'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add is_admin column to users table
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='false'))
    # Create index on is_admin for faster admin queries
    op.create_index(op.f('ix_users_is_admin'), 'users', ['is_admin'], unique=False)


def downgrade() -> None:
    # Drop index and column
    op.drop_index(op.f('ix_users_is_admin'), table_name='users')
    op.drop_column('users', 'is_admin')
