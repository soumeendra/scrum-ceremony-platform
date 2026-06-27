"""Team and TeamMember models."""

from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TenantMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Team(UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin, Base):
    """A Scrum team (tenant-scoped)."""

    __tablename__ = "teams"
    __table_args__ = (
        *TenantMixin._tenant_table_args(),
        UniqueConstraint("name", "tenant_id", name="uq_team_name_tenant"),
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    members: Mapped[list[TeamMember]] = relationship(back_populates="team", cascade="all, delete-orphan")


class TeamMember(UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin, Base):
    """Membership join table between User and Team."""

    __tablename__ = "team_members"
    __table_args__ = (
        *TenantMixin._tenant_table_args(),
        UniqueConstraint("user_id", "team_id", name="uq_team_member_user_team"),
    )

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    team_id: Mapped[str] = mapped_column(String(36), ForeignKey("teams.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="member")  # scrum_master, product_owner, member

    # Relationships
    team: Mapped[Team] = relationship(back_populates="members")
