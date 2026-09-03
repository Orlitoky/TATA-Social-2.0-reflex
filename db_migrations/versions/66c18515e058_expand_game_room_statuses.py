"""expand_game_room_statuses

Revision ID: 66c18515e058
Revises: 6b5d119bafb6
"""
from typing import Sequence, Union

from alembic import op

revision: str = '66c18515e058'
down_revision: Union[str, Sequence[str], None] = '6b5d119bafb6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE game_room DROP CONSTRAINT IF EXISTS ck_game_room_status;\nALTER TABLE game_room ADD CONSTRAINT ck_game_room_status CHECK (status IN ('open', 'waiting', 'active', 'in_progress', 'finished', 'closed'));")


def downgrade() -> None:
    pass
