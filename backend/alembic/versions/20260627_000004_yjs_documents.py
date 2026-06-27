"""Add yjs_documents table for real-time board state persistence.

Revision ID: 20260627_000004
Revises: 20260627_000003
Create Date: 2026-06-27

"""
from alembic import op
import sqlalchemy as sa

revision = "20260627_000004"
down_revision = "20260627_000003"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "yjs_documents",
        sa.Column("ceremony_id", sa.String(36), primary_key=True),
        sa.Column("doc_state", sa.LargeBinary(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table("yjs_documents")
