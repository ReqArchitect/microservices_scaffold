"""Add context IDs for domain decomposition

Revision ID: 2b3c4d5e6f7g
Revises: 
Create Date: 2025-05-22 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2b3c4d5e6f7g'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Update BusinessActor table
    with op.batch_alter_table('business_actor') as batch_op:
        batch_op.add_column(sa.Column('initiative_context_id', sa.Integer(), nullable=True))
        batch_op.drop_constraint('fk_business_actor_initiative_id', type_='foreignkey')
        batch_op.drop_column('initiative_id')
    
    # Update BusinessProcess table
    with op.batch_alter_table('business_process') as batch_op:
        batch_op.add_column(sa.Column('initiative_context_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('kpi_context_id', sa.Integer(), nullable=True))
        batch_op.drop_constraint('fk_business_process_initiative_id', type_='foreignkey')
        batch_op.drop_constraint('fk_business_process_kpi_id', type_='foreignkey')
        batch_op.drop_column('initiative_id')
        batch_op.drop_column('kpi_id')

def downgrade():
    # Revert BusinessProcess table changes
    op.add_column('business_process', sa.Column('kpi_id', sa.Integer(), nullable=True))
    op.add_column('business_process', sa.Column('initiative_id', sa.Integer(), nullable=True))
    op.drop_column('business_process', 'kpi_context_id')
    op.drop_column('business_process', 'initiative_context_id')
    op.create_foreign_key('fk_business_process_kpi_id', 'business_process', 'kpi', ['kpi_id'], ['id'])
    op.create_foreign_key('fk_business_process_initiative_id', 'business_process', 'initiative', ['initiative_id'], ['id'])
    
    # Revert BusinessActor table changes
    op.add_column('business_actor', sa.Column('initiative_id', sa.Integer(), nullable=True))
    op.drop_column('business_actor', 'initiative_context_id')
    op.create_foreign_key('fk_business_actor_initiative_id', 'business_actor', 'initiative', ['initiative_id'], ['id'])
