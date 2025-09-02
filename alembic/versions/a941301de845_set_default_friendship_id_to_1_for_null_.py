"""Set default friendship_id to 1 for null values

Revision ID: a941301de845
Revises: dcb8d0af45c4
Create Date: 2025-08-21 14:42:05.500583
"""

from alembic import op
from sqlalchemy.sql import text
from typing import Sequence, Union

# Identifiants de migration
revision: str = 'a941301de845'
down_revision: Union[str, Sequence[str], None] = 'dcb8d0af45c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    conn = op.get_bind()
    count = conn.execute(text("""
        SELECT COUNT(*) FROM notifications
        WHERE type = 'friend_request' AND friendship_id IS NULL;
    """)).scalar()
    print(f"🔍 Lignes à mettre à jour : {count}")

    if count > 0:
        conn.execute(text("""
            UPDATE notifications
            SET friendship_id = 1
            WHERE type = 'friend_request' AND friendship_id IS NULL;
        """))


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(text("""
        UPDATE notifications
        SET friendship_id = NULL
        WHERE type = 'friend_request' AND friendship_id = 1;
    """))