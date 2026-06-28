"""Planning poker ceremony service and API."""

from __future__ import annotations

import json
from typing import Any

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.models.ceremony import Ceremony

logger = structlog.get_logger()


POKER_ESTIMATES = ["1", "2", "3", "5", "8", "13", "21", "?"]


class PokerService:
    """Manage planning poker sessions."""

    async def create_poker_session(
        self,
        team_id: str,
        tenant_id: str,
        title: str,
        stories: list[dict[str, str]],
    ) -> dict[str, Any]:
        """Create a new planning poker session."""
        async with async_session_factory() as session:
            ceremony = Ceremony(
                team_id=team_id,
                tenant_id=tenant_id,
                title=title,
                ceremony_type="planning_poker",
                current_phase="story_selection",
            )
            session.add(ceremony)
            await session.commit()

        return {
            "id": ceremony.id,
            "title": title,
            "type": "planning_poker",
            "current_phase": "story_selection",
            "stories": stories,
        }

    async def submit_estimate(
        self,
        ceremony_id: str,
        story_id: str,
        user_id: str,
        estimate: str,
    ) -> dict[str, Any]:
        """Submit an estimate for a story (hidden until reveal)."""
        # In production: store in poker_estimates table
        return {
            "ceremony_id": ceremony_id,
            "story_id": story_id,
            "user_id": user_id,
            "estimate": estimate,
            "submitted": True,
        }

    async def reveal_estimates(
        self,
        ceremony_id: str,
        story_id: str,
    ) -> dict[str, Any]:
        """Reveal all estimates for a story."""
        # In production: fetch estimates, check consensus
        return {
            "ceremony_id": ceremony_id,
            "story_id": story_id,
            "revealed": True,
            "estimates": [],
            "consensus": None,
        }

    async def get_poker_session(self, ceremony_id: str) -> dict[str, Any]:
        """Get poker session details."""
        async with async_session_factory() as session:
            result = await session.execute(
                select(Ceremony).where(Ceremony.id == ceremony_id)
            )
            ceremony = result.scalar_one_or_none()

        if not ceremony:
            return {"error": "Session not found"}

        return {
            "id": ceremony.id,
            "title": ceremony.title,
            "type": "planning_poker",
            "current_phase": ceremony.current_phase,
        }
