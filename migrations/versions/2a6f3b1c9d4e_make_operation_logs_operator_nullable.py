"""make operation logs operator nullable

Revision ID: 2a6f3b1c9d4e
Revises: b9f4c7a1e2d3
Create Date: 2026-03-11 20:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2a6f3b1c9d4e'
down_revision = 'b9f4c7a1e2d3'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('operation_logs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('operator_name', sa.String(length=100), nullable=True))
        batch_op.alter_column('operator_id', existing_type=sa.Integer(), nullable=True)

    op.execute(
        """
        UPDATE operation_logs
        SET operator_name = (
            SELECT COALESCE(users.player_nickname, users.kook_username, users.nickname, users.username)
            FROM users
            WHERE users.id = operation_logs.operator_id
        )
        WHERE operator_name IS NULL
        """
    )


def downgrade():
    op.execute(
        """
        UPDATE operation_logs
        SET operator_id = (
            SELECT id
            FROM users
            ORDER BY CASE WHEN role IN ('admin', 'superadmin') THEN 0 ELSE 1 END, id
            LIMIT 1
        )
        WHERE operator_id IS NULL
        """
    )

    with op.batch_alter_table('operation_logs', schema=None) as batch_op:
        batch_op.alter_column('operator_id', existing_type=sa.Integer(), nullable=False)
        batch_op.drop_column('operator_name')
