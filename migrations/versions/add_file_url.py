"""Add file_url to Document model

Revision ID: add_file_url
Revises: initial_migration
Create Date: 2024-10-29 00:20:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_file_url'
down_revision = 'initial_migration'
branch_labels = None
depends_on = None

def upgrade():
    # Add file_url column to document table
    op.add_column('document', sa.Column('file_url', sa.String(500), nullable=True))

def downgrade():
    # Remove file_url column from document table
    op.drop_column('document', 'file_url')
