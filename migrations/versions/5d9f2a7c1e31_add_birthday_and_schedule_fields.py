"""add birthday and schedule fields

Revision ID: 5d9f2a7c1e31
Revises: 3f6c4a9d1b2e
Create Date: 2026-03-06 22:05:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5d9f2a7c1e31'
down_revision = '3f6c4a9d1b2e'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('birthday', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('birthday_notified_year', sa.Integer(), nullable=True))

    with op.batch_alter_table('broadcast_configs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('schedule_weekday', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('schedule_time', sa.String(length=5), nullable=True))
        batch_op.add_column(sa.Column('mention_role_ids', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('last_sent_at', sa.DateTime(), nullable=True))

    op.execute("UPDATE users SET birthday_notified_year = 0 WHERE birthday_notified_year IS NULL")


def downgrade():
    with op.batch_alter_table('broadcast_configs', schema=None) as batch_op:
        batch_op.drop_column('last_sent_at')
        batch_op.drop_column('mention_role_ids')
        batch_op.drop_column('schedule_time')
        batch_op.drop_column('schedule_weekday')

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('birthday_notified_year')
        batch_op.drop_column('birthday')
