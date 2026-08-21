"""adiciona traducao nas mensagens de conversa

Revision ID: 2531d88c1dfd
Revises: e46d973cc4f2
Create Date: 2026-08-21 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2531d88c1dfd'
down_revision: Union[str, Sequence[str], None] = 'e46d973cc4f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('conversation_messages', schema=None) as batch_op:
        batch_op.add_column(sa.Column('texto_pt', sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('conversation_messages', schema=None) as batch_op:
        batch_op.drop_column('texto_pt')
