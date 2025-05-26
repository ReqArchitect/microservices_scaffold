"""Add user fields

Revision ID: add_user_fields
Revises: 5992bf14fa3b
Create Date: 2024-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = 'add_user_fields'
down_revision = '5992bf14fa3b'
branch_labels = None
depends_on = None

def table_exists(table_name):
    inspector = inspect(op.get_bind())
    return table_name in inspector.get_table_names()

def upgrade():
    # Add new columns to user table
    op.add_column('user', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('user', sa.Column('is_email_verified', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('user', sa.Column('email_verification_token', sa.String(length=100), nullable=True))
    op.add_column('user', sa.Column('password_reset_token', sa.String(length=100), nullable=True))
    op.add_column('user', sa.Column('preferences', sa.JSON(), nullable=True))
    op.add_column('user', sa.Column('last_login', sa.DateTime(), nullable=True))
    op.add_column('user', sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')))
    op.add_column('user', sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')))

    # Add new columns to tenant table
    op.add_column('tenant', sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')))
    op.add_column('tenant', sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')))

    # Create user_activity table only if it doesn't exist
    if not table_exists('user_activity'):
        op.create_table('user_activity',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('action', sa.String(length=50), nullable=False),
            sa.Column('details', sa.JSON(), nullable=True),
            sa.Column('ip_address', sa.String(length=45), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
            sa.PrimaryKeyConstraint('id')
        )

def downgrade():
    # Drop user_activity table if it exists
    if table_exists('user_activity'):
        op.drop_table('user_activity')

    # Drop columns from tenant table
    op.drop_column('tenant', 'updated_at')
    op.drop_column('tenant', 'created_at')

    # Drop columns from user table
    op.drop_column('user', 'updated_at')
    op.drop_column('user', 'created_at')
    op.drop_column('user', 'last_login')
    op.drop_column('user', 'preferences')
    op.drop_column('user', 'password_reset_token')
    op.drop_column('user', 'email_verification_token')
    op.drop_column('user', 'is_email_verified')
    op.drop_column('user', 'is_active') 