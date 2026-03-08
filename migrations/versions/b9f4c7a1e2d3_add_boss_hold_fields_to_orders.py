"""add boss hold fields to orders

Revision ID: b9f4c7a1e2d3
Revises: 8e1a4d2c9fbb
Create Date: 2026-03-08 16:40:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b9f4c7a1e2d3'
down_revision = '8e1a4d2c9fbb'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'orders',
        sa.Column('boss_hold_coin', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0.00')
    )
    op.add_column(
        'orders',
        sa.Column('boss_hold_gift', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0.00')
    )


def downgrade():
    op.drop_column('orders', 'boss_hold_gift')
    op.drop_column('orders', 'boss_hold_coin')
