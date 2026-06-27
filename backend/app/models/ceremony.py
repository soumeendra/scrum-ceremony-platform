"""Ceremony, CeremonyState, BoardItem, AnonymousAuthorMap, and Vote models."""

from __future__ import annotations

import enum

from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TenantMixin, TimestampMixin, UUIDPrimaryKeyMixin


class CeremonyStateEnum(str, enum.Enum):
    """Lifecycle states for a ceremony."""

    DRAFT = "draft"
    ACTIVE = "active"
    VOTING = "voting"
    ACTION_ITEMS = "action_items"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Ceremony(UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin, Base):
    """A Scrum ceremony instance (tenant-scoped)."""

    __tablename__ = "ceremonies"
    __table_args__ = (*TenantMixin._tenant_table_args(),)

    team_id: Mapped[str] = mapped_column(String(36), ForeignKey("teams.id"), nullable=False)
    template_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("templates.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    ceremony_type: Mapped[str] = mapped_column(String(50), nullable=False)
    state: Mapped[str] = mapped_column(
        Enum(CeremonyStateEnum),
        default=CeremonyStateEnum.DRAFT,
    )
    facilitate_ai: Mapped[bool] = mapped_column(default=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ended_at: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Relationships
    board_items: Mapped[list[BoardItem]] = relationship(back_populates="ceremony", cascade="all, delete-orphan")
    ceremony_states: Mapped[list[CeremonyState]] = relationship(back_populates="ceremony", cascade="all, delete-orphan")


class CeremonyState(UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin, Base):
    """State transition audit log for a ceremony."""

    __tablename__ = "ceremony_states"
    __table_args__ = (*TenantMixin._tenant_table_args(),)

    ceremony_id: Mapped[str] = mapped_column(String(36), ForeignKey("ceremonies.id"), nullable=False)
    from_state: Mapped[str | None] = mapped_column(String(50), nullable=True)
    to_state: Mapped[str] = mapped_column(String(50), nullable=False)
    changed_by: Mapped[str] = mapped_column(String(36), nullable=False)

    # Relationships
    ceremony: Mapped[Ceremony] = relationship(back_populates="ceremony_states")


class BoardItem(UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin, Base):
    """A single item (card) on the ceremony board."""

    __tablename__ = "board_items"
    __table_args__ = (*TenantMixin._tenant_table_args(),)

    ceremony_id: Mapped[str] = mapped_column(String(36), ForeignKey("ceremonies.id"), nullable=False)
    column_name: Mapped[str] = mapped_column(String(100), nullable=False)  # went_well, improve, actions
    content: Mapped[str] = mapped_column(Text, nullable=False)
    author_display_id: Mapped[str | None] = mapped_column(String(36), nullable=True, comment="Links to anonymous_author_map")
    cluster_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("clusters.id"), nullable=True)
    order: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    ceremony: Mapped[Ceremony] = relationship(back_populates="board_items")
    votes: Mapped[list[Vote]] = relationship(back_populates="board_item", cascade="all, delete-orphan")


class AnonymousAuthorMap(UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin, Base):
    """Maps real user_id to a pseudonymised display id within a ceremony."""

    __tablename__ = "anonymous_author_maps"
    __table_args__ = (*TenantMixin._tenant_table_args(),)

    ceremony_id: Mapped[str] = mapped_column(String(36), ForeignKey("ceremonies.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    display_id: Mapped[str] = mapped_column(String(36), nullable=False, unique=True)


class Vote(UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin, Base):
    """A vote on a board item."""

    __tablename__ = "votes"
    __table_args__ = (*TenantMixin._tenant_table_args(),)

    board_item_id: Mapped[str] = mapped_column(String(36), ForeignKey("board_items.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    value: Mapped[int] = mapped_column(Integer, default=1)

    # Relationships
    board_item: Mapped[BoardItem] = relationship(back_populates="votes")
