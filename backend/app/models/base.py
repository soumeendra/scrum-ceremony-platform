"""SQLAlchemy declarative base and shared mixins."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Application-wide declarative base."""

    pass


# ── Mixins ──────────────────────────────────────────────────────────────────────


class UUIDPrimaryKeyMixin:
    """UUID primary key for all tables."""

    id: Mapped[uuid.UUID] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )


class TimestampMixin:
    """``created_at`` and ``updated_at`` columns with server-side defaults."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class TenantMixin:
    """``tenant_id`` column + RLS placeholder in ``__table_args__``."""

    tenant_id: Mapped[str] = mapped_column(
        String(36),
        index=True,
        nullable=False,
    )

    # Subclasses that also define their own __table_args__ must merge this.
    @classmethod
    def _tenant_table_args(cls) -> tuple[dict, ...]:
        """Return the RLS-policy placeholder entry for ``__table_args__``.

        Override or merge in concrete models as needed::

            __table_args__ = (
                *TenantMixin._tenant_table_args(),
                UniqueConstraint("name", "tenant_id"),
            )
        """
        return (
            {
                "comment": (
                    "RLS policy placeholder – apply "
                    "'ALTER TABLE ... ENABLE ROW LEVEL SECURITY' "
                    "and create a policy using app.current_tenant_id"
                ),
            },
        )
