"""initial

Revision ID: 001_initial
Revises: 
Create Date: 2023-10-27 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('tracking_orders',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('order_name', sa.String(length=50), nullable=False),
    sa.Column('tracking_code', sa.String(length=50), nullable=False),
    sa.Column('last_order_code', sa.String(length=10), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tracking_orders_user_id'), 'tracking_orders', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_tracking_orders_user_id'), table_name='tracking_orders')
    op.drop_table('tracking_orders')
