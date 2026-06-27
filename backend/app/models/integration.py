"""IntegrationConfig and AuditEvent models."""

from __future__ import annotations

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantMixin, TimestampMixin, UUIDPrimaryKeyMixin


class IntegrationConfig(UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin, Base):
    """Per-tenant integration configuration (Jira, ERPNext, Slack, etc.)."""

    __tablename__ = "integration_configs"
    __table_args__ = (*TenantMixin._tenant_table_args(),)

    provider: Mapped[str] = mapped_column(String(50), nullable=False)  # jira, erpnext, slack, github
    config: Mapped[dict] = mapped_column(Text, nullable=False, comment="JSON blob of provider-specific config")
    is_active: Mapped[bool] = mapped_column(default=True)
    last_sync_at: Mapped[str | None] = mapped_column(String(50), nullable=True)


class AuditEvent(UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin, Base):
    """Immutable audit log for compliance and debugging."""

    __tablename__ = "audit_events"
    __table_args__ = (*TenantMixin._tenant_table_args(),)

    actor_id: Mapped[str] = mapped_column(String(36), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)
    resource_id: Mapped[str] = mapped_column(String(36), nullable=False)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True, comment="JSON blob with change diff")
