"""add identity tags table

Revision ID: 8e1a4d2c9fbb
Revises: 5d9f2a7c1e31
Create Date: 2026-03-08 10:08:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8e1a4d2c9fbb'
down_revision = '5d9f2a7c1e31'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'identity_tags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('exp_multiplier', sa.Numeric(precision=5, scale=2), nullable=False, server_default='1.00'),
        sa.Column('exp_bonus_until', sa.Integer(), nullable=True),
        sa.Column('status', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_identity_tags_name'), 'identity_tags', ['name'], unique=True)
    op.create_index(op.f('ix_identity_tags_status'), 'identity_tags', ['status'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_identity_tags_status'), table_name='identity_tags')
    op.drop_index(op.f('ix_identity_tags_name'), table_name='identity_tags')
    op.drop_table('identity_tags')
