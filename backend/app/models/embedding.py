"""Embedding, Cluster, and Summary models for AI-assisted features."""

from __future__ import annotations

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TenantMixin, TimestampMixin, UUIDPrimaryKeyMixin

try:
    from pgvector.sqlalchemy import Vector
except ImportError:  # pragma: no cover – pgvector may not be installed in CI
    Vector = None  # type: ignore[assignment,misc]


class Embedding(UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin, Base):
    """Vector embedding for a board item or action."""

    __tablename__ = "embeddings"
    __table_args__ = (*TenantMixin._tenant_table_args(),)

    source_type: Mapped[str] = mapped_column(String(50), nullable=False)  # board_item, action
    source_id: Mapped[str] = mapped_column(String(36), nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    vector: Mapped[list[float] | None] = mapped_column(
        Vector(1536) if Vector is not None else Text,  # type: ignore[arg-type]
        nullable=True,
    )


class Cluster(UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin, Base):
    """A group of semantically similar board items."""

    __tablename__ = "clusters"
    __table_args__ = (*TenantMixin._tenant_table_args(),)

    ceremony_id: Mapped[str] = mapped_column(String(36), ForeignKey("ceremonies.id"), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    item_count: Mapped[int] = mapped_column(Integer, default=0)


class Summary(UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin, Base):
    """AI-generated summary for a ceremony."""

    __tablename__ = "summaries"
    __table_args__ = (*TenantMixin._tenant_table_args(),)

    ceremony_id: Mapped[str] = mapped_column(String(36), ForeignKey("ceremonies.id"), nullable=False)
    model_used: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
