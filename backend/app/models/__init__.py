"""Domain models – import everything so Alembic and the ORM can see it."""

from app.models.base import Base, TenantMixin, TimestampMixin, UUIDPrimaryKeyMixin

# ── Organization / multi-tenancy ───────────────────────────────────────────────
from app.models.organization import Organization, Workspace
from app.models.team import Team, TeamMember
from app.models.user import User

# ── Ceremony domain ───────────────────────────────────────────────────────────
from app.models.template import Template
from app.models.ceremony import Ceremony, CeremonyState, BoardItem, AnonymousAuthorMap, Vote
from app.models.action import Action, ActionRegister, IntegrationLink

# ── AI / analytics ─────────────────────────────────────────────────────────────
from app.models.embedding import Embedding, Cluster, Summary

# ── Integrations & audit ──────────────────────────────────────────────────────
from app.models.integration import IntegrationConfig, AuditEvent

# ── Team health & recurring themes ────────────────────────────────────────────
from app.models.health import TeamHealth, RecurringTheme

__all__ = [
    # base
    "Base",
    "TenantMixin",
    "TimestampMixin",
    "UUIDPrimaryKeyMixin",
    # org
    "Organization",
    "Workspace",
    # team
    "Team",
    "TeamMember",
    "User",
    # ceremony
    "Template",
    "Ceremony",
    "CeremonyState",
    "BoardItem",
    "AnonymousAuthorMap",
    "Vote",
    # action
    "Action",
    "ActionRegister",
    "IntegrationLink",
    # ai
    "Embedding",
    "Cluster",
    "Summary",
    # integration
    "IntegrationConfig",
    "AuditEvent",
    # health
    "TeamHealth",
    "RecurringTheme",
]
