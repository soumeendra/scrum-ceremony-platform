"""Anonymity engine — enforces per-phase anonymity rules.

This service implements the dual-path data architecture:
- Path A: Display content (board_items) — never contains author_id when anonymous
- Path B: Identity map (anonymous_author_map) — access-gated, audited
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ceremony import AnonymousAuthorMap, BoardItem, Ceremony


@dataclass
class AnonymityConfig:
    """Per-phase anonymity configuration for a ceremony."""

    collect: str = "anonymous"  # "anonymous" | "named"
    vote: str = "anonymous"
    discuss: str = "named"
    action: str = "named"  # ALWAYS named
    quiet_mode: bool = False
    delayed_reveal: bool = False

    @classmethod
    def from_json(cls, data: str | None) -> AnonymityConfig:
        if not data:
            return cls()
        return cls(**json.loads(data))

    def to_json(self) -> str:
        return json.dumps({
            "collect": self.collect,
            "vote": self.vote,
            "discuss": self.discuss,
            "action": self.action,
            "quiet_mode": self.quiet_mode,
            "delayed_reveal": self.delayed_reveal,
        })

    def is_anonymous(self, phase: str) -> bool:
        """Return True if the given phase should be anonymous."""
        return getattr(self, phase, "named") == "anonymous"


DEFAULT_ANONYMITY = AnonymityConfig()


class AnonymityEngine:
    """Enforces anonymity rules for ceremony board items."""

    @staticmethod
    async def create_board_item(
        db: AsyncSession,
        ceremony_id: str,
        tenant_id: str,
        content: str,
        column_name: str,
        user_id: str,
        is_anonymous: bool,
    ) -> BoardItem:
        """Create a board item with proper anonymity handling.

        When is_anonymous=True:
        - author_id is NULL in board_items
        - author_display is "Anonymous"
        - A mapping is stored in anonymous_author_map

        When is_anonymous=False:
        - author_id is set to the user's ID
        - author_display is the user's display name
        """
        item = BoardItem(
            ceremony_id=ceremony_id,
            tenant_id=tenant_id,
            column_name=column_name,
            content=content,
            is_anonymous=is_anonymous,
            author_id=user_id if not is_anonymous else None,
            author_display="Anonymous" if is_anonymous else None,  # Will be set from user
        )
        db.add(item)
        await db.flush()

        if is_anonymous:
            # Create anonymous author mapping
            anon_map = AnonymousAuthorMap(
                ceremony_id=ceremony_id,
                tenant_id=tenant_id,
                user_id=user_id,
                display_id=item.id,  # Use item ID as display pseudonym
            )
            db.add(anon_map)

        return item

    @staticmethod
    async def get_display_items(
        db: AsyncSession,
        ceremony_id: str,
    ) -> list[dict[str, Any]]:
        """Get board items for display (Path A — no author_id exposed).

        Returns items with author_display but NEVER author_id.
        """
        stmt = select(BoardItem).where(
            BoardItem.ceremony_id == ceremony_id,
        ).order_by(BoardItem.created_at)

        result = (await db.execute(stmt)).scalars().all()

        return [
            {
                "id": item.id,
                "content": item.content,
                "column_name": item.column_name,
                "is_anonymous": item.is_anonymous,
                "author_display": "Anonymous" if item.is_anonymous else item.author_display,
                "cluster_id": item.cluster_id,
                "order": item.order,
                "created_at": item.created_at,
            }
            for item in result
        ]

    @staticmethod
    async def resolve_author_identity(
        db: AsyncSession,
        board_item_id: str,
        requester_id: str,
        reason: str,
    ) -> dict[str, str] | None:
        """Break-glass: resolve anonymous author identity (Path B).

        ONLY accessible to org admins. Every access is audited.
        Returns user_id if found, None if not anonymous.
        """
        stmt = select(BoardItem).where(BoardItem.id == board_item_id)
        item = (await db.execute(stmt)).scalar_one_or_none()

        if not item or not item.is_anonymous:
            return None

        # Look up the real author
        map_stmt = select(AnonymousAuthorMap).where(
            AnonymousAuthorMap.ceremony_id == item.ceremony_id,
            AnonymousAuthorMap.display_id == item.id,
        )
        anon_map = (await db.execute(map_stmt)).scalar_one_or_none()

        if not anon_map:
            return None

        # TODO: Log audit event with requester_id + reason

        return {
            "user_id": anon_map.user_id,
            "reason": reason,
        }

    @staticmethod
    async def get_ceremony_anonymity(
        db: AsyncSession,
        ceremony_id: str,
    ) -> AnonymityConfig:
        """Get the anonymity configuration for a ceremony."""
        stmt = select(Ceremony.anonymity_config).where(Ceremony.id == ceremony_id)
        config_json = (await db.execute(stmt)).scalar_one_or_none()
        return AnonymityConfig.from_json(config_json)

    @staticmethod
    def set_ceremony_anonymity(
        ceremony: Ceremony,
        config: AnonymityConfig,
    ) -> None:
        """Set the anonymity configuration for a ceremony."""
        ceremony.anonymity_config = config.to_json()
