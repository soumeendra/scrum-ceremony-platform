"""Add anonymity fields to ceremony and board item models.

Revision ID: 20260627_000005
Revises: 20260627_000004
Create Date: 2026-06-27

"""
from alembic import op
import sqlalchemy as sa

revision = "20260627_000005"
down_revision = "20260627_000004"
branch_labels = None
depends_on = None


def upgrade():
    # Add is_anonymous and author_id to board_items
    op.add_column("board_items", sa.Column("is_anonymous", sa.Boolean(), server_default="false", nullable=False))
    op.add_column("board_items", sa.Column("author_id", sa.String(36), nullable=True))
    op.add_column("board_items", sa.Column("author_display", sa.String(100), server_default="Anonymous", nullable=True))
    op.create_index("ix_board_items_author_id", "board_items", ["author_id"])

    # Add current_phase and anonymity_config to ceremonies
    op.add_column("ceremonies", sa.Column("current_phase", sa.String(50), server_default="draft", nullable=True))
    op.add_column("ceremonies", sa.Column("anonymity_config", sa.Text(), nullable=True))

    # Add voter_token to votes (nullable for backward compat)
    op.add_column("votes", sa.Column("voter_token", sa.String(36), server_placeholder=True, nullable=True))
    op.create_unique_constraint("uq_vote_item_token", "votes", ["board_item_id", "voter_token"])
    op.alter_column("votes", "user_id", nullable=True)

    # Add FK for board_items.author_id
    op.create_foreign_key("fk_board_items_author_id", "board_items", "users", ["author_id"], ["id"])


def downgrade():
    op.drop_constraint("fk_board_items_author_id", "board_items", type_="foreignkey")
    op.drop_unique_constraint("uq_vote_item_token", "votes", type_="unique")
    op.alter_column("votes", "user_id", nullable=False)
    op.drop_column("votes", "voter_token")
    op.drop_column("ceremonies", "anonymity_config")
    op.drop_column("ceremonies", "current_phase")
    op.drop_column("board_items", "author_display")
    op.drop_column("board_items", "author_id")
    op.drop_column("board_items", "is_anonymous")
