"""TeamHealth and RecurringTheme models."""

from __future__ import annotations

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantMixin, TimestampMixin, UUIDPrimaryKeyMixin


class TeamHealth(UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin, Base):
    """Team health check scores, tracked over time."""

    __tablename__ = "team_health"
    __table_args__ = (*TenantMixin._tenant_table_args(),)

    team_id: Mapped[str] = mapped_column(String(36), ForeignKey("teams.id"), nullable=False)
    ceremony_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("ceremonies.id"), nullable=True)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    dimension: Mapped[str] = mapped_column(String(50), nullable=False, comment="e.g. morale, velocity, collaboration")
    note: Mapped[str | None] = mapped_column(Text, nullable=True)


class RecurringTheme(UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin, Base):
    """A pattern or theme that recurs across multiple ceremonies."""

    __tablename__ = "recurring_themes"
    __table_args__ = (*TenantMixin._tenant_table_args(),)

    team_id: Mapped[str] = mapped_column(String(36), ForeignKey("teams.id"), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    occurrence_count: Mapped[int] = mapped_column(Integer, default=1)
    first_seen_ceremony_id: Mapped[str] = mapped_column(String(36), ForeignKey("ceremonies.id"), nullable=False)
    last_seen_ceremony_id: Mapped[str] = mapped_column(String(36), ForeignKey("ceremonies.id"), nullable=False)
