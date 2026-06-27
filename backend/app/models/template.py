"""Template model – reusable ceremony templates."""

from __future__ import annotations

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Template(UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin, Base):
    """A reusable ceremony template (tenant-scoped)."""

    __tablename__ = "templates"
    __table_args__ = (*TenantMixin._tenant_table_args(),)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    ceremony_type: Mapped[str] = mapped_column(String(50), nullable=False)  # retro, standup, planning, review
    structure: Mapped[dict] = mapped_column(Text, nullable=False, comment="JSON blob of template structure")
    is_default: Mapped[bool] = mapped_column(default=False)
