"""add crown broadcast template to gifts

Revision ID: 9c41d2a7b6ef
Revises: 6bb7f0d3a12c
Create Date: 2026-03-12 10:20:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = '9c41d2a7b6ef'
down_revision = '6bb7f0d3a12c'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    cols = {c.get('name') for c in inspect(bind).get_columns('gifts')}
    if 'crown_broadcast_template' in cols:
        return

    with op.batch_alter_table('gifts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('crown_broadcast_template', sa.Text(), nullable=True))


def downgrade():
    bind = op.get_bind()
    cols = {c.get('name') for c in inspect(bind).get_columns('gifts')}
    if 'crown_broadcast_template' not in cols:
        return

    with op.batch_alter_table('gifts', schema=None) as batch_op:
        batch_op.drop_column('crown_broadcast_template')
