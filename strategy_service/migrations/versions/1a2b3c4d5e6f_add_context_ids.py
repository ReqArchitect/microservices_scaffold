"""Add context IDs for domain decomposition

Revision ID: 1a2b3c4d5e6f
Revises: 
Create Date: 2025-05-22 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '1a2b3c4d5e6f'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Update Capability table
    op.add_column('capability', sa.Column('business_context_id', sa.Integer(), nullable=True))
    op.add_column('capability', sa.Column('initiative_context_id', sa.Integer(), nullable=True))
    
    # Remove old foreign key constraints
    with op.batch_alter_table('capability') as batch_op:
        batch_op.drop_constraint('fk_capability_business_case_id', type_='foreignkey')
        batch_op.drop_constraint('fk_capability_initiative_id', type_='foreignkey')
        batch_op.drop_column('business_case_id')
        batch_op.drop_column('initiative_id')
    
    # Update CourseOfAction table
    op.add_column('course_of_action', sa.Column('initiative_context_id', sa.Integer(), nullable=True))
    op.add_column('course_of_action', sa.Column('capability_context_id', sa.Integer(), nullable=True))
    
    # Remove old foreign key constraints
    with op.batch_alter_table('course_of_action') as batch_op:
        batch_op.drop_constraint('fk_course_of_action_initiative_id', type_='foreignkey')
        batch_op.drop_constraint('fk_course_of_action_capability_id', type_='foreignkey')
        batch_op.drop_column('initiative_id')
        batch_op.drop_column('capability_id')

def downgrade():
    # Revert CourseOfAction table changes
    op.add_column('course_of_action', sa.Column('capability_id', sa.Integer(), nullable=True))
    op.add_column('course_of_action', sa.Column('initiative_id', sa.Integer(), nullable=True))
    op.drop_column('course_of_action', 'capability_context_id')
    op.drop_column('course_of_action', 'initiative_context_id')
    op.create_foreign_key('fk_course_of_action_capability_id', 'course_of_action', 'capability', ['capability_id'], ['id'])
    op.create_foreign_key('fk_course_of_action_initiative_id', 'course_of_action', 'initiative', ['initiative_id'], ['id'])
    
    # Revert Capability table changes
    op.add_column('capability', sa.Column('business_case_id', sa.Integer(), nullable=True))
    op.add_column('capability', sa.Column('initiative_id', sa.Integer(), nullable=True))
    op.drop_column('capability', 'initiative_context_id')
    op.drop_column('capability', 'business_context_id')
    op.create_foreign_key('fk_capability_business_case_id', 'capability', 'business_case', ['business_case_id'], ['id'])
    op.create_foreign_key('fk_capability_initiative_id', 'capability', 'initiative', ['initiative_id'], ['id'])
