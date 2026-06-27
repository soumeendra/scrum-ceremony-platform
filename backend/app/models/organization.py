"""Organization and Workspace models."""

from __future__ import annotations

import uuid

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TenantMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Organization(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Top-level tenant / billing entity."""

    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    logo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    plan: Mapped[str] = mapped_column(String(50), default="free")

    # Relationships
    workspaces: Mapped[list[Workspace]] = relationship(back_populates="organization", cascade="all, delete-orphan")


class Workspace(UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin, Base):
    """A workspace within an organization (tenant-scoped)."""

    __tablename__ = "workspaces"
    __table_args__ = (*TenantMixin._tenant_table_args(),)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False)

    # Relationships
    organization: Mapped[Organization] = relationship(back_populates="workspaces")
