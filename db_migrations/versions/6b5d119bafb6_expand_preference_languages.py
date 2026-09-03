"""expand_preference_languages

Revision ID: 6b5d119bafb6
Revises: 456008a271fb
"""
from typing import Sequence, Union

from alembic import op

revision: str = '6b5d119bafb6'
down_revision: Union[str, Sequence[str], None] = '456008a271fb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE preference DROP CONSTRAINT IF EXISTS ck_preference_language;\nALTER TABLE preference ADD CONSTRAINT ck_preference_language CHECK (language IN ('en', 'fr', 'mg', 'ar', 'hi', 'zh', 'es', 'pt'));")


def downgrade() -> None:
    pass
