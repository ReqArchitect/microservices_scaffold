"""Initial migration

Revision ID: 1a2b3c4d5e6f
Revises: 
Create Date: 2024-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1a2b3c4d5e6f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create tenants table
    op.create_table('tenants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('settings', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=120), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_email_verified', sa.Boolean(), nullable=True),
        sa.Column('email_verification_token', sa.String(length=100), nullable=True),
        sa.Column('password_reset_token', sa.String(length=100), nullable=True),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('preferences', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_email_tenant', 'users', ['email', 'tenant_id'], unique=True)
    op.create_index('idx_tenant_role', 'users', ['tenant_id', 'role'], unique=False)

    # Create user_activities table
    op.create_table('user_activities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('details', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_user_activity', 'user_activities', ['user_id', 'created_at'], unique=False)
    op.create_index('idx_action_created', 'user_activities', ['action', 'created_at'], unique=False)


def downgrade():
    op.drop_table('user_activities')
    op.drop_table('users')
    op.drop_table('tenants') 