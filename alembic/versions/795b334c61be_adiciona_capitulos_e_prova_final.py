"""adiciona capitulos e prova final

Revision ID: 795b334c61be
Revises: cf774f68e433
Create Date: 2026-08-19 17:05:36.526699

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '795b334c61be'
down_revision: Union[str, Sequence[str], None] = 'cf774f68e433'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('capitulos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ordem', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(length=120), nullable=False),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('nota_minima_prova_final', sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('ordem')
    )
    op.create_index(op.f('ix_capitulos_id'), 'capitulos', ['id'], unique=False)

    # batch mode: funciona tanto no Postgres (produção) quanto no SQLite
    # (dev local), que não suporta ALTER de constraints diretamente.
    with op.batch_alter_table('levels', schema=None) as batch_op:
        batch_op.add_column(sa.Column('capitulo_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_levels_capitulo_id', 'capitulos', ['capitulo_id'], ['id'])

    with op.batch_alter_table('quizzes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('capitulo_id', sa.Integer(), nullable=True))
        batch_op.alter_column('lesson_id', existing_type=sa.INTEGER(), nullable=True)
        batch_op.create_unique_constraint('uq_quizzes_capitulo_id', ['capitulo_id'])
        batch_op.create_foreign_key('fk_quizzes_capitulo_id', 'capitulos', ['capitulo_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('quizzes', schema=None) as batch_op:
        batch_op.drop_constraint('fk_quizzes_capitulo_id', type_='foreignkey')
        batch_op.drop_constraint('uq_quizzes_capitulo_id', type_='unique')
        batch_op.alter_column('lesson_id', existing_type=sa.INTEGER(), nullable=False)
        batch_op.drop_column('capitulo_id')

    with op.batch_alter_table('levels', schema=None) as batch_op:
        batch_op.drop_constraint('fk_levels_capitulo_id', type_='foreignkey')
        batch_op.drop_column('capitulo_id')

    op.drop_index(op.f('ix_capitulos_id'), table_name='capitulos')
    op.drop_table('capitulos')