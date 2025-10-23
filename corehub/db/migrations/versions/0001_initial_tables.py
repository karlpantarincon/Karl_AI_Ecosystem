"""Initial tables

Revision ID: 0001
Revises: 
Create Date: 2025-10-22 20:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create tasks table
    op.create_table('tasks',
        sa.Column('id', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('prio', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create runs table
    op.create_table('runs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('agent', sa.String(length=100), nullable=False),
        sa.Column('task_id', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('cost_usd', sa.Float(), nullable=True),
        sa.Column('duration_sec', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create events table
    op.create_table('events',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('agent', sa.String(length=100), nullable=True),
        sa.Column('type', sa.String(length=100), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create flags table
    op.create_table('flags',
        sa.Column('key', sa.String(length=100), nullable=False),
        sa.Column('value', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('key')
    )
    
    # Insert initial flags
    op.execute("""
        INSERT INTO flags (key, value, description, updated_at) 
        VALUES ('system_paused', 'false', 'System pause flag', datetime('now'))
    """)


def downgrade() -> None:
    op.drop_table('flags')
    op.drop_table('events')
    op.drop_table('runs')
    op.drop_table('tasks')
