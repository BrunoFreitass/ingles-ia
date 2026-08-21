"""adiciona exercicios

Revision ID: e46d973cc4f2
Revises: 795b334c61be
Create Date: 2026-08-21 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e46d973cc4f2'
down_revision: Union[str, Sequence[str], None] = '795b334c61be'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('exercises',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('lesson_id', sa.Integer(), nullable=False),
        sa.Column('ordem', sa.Integer(), nullable=False),
        sa.Column('tipo', sa.String(length=50), nullable=False),
        sa.Column('enunciado', sa.Text(), nullable=True),
        sa.Column('dados_json', sa.Text(), nullable=False),
        sa.Column('resposta_correta_json', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_exercises_id'), 'exercises', ['id'], unique=False)

    op.create_table('exercise_attempts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('exercise_id', sa.Integer(), nullable=False),
        sa.Column('resposta_dada_json', sa.Text(), nullable=False),
        sa.Column('acertou', sa.Boolean(), nullable=False),
        sa.Column('data', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['exercise_id'], ['exercises.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_exercise_attempts_id'), 'exercise_attempts', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_exercise_attempts_id'), table_name='exercise_attempts')
    op.drop_table('exercise_attempts')

    op.drop_index(op.f('ix_exercises_id'), table_name='exercises')
    op.drop_table('exercises')
