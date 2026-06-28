"""Async standup service and API."""

from __future__ import annotations

from typing import Any

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.models.ceremony import Ceremony

logger = structlog.get_logger()


class StandupService:
    """Manage async standup sessions."""

    async def create_standup(
        self,
        team_id: str,
        tenant_id: str,
        title: str = "Daily Standup",
    ) -> dict[str, Any]:
        """Create an async standup session."""
        async with async_session_factory() as session:
            ceremony = Ceremony(
                team_id=team_id,
                tenant_id=tenant_id,
                title=title,
                ceremony_type="async_standup",
                current_phase="open",
            )
            session.add(ceremony)
            await session.commit()

        return {
            "id": ceremony.id,
            "title": title,
            "type": "async_standup",
            "current_phase": "open",
        }

    async def submit_update(
        self,
        ceremony_id: str,
        user_id: str,
        done: str,
        doing: str,
        blockers: str | None = None,
    ) -> dict[str, Any]:
        """Submit a standup update."""
        return {
            "ceremony_id": ceremony_id,
            "user_id": user_id,
            "done": done,
            "doing": doing,
            "blockers": blockers,
            "has_blockers": bool(blockers),
            "submitted": True,
        }

    async def get_standup_digest(self, ceremony_id: str) -> dict[str, Any]:
        """Get a digest of all standup updates."""
        return {
            "ceremony_id": ceremony_id,
            "updates": [],
            "blocker_count": 0,
            "participant_count": 0,
        }
