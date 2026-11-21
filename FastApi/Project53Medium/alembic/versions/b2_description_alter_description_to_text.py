"""Alter description to Text

Revision ID: b2_description
Revises: a2_featured
Create Date: 2026-11-09 14:37:22.090416

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2_description'
down_revision: Union[str, Sequence[str], None] = '85d3a2bf9de6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        'products',
        'description',
        existing_type=sa.String(length=255),
        type_=sa.Text(),
        nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        'products',
        'description',
        existing_type=sa.Text(),
        type_=sa.String(length=255),
        nullable=False,
    )
