"""create initiatives table

Revision ID: fa662646d9ff
Revises: 
Create Date: 2024-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fa662646d9ff'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('initiatives',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=120), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('strategic_objective', sa.String(length=255), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='draft'),
        sa.Column('priority', sa.String(length=20), nullable=True, server_default='medium'),
        sa.Column('progress', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('business_case_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('updated_by', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('tags', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_tenant_status', 'initiatives', ['tenant_id', 'status'])
    op.create_index('idx_owner', 'initiatives', ['owner_id'])
    op.create_index('idx_dates', 'initiatives', ['start_date', 'end_date'])


def downgrade():
    op.drop_index('idx_dates', table_name='initiatives')
    op.drop_index('idx_owner', table_name='initiatives')
    op.drop_index('idx_tenant_status', table_name='initiatives')
    op.drop_table('initiatives') 