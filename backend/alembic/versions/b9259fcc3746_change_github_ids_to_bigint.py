"""change_github_ids_to_bigint

Revision ID: b9259fcc3746
Revises: a98420c5365f
Create Date: 2026-03-03
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'b9259fcc3746'
down_revision: Union[str, None] = 'a98420c5365f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('issues', 'github_issue_id', type_=sa.BigInteger(), existing_type=sa.Integer())
    op.alter_column('repositories', 'github_repo_id', type_=sa.BigInteger(), existing_type=sa.Integer())


def downgrade() -> None:
    op.alter_column('issues', 'github_issue_id', type_=sa.Integer(), existing_type=sa.BigInteger())
    op.alter_column('repositories', 'github_repo_id', type_=sa.Integer(), existing_type=sa.BigInteger())
