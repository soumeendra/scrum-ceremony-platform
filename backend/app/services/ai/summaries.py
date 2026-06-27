"""Summary service for generating retro summaries and extracting actions."""

from __future__ import annotations

import json
from typing import Any

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.models.ceremony import BoardItem, Ceremony, Cluster, Summary
from app.services.ai.ollama_client import OllamaClient

logger = structlog.get_logger()

SUMMARY_SCHEMA = {
    "type": "object",
    "properties": {
        "top_themes": {"type": "array", "items": {"type": "string"}},
        "top_voted_items": {"type": "array", "items": {"type": "string"}},
        "proposed_actions": {"type": "array", "items": {"type": "string"}},
        "carry_forward": {"type": "array", "items": {"type": "string"}},
    },
}

ACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "actions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "owner_hint": {"type": "string"},
                    "priority_hint": {"type": "string"},
                },
            },
        },
    },
}


class SummaryService:
    """Generate retro summaries, extract actions, analyze sentiment."""

    def __init__(self):
        self.llm = OllamaClient()

    async def generate_summary(self, ceremony_id: str) -> dict[str, Any]:
        """Generate a structured retro summary."""
        async with async_session_factory() as session:
            result = await session.execute(
                select(BoardItem).where(BoardItem.ceremony_id == ceremony_id)
            )
            notes = result.scalars().all()

        if not notes:
            return {"error": "No notes found"}

        note_texts = "\n".join(f"- {n.content}" for n in notes[:50])

        prompt = (
            f"Analyze these retrospective notes and generate a structured summary:\n\n"
            f"{note_texts}\n\n"
            f"Generate JSON with: top_themes (3-5 themes), "
            f"top_voted_items (most important items), "
            f"proposed_actions (suggested action items), "
            f"carry_forward (items to bring to next retro)."
        )

        result = await self.llm.generate(prompt, format=SUMMARY_SCHEMA)
        return result

    async def extract_actions(self, ceremony_id: str) -> list[dict[str, str]]:
        """Extract action items from retro notes."""
        async with async_session_factory() as session:
            result = await session.execute(
                select(BoardItem).where(BoardItem.ceremony_id == ceremony_id)
            )
            notes = result.scalars().all()

        if not notes:
            return []

        note_texts = "\n".join(f"- {n.content}" for n in notes[:30])

        prompt = (
            f"Extract actionable items from these retrospective notes:\n\n"
            f"{note_texts}\n\n"
            f"Generate JSON with 'actions' array. Each action needs: "
            f"title, description, owner_hint (who should take it), "
            f"priority_hint (high/medium/low)."
        )

        result = await self.llm.generate(prompt, format=ACTION_SCHEMA)
        return result.get("actions", [])

    async def analyze_sentiment(self, ceremony_id: str) -> dict[str, Any]:
        """Analyze sentiment of retro notes."""
        async with async_session_factory() as session:
            result = await session.execute(
                select(BoardItem).where(BoardItem.ceremony_id == ceremony_id)
            )
            notes = result.scalars().all()

        if not notes:
            return {"overall": "neutral", "score": 0, "per_note": []}

        note_texts = "\n".join(f"- {n.content}" for n in notes[:20])

        prompt = (
            f"Analyze the sentiment of these retrospective notes:\n\n"
            f"{note_texts}\n\n"
            f"Generate JSON with: overall (positive/neutral/negative), "
            f"score (-1 to 1), per_note (array of {{text, sentiment}})."
        )

        result = await self.llm.generate(prompt)
        return result

    async def store_summary(
        self, ceremony_id: str, content: dict, approved_by: str
    ) -> Summary:
        """Store an approved summary."""
        async with async_session_factory() as session:
            summary = Summary(
                ceremony_id=ceremony_id,
                tenant_id="",  # TODO: get from ceremony
                content=json.dumps(content),
                source="ai",
                approved_by=approved_by,
            )
            session.add(summary)
            await session.commit()
            return summary
