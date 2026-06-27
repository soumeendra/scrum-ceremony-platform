"""20260627_000002_rls_policies

SCP Migration — Review before applying to production.

Enables Row Level Security on all tenant-scoped tables and creates:
- tenant_isolation_policy: restricts rows to current tenant_id
- tenant_admin_policy: allows org_admin role full access
Grants full DML to scp_app_user role.

RLS is the last line of defense. Application middleware also enforces tenant isolation.

Revision ID: 20260627_000002
Revises: 20260627_000001
Create Date: 2026-06-27 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260627_000002"
down_revision: Union[str, None] = "20260627_000001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# All tenant-scoped tables that require RLS
TENANT_TABLES = [
    "workspaces",
    "users",
    "teams",
    "team_members",
    "templates",
    "ceremonies",
    "ceremony_states",
    "board_items",
    "anonymous_author_maps",
    "votes",
    "actions",
    "action_registers",
    "integration_links",
    "embeddings",
    "clusters",
    "summaries",
    "integration_configs",
    "audit_events",
    "team_health",
    "recurring_themes",
]


def _enable_rls(table: str) -> str:
    return f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;"


def _drop_rls(table: str) -> str:
    return f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;"


def _create_tenant_isolation_policy(table: str) -> str:
    return (
        f"CREATE POLICY tenant_isolation_policy ON {table}\n"
        f"  USING (tenant_id = current_setting('app.current_tenant_id', true)::uuid)\n"
        f"  WITH CHECK (tenant_id = current_setting('app.current_tenant_id', true)::uuid);"
    )


def _drop_tenant_isolation_policy(table: str) -> str:
    return f"DROP POLICY IF EXISTS tenant_isolation_policy ON {table};"


def _create_tenant_admin_policy(table: str) -> str:
    return (
        f"CREATE POLICY tenant_admin_policy ON {table}\n"
        f"  USING (current_setting('app.current_user_role', true) = 'org_admin');\n"
    )


def _drop_tenant_admin_policy(table: str) -> str:
    return f"DROP POLICY IF EXISTS tenant_admin_policy ON {table};"


def _grant_all(table: str) -> str:
    return (
        f"GRANT SELECT, INSERT, UPDATE, DELETE ON {table} TO scp_app_user;"
    )


def _revoke_all(table: str) -> str:
    return (
        f"REVOKE ALL ON {table} FROM scp_app_user;"
    )


def upgrade() -> None:
    """Enable RLS, create policies, and grant permissions."""
    # Grant schema usage first
    op.execute("GRANT USAGE ON SCHEMA public TO scp_app_user;")

    for table in TENANT_TABLES:
        # Enable RLS
        op.execute(_enable_rls(table))
        # Create tenant isolation policy
        op.execute(_create_tenant_isolation_policy(table))
        # Create admin bypass policy
        op.execute(_create_tenant_admin_policy(table))
        # Grant DML permissions
        op.execute(_grant_all(table))


def downgrade() -> None:
    """Revoke permissions, drop policies, and disable RLS."""
    for table in reversed(TENANT_TABLES):
        # Revoke DML permissions
        op.execute(_revoke_all(table))
        # Drop policies
        op.execute(_drop_tenant_admin_policy(table))
        op.execute(_drop_tenant_isolation_policy(table))
        # Disable RLS
        op.execute(_drop_rls(table))

    # Revoke schema usage
    op.execute("REVOKE USAGE ON SCHEMA public FROM scp_app_user;")
