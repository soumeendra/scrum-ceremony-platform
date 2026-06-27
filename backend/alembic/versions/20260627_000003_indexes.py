"""20260627_000003_indexes

SCP Migration — Review before applying to production.

Creates performance indexes for common query patterns:
- board_items: composite on (ceremony_id, phase/column_name)
- votes: unique on (board_item_id, user_id) to prevent duplicate votes
- actions: composite on (team_id, status) for filtered action lists
- audit_events: composite on (actor_id, created_at) for actor timeline queries
- embeddings: HNSW index on vector column for fast cosine similarity search
- recurring_themes: composite on (team_id, category/label)
- ceremonies: composite on (team_id, state, scheduled_at/started_at)

Revision ID: 20260627_000003
Revises: 20260627_000002
Create Date: 2026-06-27 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260627_000003"
down_revision: Union[str, None] = "20260627_000002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create performance indexes."""

    # ── board_items: fast lookup of items by ceremony + column ────────────────
    op.create_index(
        "ix_board_items_ceremony_column",
        "board_items",
        ["ceremony_id", "column_name"],
    )

    # ── votes: prevent duplicate votes + fast vote lookups ───────────────────
    op.create_index(
        "uq_votes_board_item_user",
        "votes",
        ["board_item_id", "user_id"],
        unique=True,
    )

    # ── actions: filtered action lists by team + status ───────────────────────
    op.create_index(
        "ix_actions_team_status",
        "actions",
        ["team_id", "status"],
    )

    # ── actions: filter by assignee + status ──────────────────────────────────
    op.create_index(
        "ix_actions_assignee_status",
        "actions",
        ["assignee_id", "status"],
    )

    # ── audit_events: actor timeline queries ──────────────────────────────────
    op.create_index(
        "ix_audit_events_actor_created",
        "audit_events",
        ["actor_id", "created_at"],
    )

    # ── audit_events: resource-based lookups ──────────────────────────────────
    op.create_index(
        "ix_audit_events_resource_created",
        "audit_events",
        ["resource_type", "resource_id", "created_at"],
    )

    # ── embeddings: HNSW index for vector similarity search ───────────────────
    # Using cosine distance (vector_cosine_ops) with recommended HNSW params:
    #   m=16: number of bi-directional links per node
    #   ef_construction=64: build-time search breadth
    op.execute(
        "CREATE INDEX ix_embeddings_vector_hnsw ON embeddings "
        "USING hnsw (vector vector_cosine_ops) "
        "WITH (m = 16, ef_construction = 64);"
    )

    # ── recurring_themes: team + label lookups ────────────────────────────────
    op.create_index(
        "ix_recurring_themes_team_label",
        "recurring_themes",
        ["team_id", "label"],
    )

    # ── ceremonies: team + state + time for scheduling queries ────────────────
    op.create_index(
        "ix_ceremonies_team_state_started",
        "ceremonies",
        ["team_id", "state", "started_at"],
    )

    # ── ceremonies: type-based filtering within a team ────────────────────────
    op.create_index(
        "ix_ceremonies_team_type",
        "ceremonies",
        ["team_id", "ceremony_type"],
    )

    # ── team_members: fast team roster lookups ────────────────────────────────
    op.create_index(
        "ix_team_members_team_user_role",
        "team_members",
        ["team_id", "user_id", "role"],
    )

    # ── templates: lookup by ceremony type ────────────────────────────────────
    op.create_index(
        "ix_templates_ceremony_type",
        "templates",
        ["ceremony_type"],
    )

    # ── integration_configs: provider lookups ─────────────────────────────────
    op.create_index(
        "ix_integration_configs_provider",
        "integration_configs",
        ["provider"],
    )

    # ── integration_links: external system lookups ────────────────────────────
    op.create_index(
        "ix_integration_links_external",
        "integration_links",
        ["provider", "external_id"],
    )

    # ── team_health: team + dimension for health history ──────────────────────
    op.create_index(
        "ix_team_health_team_dimension",
        "team_health",
        ["team_id", "dimension"],
    )


def downgrade() -> None:
    """Drop all performance indexes."""
    op.drop_index("ix_team_health_team_dimension", table_name="team_health")
    op.drop_index("ix_integration_links_external", table_name="integration_links")
    op.drop_index("ix_integration_configs_provider", table_name="integration_configs")
    op.drop_index("ix_templates_ceremony_type", table_name="templates")
    op.drop_index("ix_team_members_team_user_role", table_name="team_members")
    op.drop_index("ix_ceremonies_team_type", table_name="ceremonies")
    op.drop_index("ix_ceremonies_team_state_started", table_name="ceremonies")
    op.drop_index("ix_recurring_themes_team_label", table_name="recurring_themes")
    op.execute("DROP INDEX IF EXISTS ix_embeddings_vector_hnsw;")
    op.drop_index("ix_audit_events_resource_created", table_name="audit_events")
    op.drop_index("ix_audit_events_actor_created", table_name="audit_events")
    op.drop_index("ix_actions_assignee_status", table_name="actions")
    op.drop_index("ix_actions_team_status", table_name="actions")
    op.drop_index("uq_votes_board_item_user", table_name="votes")
    op.drop_index("ix_board_items_ceremony_column", table_name="board_items")
