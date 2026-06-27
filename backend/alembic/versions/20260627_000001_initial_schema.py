"""20260627_000001_initial_schema

SCP Migration — Review before applying to production.

Creates all 20 tables for the Scrum Ceremony Platform:
organizations, workspaces, users, teams, team_members, templates, ceremonies,
ceremony_states, board_items, anonymous_author_maps, votes, actions,
action_registers, integration_links, embeddings, clusters, summaries,
integration_configs, audit_events, team_health, recurring_themes.

Revision ID: 20260627_000001
Revises:
Create Date: 2026-06-27 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260627_000001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all tables for the Scrum Ceremony Platform."""

    # ── 1. organizations ──────────────────────────────────────────────────────
    op.create_table(
        "organizations",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), unique=True, nullable=False),
        sa.Column("logo_url", sa.Text, nullable=True),
        sa.Column("plan", sa.String(50), server_default="free", nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # ── 2. workspaces ────────────────────────────────────────────────────────
    op.create_table(
        "workspaces",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("tenant_id", sa.String(36), index=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index("ix_workspaces_organization_id", "workspaces", ["organization_id"])

    # ── 3. users ──────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("email", sa.String(320), unique=True, nullable=False),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("avatar_url", sa.String(1024), nullable=True),
        sa.Column("clerk_id", sa.String(255), unique=True, nullable=False),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=True),
        sa.Column("role", sa.String(50), server_default="member", nullable=True),
        sa.Column("tenant_id", sa.String(36), index=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # ── 4. teams ──────────────────────────────────────────────────────────────
    op.create_table(
        "teams",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=True),
        sa.Column("tenant_id", sa.String(36), index=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.UniqueConstraint("name", "tenant_id", name="uq_team_name_tenant"),
    )

    # ── 5. team_members ───────────────────────────────────────────────────────
    op.create_table(
        "team_members",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("team_id", sa.String(36), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("role", sa.String(50), server_default="member", nullable=True),
        sa.Column("tenant_id", sa.String(36), index=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "team_id", name="uq_team_member_user_team"),
    )
    op.create_index("ix_team_members_user_id", "team_members", ["user_id"])
    op.create_index("ix_team_members_team_id", "team_members", ["team_id"])

    # ── 6. templates ──────────────────────────────────────────────────────────
    op.create_table(
        "templates",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("ceremony_type", sa.String(50), nullable=False),
        sa.Column("structure", sa.Text, nullable=False),
        sa.Column("is_default", sa.Boolean, server_default="false", nullable=True),
        sa.Column("tenant_id", sa.String(36), index=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # ── 7. ceremonies ─────────────────────────────────────────────────────────
    op.create_table(
        "ceremonies",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("team_id", sa.String(36), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("template_id", sa.String(36), sa.ForeignKey("templates.id"), nullable=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("ceremony_type", sa.String(50), nullable=False),
        sa.Column("state", sa.String(50), server_default="draft", nullable=True),
        sa.Column("facilitate_ai", sa.Boolean, server_default="false", nullable=True),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("started_at", sa.String(50), nullable=True),
        sa.Column("ended_at", sa.String(50), nullable=True),
        sa.Column("tenant_id", sa.String(36), index=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index("ix_ceremonies_team_id", "ceremonies", ["team_id"])
    op.create_index("ix_ceremonies_template_id", "ceremonies", ["template_id"])

    # ── 8. ceremony_states ────────────────────────────────────────────────────
    op.create_table(
        "ceremony_states",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("ceremony_id", sa.String(36), sa.ForeignKey("ceremonies.id"), nullable=False),
        sa.Column("from_state", sa.String(50), nullable=True),
        sa.Column("to_state", sa.String(50), nullable=False),
        sa.Column("changed_by", sa.String(36), nullable=False),
        sa.Column("tenant_id", sa.String(36), index=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index("ix_ceremony_states_ceremony_id", "ceremony_states", ["ceremony_id"])
    op.create_unique_constraint("uq_ceremony_states_ceremony_id", "ceremony_states", ["ceremony_id"])

    # ── 9. board_items ────────────────────────────────────────────────────────
    op.create_table(
        "board_items",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("ceremony_id", sa.String(36), sa.ForeignKey("ceremonies.id"), nullable=False),
        sa.Column("column_name", sa.String(100), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("author_display_id", sa.String(36), nullable=True),
        sa.Column("cluster_id", sa.String(36), sa.ForeignKey("clusters.id"), nullable=True),
        sa.Column("order", sa.Integer, server_default="0", nullable=True),
        sa.Column("tenant_id", sa.String(36), index=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index("ix_board_items_ceremony_id", "board_items", ["ceremony_id"])
    op.create_index("ix_board_items_cluster_id", "board_items", ["cluster_id"])

    # ── 10. anonymous_author_maps ─────────────────────────────────────────────
    op.create_table(
        "anonymous_author_maps",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("ceremony_id", sa.String(36), sa.ForeignKey("ceremonies.id"), nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("display_id", sa.String(36), unique=True, nullable=False),
        sa.Column("tenant_id", sa.String(36), index=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index("ix_anonymous_author_maps_ceremony_id", "anonymous_author_maps", ["ceremony_id"])
    op.create_index("ix_anonymous_author_maps_user_id", "anonymous_author_maps", ["user_id"])

    # ── 11. votes ──────────────────────────────────────────────────────────────
    op.create_table(
        "votes",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("board_item_id", sa.String(36), sa.ForeignKey("board_items.id"), nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("value", sa.Integer, server_default="1", nullable=True),
        sa.Column("tenant_id", sa.String(36), index=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index("ix_votes_board_item_id", "votes", ["board_item_id"])
    op.create_index("ix_votes_user_id", "votes", ["user_id"])

    # ── 12. actions ───────────────────────────────────────────────────────────
    op.create_table(
        "actions",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("ceremony_id", sa.String(36), sa.ForeignKey("ceremonies.id"), nullable=False),
        sa.Column("team_id", sa.String(36), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("assignee_id", sa.String(36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("due_date", sa.String(50), nullable=True),
        sa.Column("priority", sa.String(20), server_default="medium", nullable=True),
        sa.Column("status", sa.String(30), server_default="open", nullable=True),
        sa.Column("source_item_id", sa.String(36), sa.ForeignKey("board_items.id"), nullable=True),
        sa.Column("tenant_id", sa.String(36), index=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index("ix_actions_ceremony_id", "actions", ["ceremony_id"])
    op.create_index("ix_actions_team_id", "actions", ["team_id"])
    op.create_index("ix_actions_assignee_id", "actions", ["assignee_id"])
    op.create_index("ix_actions_source_item_id", "actions", ["source_item_id"])

    # ── 13. action_registers ──────────────────────────────────────────────────
    op.create_table(
        "action_registers",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("team_id", sa.String(36), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("action_id", sa.String(36), sa.ForeignKey("actions.id"), nullable=False),
        sa.Column("is_recurring", sa.Boolean, server_default="false", nullable=True),
        sa.Column("recurring_pattern", sa.String(100), nullable=True),
        sa.Column("tenant_id", sa.String(36), index=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index("ix_action_registers_team_id", "action_registers", ["team_id"])
    op.create_unique_constraint("uq_action_registers_team_id", "action_registers", ["team_id"])

    # ── 14. integration_links ──────────────────────────────────────────────────
    op.create_table(
        "integration_links",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("action_id", sa.String(36), sa.ForeignKey("actions.id"), nullable=False),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("external_id", sa.String(255), nullable=False),
        sa.Column("external_url", sa.String(1024), nullable=True),
        sa.Column("sync_status", sa.String(30), server_default="pending", nullable=True),
        sa.Column("tenant_id", sa.String(36), index=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index("ix_integration_links_action_id", "integration_links", ["action_id"])

    # ── 15. embeddings ────────────────────────────────────────────────────────
    op.create_table(
        "embeddings",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("source_type", sa.String(50), nullable=False),
        sa.Column("source_id", sa.String(36), nullable=False),
        sa.Column("model_name", sa.String(100), nullable=False),
        sa.Column("vector", postgresql.VECTOR(1536), nullable=True),
        sa.Column("tenant_id", sa.String(36), index=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index("ix_embeddings_source_type", "embeddings", ["source_type"])
    op.create_index("ix_embeddings_source_id", "embeddings", ["source_id"])
    op.create_unique_constraint("uq_embeddings_source", "embeddings", ["source_type", "source_id"])

    # ── 16. clusters ──────────────────────────────────────────────────────────
    op.create_table(
        "clusters",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("ceremony_id", sa.String(36), sa.ForeignKey("ceremonies.id"), nullable=False),
        sa.Column("label", sa.String(255), nullable=False),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("item_count", sa.Integer, server_default="0", nullable=True),
        sa.Column("tenant_id", sa.String(36), index=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index("ix_clusters_ceremony_id", "clusters", ["ceremony_id"])

    # ── 17. summaries ─────────────────────────────────────────────────────────
    op.create_table(
        "summaries",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("ceremony_id", sa.String(36), sa.ForeignKey("ceremonies.id"), nullable=False),
        sa.Column("model_used", sa.String(100), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("token_count", sa.Integer, nullable=True),
        sa.Column("tenant_id", sa.String(36), index=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index("ix_summaries_ceremony_id", "summaries", ["ceremony_id"])

    # ── 18. integration_configs ────────────────────────────────────────────────
    op.create_table(
        "integration_configs",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("config", sa.Text, nullable=False),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=True),
        sa.Column("last_sync_at", sa.String(50), nullable=True),
        sa.Column("tenant_id", sa.String(36), index=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # ── 19. audit_events ──────────────────────────────────────────────────────
    op.create_table(
        "audit_events",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("actor_id", sa.String(36), nullable=False),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(50), nullable=False),
        sa.Column("resource_id", sa.String(36), nullable=False),
        sa.Column("detail", sa.Text, nullable=True),
        sa.Column("tenant_id", sa.String(36), index=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index("ix_audit_events_actor_id", "audit_events", ["actor_id"])
    op.create_index("ix_audit_events_resource", "audit_events", ["resource_type", "resource_id"])

    # ── 20. team_health ───────────────────────────────────────────────────────
    op.create_table(
        "team_health",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("team_id", sa.String(36), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("ceremony_id", sa.String(36), sa.ForeignKey("ceremonies.id"), nullable=True),
        sa.Column("score", sa.Float, nullable=False),
        sa.Column("dimension", sa.String(50), nullable=False),
        sa.Column("note", sa.Text, nullable=True),
        sa.Column("tenant_id", sa.String(36), index=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index("ix_team_health_team_id", "team_health", ["team_id"])
    op.create_index("ix_team_health_ceremony_id", "team_health", ["ceremony_id"])

    # ── 21. recurring_themes ──────────────────────────────────────────────────
    op.create_table(
        "recurring_themes",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("team_id", sa.String(36), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("label", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("occurrence_count", sa.Integer, server_default="1", nullable=True),
        sa.Column("first_seen_ceremony_id", sa.String(36), sa.ForeignKey("ceremonies.id"), nullable=False),
        sa.Column("last_seen_ceremony_id", sa.String(36), sa.ForeignKey("ceremonies.id"), nullable=False),
        sa.Column("tenant_id", sa.String(36), index=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index("ix_recurring_themes_team_id", "recurring_themes", ["team_id"])
    op.create_index("ix_recurring_themes_first_seen", "recurring_themes", ["first_seen_ceremony_id"])
    op.create_index("ix_recurring_themes_last_seen", "recurring_themes", ["last_seen_ceremony_id"])


def downgrade() -> None:
    """Drop all tables in reverse order (respecting foreign key dependencies)."""
    op.drop_table("recurring_themes")
    op.drop_table("team_health")
    op.drop_table("audit_events")
    op.drop_table("integration_configs")
    op.drop_table("summaries")
    op.drop_table("clusters")
    op.drop_table("embeddings")
    op.drop_table("integration_links")
    op.drop_table("action_registers")
    op.drop_table("actions")
    op.drop_table("votes")
    op.drop_table("anonymous_author_maps")
    op.drop_table("board_items")
    op.drop_table("ceremony_states")
    op.drop_table("ceremonies")
    op.drop_table("templates")
    op.drop_table("team_members")
    op.drop_table("teams")
    op.drop_table("users")
    op.drop_table("workspaces")
    op.drop_table("organizations")
