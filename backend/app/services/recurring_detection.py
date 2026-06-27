"""Recurring theme detection with embedding-based similarity."""

from __future__ import annotations

import json
from typing import Any

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.models.ceremony import BoardItem, Ceremony
from app.models.health import RecurringTheme
from app.services.ai.embeddings import EmbeddingService

logger = structlog.get_logger()


# Blocker ontology categories
BLOCKER_CATEGORIES = [
    "planning",
    "requirements",
    "quality",
    "tech_debt",
    "dependency",
    "leadership",
    "tooling",
    "morale",
    "workload",
    "communication",
    "process",
    "infrastructure",
]


class RecurringThemeDetector:
    """Detect recurring themes across ceremonies using embeddings."""

    def __init__(self):
        self.embedding_service = EmbeddingService()

    async def detect_for_team(self, team_id: str) -> list[dict[str, Any]]:
        """Detect recurring themes for a team across all ceremonies."""
        async with async_session_factory() as session:
            # Get all ceremonies for this team
            result = await session.execute(
                select(Ceremony.id, Ceremony.title)
                .where(Ceremony.team_id == team_id)
                .order_by(Ceremony.created_at.desc())
                .limit(20)
            )
            ceremonies = result.all()

        if len(ceremonies) < 2:
            return []

        # Get all notes grouped by ceremony
        ceremony_notes: dict[str, list[str]] = {}
        for ceremony_id, title in ceremonies:
            result = await session.execute(
                select(BoardItem.content)
                .where(BoardItem.ceremony_id == ceremony_id)
            )
            notes = [row[0] for row in result.all()]
            if notes:
                ceremony_notes[ceremony_id] = notes

        if len(ceremony_notes) < 2:
            return []

        # Find recurring themes using embedding similarity
        recurring = await self._find_recurring(ceremony_notes)

        return recurring

    async def _find_recurring(
        self, ceremony_notes: dict[str, list[str]]
    ) -> list[dict[str, Any]]:
        """Find notes that are semantically similar across ceremonies."""
        all_embeddings: dict[str, list[tuple[str, list[float]]]] = {}

        for ceremony_id, notes in ceremony_notes.items():
            embeddings = await self.embedding_service.generate_embeddings(notes)
            all_embeddings[ceremony_id] = list(zip(notes, embeddings))

        # Cross-ceremony similarity check
        ceremony_ids = list(all_embeddings.keys())
        recurring_groups: list[dict[str, Any]] = []

        for i in range(len(ceremony_ids)):
            for j in range(i + 1, len(ceremony_ids)):
                cid_a = ceremony_ids[i]
                cid_b = ceremony_ids[j]

                for note_a, emb_a in all_embeddings[cid_a]:
                    for note_b, emb_b in all_embeddings[cid_b]:
                        sim = EmbeddingService.cosine_similarity(emb_a, emb_b)
                        if sim >= 0.75:
                            recurring_groups.append({
                                "note_a": note_a[:100],
                                "note_b": note_b[:100],
                                "similarity": round(sim, 3),
                                "ceremony_a": cid_a,
                                "ceremony_b": cid_b,
                            })

        # Deduplicate and group
        return recurring_groups[:20]

    async def store_recurring_themes(
        self, team_id: str, themes: list[dict[str, Any]]
    ) -> list[RecurringTheme]:
        """Store detected recurring themes."""
        async with async_session_factory() as session:
            stored = []
            for theme in themes:
                rt = RecurringTheme(
                    team_id=team_id,
                    label=theme.get("label", "Untitled"),
                    description=theme.get("description"),
                    occurrence_count=theme.get("occurrences", 2),
                    category=theme.get("category", "process"),
                )
                session.add(rt)
                stored.append(rt)

            await session.commit()
            return stored


class BlockerClassifier:
    """Classify blocker notes into ontology categories."""

    CATEGORY_KEYWORDS: dict[str, list[str]] = {
        "planning": ["estimate", "scope", "sprint goal", "planning", "backlog", "priorit"],
        "requirements": ["requirement", "spec", "unclear", "ambiguous", "missing detail"],
        "quality": ["bug", "defect", "test", "qa", "regression", "broken", "quality"],
        "tech_debt": ["refactor", "debt", "legacy", "cleanup", "deprecated", "outdated"],
        "dependency": ["blocked", "waiting", "depends", "external", "other team", "dependency"],
        "leadership": ["decision", "direction", "management", "leadership", "alignment"],
        "tooling": ["tool", "build", "ci", "cd", "deploy", "environment", "slow"],
        "morale": ["burnout", "stress", "motivation", "team culture", "conflict"],
        "workload": ["overworked", "capacity", "overtime", "too much", "bandwidth"],
        "communication": ["meeting", "email", "slack", "miscommunication", "info"],
        "process": ["process", "workflow", "ceremony", "retro", "standup"],
        "infrastructure": ["server", "network", "performance", "outage", "downtime"],
    }

    @classmethod
    def classify(cls, text: str) -> dict[str, Any]:
        """Classify a note into blocker categories with confidence scores."""
        text_lower = text.lower()
        scores: dict[str, float] = {}

        for category, keywords in cls.CATEGORY_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw in text_lower)
            if matches > 0:
                scores[category] = min(matches / len(keywords) * 2, 1.0)

        if not scores:
            return {"category": "other", "confidence": 0.0, "scores": {}}

        best_category = max(scores, key=scores.get)
        return {
            "category": best_category,
            "confidence": round(scores[best_category], 2),
            "scores": {k: round(v, 2) for k, v in scores.items()},
        }

    @classmethod
    def classify_batch(cls, notes: list[str]) -> list[dict[str, Any]]:
        """Classify multiple notes."""
        return [cls.classify(note) for note in notes]
