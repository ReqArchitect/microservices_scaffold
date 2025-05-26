"""Add context IDs for domain decomposition

Revision ID: 3c4d5e6f7g8h
Revises: 
Create Date: 2025-05-22 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '3c4d5e6f7g8h'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Update ApplicationComponent table
    op.add_column('application_component', sa.Column('capability_context_id', sa.Integer(), nullable=True))
    with op.batch_alter_table('application_component') as batch_op:
        batch_op.drop_constraint('fk_application_component_capability_id', type_='foreignkey')
        batch_op.drop_column('capability_id')
    
    # Update ApplicationService table
    op.add_column('application_service', sa.Column('capability_context_id', sa.Integer(), nullable=True))
    with op.batch_alter_table('application_service') as batch_op:
        batch_op.drop_constraint('fk_application_service_capability_id', type_='foreignkey')
        batch_op.drop_column('capability_id')
    
    # Update ApplicationInterface table
    op.add_column('application_interface', sa.Column('course_of_action_context_id', sa.Integer(), nullable=True))
    with op.batch_alter_table('application_interface') as batch_op:
        batch_op.drop_constraint('fk_application_interface_course_of_action_id', type_='foreignkey')
        batch_op.drop_column('course_of_action_id')

def downgrade():
    # Revert ApplicationInterface table changes
    op.add_column('application_interface', sa.Column('course_of_action_id', sa.Integer(), nullable=True))
    op.drop_column('application_interface', 'course_of_action_context_id')
    op.create_foreign_key('fk_application_interface_course_of_action_id', 'application_interface', 'course_of_action', ['course_of_action_id'], ['id'])
    
    # Revert ApplicationService table changes
    op.add_column('application_service', sa.Column('capability_id', sa.Integer(), nullable=True))
    op.drop_column('application_service', 'capability_context_id')
    op.create_foreign_key('fk_application_service_capability_id', 'application_service', 'capability', ['capability_id'], ['id'])
    
    # Revert ApplicationComponent table changes
    op.add_column('application_component', sa.Column('capability_id', sa.Integer(), nullable=True))
    op.drop_column('application_component', 'capability_context_id')
    op.create_foreign_key('fk_application_component_capability_id', 'application_component', 'capability', ['capability_id'], ['id'])
