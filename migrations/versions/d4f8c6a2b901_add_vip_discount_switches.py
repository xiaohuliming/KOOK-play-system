"""add vip discount switches

Revision ID: d4f8c6a2b901
Revises: a7d3c2f1e4b9
Create Date: 2026-04-18 17:20:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = 'd4f8c6a2b901'
down_revision = 'a7d3c2f1e4b9'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()

    gift_cols = {c.get('name') for c in inspect(bind).get_columns('gifts')}
    if 'vip_discount_enabled' not in gift_cols:
        with op.batch_alter_table('gifts', schema=None) as batch_op:
            batch_op.add_column(sa.Column(
                'vip_discount_enabled',
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            ))

    item_cols = {c.get('name') for c in inspect(bind).get_columns('project_items')}
    if 'vip_discount_enabled' not in item_cols:
        with op.batch_alter_table('project_items', schema=None) as batch_op:
            batch_op.add_column(sa.Column(
                'vip_discount_enabled',
                sa.Boolean(),
                nullable=False,
                server_default=sa.true(),
            ))
        op.execute(
            "UPDATE project_items SET vip_discount_enabled = 0 "
            "WHERE LOWER(COALESCE(project_type, 'normal')) = 'training'"
        )


def downgrade():
    bind = op.get_bind()

    item_cols = {c.get('name') for c in inspect(bind).get_columns('project_items')}
    if 'vip_discount_enabled' in item_cols:
        with op.batch_alter_table('project_items', schema=None) as batch_op:
            batch_op.drop_column('vip_discount_enabled')

    gift_cols = {c.get('name') for c in inspect(bind).get_columns('gifts')}
    if 'vip_discount_enabled' in gift_cols:
        with op.batch_alter_table('gifts', schema=None) as batch_op:
            batch_op.drop_column('vip_discount_enabled')
