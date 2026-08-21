"""adiciona perfil de usuario

Revision ID: c10b9baca88d
Revises: 2531d88c1dfd
Create Date: 2026-08-21 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c10b9baca88d'
down_revision: Union[str, Sequence[str], None] = '2531d88c1dfd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('user_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('foto_perfil_url', sa.String(length=500), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('curso', sa.String(length=120), nullable=True),
        sa.Column('idade', sa.Integer(), nullable=True),
        sa.Column('signo', sa.String(length=20), nullable=True),
        sa.Column('instagram_url', sa.String(length=300), nullable=True),
        sa.Column('linkedin_url', sa.String(length=300), nullable=True),
        sa.Column('atualizado_em', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id'),
    )
    op.create_index(op.f('ix_user_profiles_id'), 'user_profiles', ['id'], unique=False)

    op.create_table('profile_photos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('profile_id', sa.Integer(), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=False),
        sa.Column('ordem', sa.Integer(), nullable=False),
        sa.Column('criado_em', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['profile_id'], ['user_profiles.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_profile_photos_id'), 'profile_photos', ['id'], unique=False)

    op.create_table('photo_comments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('photo_id', sa.Integer(), nullable=False),
        sa.Column('autor_id', sa.Integer(), nullable=False),
        sa.Column('texto', sa.String(length=500), nullable=False),
        sa.Column('criado_em', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['photo_id'], ['profile_photos.id']),
        sa.ForeignKeyConstraint(['autor_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_photo_comments_id'), 'photo_comments', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_photo_comments_id'), table_name='photo_comments')
    op.drop_table('photo_comments')

    op.drop_index(op.f('ix_profile_photos_id'), table_name='profile_photos')
    op.drop_table('profile_photos')

    op.drop_index(op.f('ix_user_profiles_id'), table_name='user_profiles')
    op.drop_table('user_profiles')
