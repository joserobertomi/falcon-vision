"""Merge detection model migrations

Revision ID: b0a6c83b5da8
Revises: 1a31ce608336, 3b50e4f754a5
Create Date: 2025-10-15 18:58:18.965042

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'b0a6c83b5da8'
down_revision = ('1a31ce608336', '3b50e4f754a5')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
