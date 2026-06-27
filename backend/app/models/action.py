"""Action, ActionRegister, and IntegrationLink models."""

from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TenantMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Action(UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin, Base):
    """An action item arising from a ceremony."""

    __tablename__ = "actions"
    __table_args__ = (*TenantMixin._tenant_table_args(),)

    ceremony_id: Mapped[str] = mapped_column(String(36), ForeignKey("ceremonies.id"), nullable=False)
    team_id: Mapped[str] = mapped_column(String(36), ForeignKey("teams.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    assignee_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    due_date: Mapped[str | None] = mapped_column(String(50), nullable=True)
    priority: Mapped[str] = mapped_column(String(20), default="medium")  # low, medium, high, critical
    status: Mapped[str] = mapped_column(String(30), default="open")  # open, in_progress, done, dropped
    source_item_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("board_items.id"), nullable=True)

    # Relationships
    integration_links: Mapped[list[IntegrationLink]] = relationship(back_populates="action", cascade="all, delete-orphan")


class ActionRegister(UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin, Base):
    """Persistent register of all actions across ceremonies for a team."""

    __tablename__ = "action_registers"
    __table_args__ = (*TenantMixin._tenant_table_args(),)

    team_id: Mapped[str] = mapped_column(String(36), ForeignKey("teams.id"), nullable=False)
    action_id: Mapped[str] = mapped_column(String(36), ForeignKey("actions.id"), nullable=False)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    recurring_pattern: Mapped[str | None] = mapped_column(String(100), nullable=True)


class IntegrationLink(UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin, Base):
    """Links an action to an external issue / task (Jira, ERPNext, etc.)."""

    __tablename__ = "integration_links"
    __table_args__ = (*TenantMixin._tenant_table_args(),)

    action_id: Mapped[str] = mapped_column(String(36), ForeignKey("actions.id"), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)  # jira, erpnext, github
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)
    external_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    sync_status: Mapped[str] = mapped_column(String(30), default="pending")  # pending, synced, error

    # Relationships
    action: Mapped[Action] = relationship(back_populates="integration_links")
