"""Health check service for multi-dimensional team wellness assessment."""

from __future__ import annotations

import json
from typing import Any

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.models.ceremony import Ceremony
from app.models.health import TeamHealth

logger = structlog.get_logger()


# ── Health Dimensions ───────────────────────────────────────────────────────

HEALTH_DIMENSIONS = [
    {"id": "communication", "label": "Communication", "description": "How well the team communicates"},
    {"id": "collaboration", "label": "Collaboration", "description": "How well the team works together"},
    {"id": "quality", "label": "Quality", "description": "Code quality and testing practices"},
    {"id": "velocity", "label": "Velocity", "description": "Sprint predictability and throughput"},
    {"id": "morale", "label": "Morale", "description": "Team satisfaction and energy"},
    {"id": "process", "label": "Process", "description": "Agile process effectiveness"},
    {"id": "technical", "label": "Technical", "description": "Technical practices and tooling"},
    {"id": "growth", "label": "Growth", "description": "Learning and skill development"},
]

DEFAULT_DIMENSIONS = {d["id"]: 3.0 for d in HEALTH_DIMENSIONS}


class HealthService:
    """Manage team health checks and radar data."""

    async def submit_health_check(
        self,
        ceremony_id: str,
        team_id: str,
        tenant_id: str,
        scores: dict[str, float],
        notes: str | None = None,
    ) -> dict[str, Any]:
        """Submit a health check assessment after a retro."""
        # Validate scores
        validated = {}
        for dim in HEALTH_DIMENSIONS:
            score = scores.get(dim["id"], 3.0)
            validated[dim["id"]] = max(1.0, min(5.0, float(score)))

        # Calculate overall score
        overall = round(sum(validated.values()) / len(validated), 2)

        async with async_session_factory() as session:
            # Store each dimension
            for dim_id, score in validated.items():
                health = TeamHealth(
                    team_id=team_id,
                    ceremony_id=ceremony_id,
                    tenant_id=tenant_id,
                    score=score,
                    dimension=dim_id,
                    note=notes if dim_id == "communication" else None,
                )
                session.add(health)

            await session.commit()

        return {
            "ceremony_id": ceremony_id,
            "team_id": team_id,
            "scores": validated,
            "overall_score": overall,
            "dimensions": HEALTH_DIMENSIONS,
        }

    async def get_health_radar(self, team_id: str, ceremony_id: str | None = None) -> dict[str, Any]:
        """Get health radar data for visualization."""
        async with async_session_factory() as session:
            query = select(TeamHealth).where(TeamHealth.team_id == team_id)
            if ceremony_id:
                query = query.where(TeamHealth.ceremony_id == ceremony_id)

            result = await session.execute(query.order_by(TeamHealth.assessed_at.desc()))
            records = result.scalars().all()

        if not records:
            return {
                "team_id": team_id,
                "scores": DEFAULT_DIMENSIONS,
                "overall_score": 3.0,
                "has_data": False,
            }

        # Get latest score per dimension
        latest_scores: dict[str, float] = {}
        for record in records:
            if record.dimension not in latest_scores:
                latest_scores[record.dimension] = record.score

        # Fill missing dimensions with defaults
        for dim in HEALTH_DIMENSIONS:
            if dim["id"] not in latest_scores:
                latest_scores[dim["id"]] = 3.0

        overall = round(sum(latest_scores.values()) / len(latest_scores), 2)

        return {
            "team_id": team_id,
            "scores": latest_scores,
            "overall_score": overall,
            "has_data": True,
            "dimensions": HEALTH_DIMENSIONS,
        }

    async def get_health_trend(self, team_id: str, sprints: int = 10) -> list[dict[str, Any]]:
        """Get health score trend over multiple ceremonies."""
        async with async_session_factory() as session:
            result = await session.execute(
                select(TeamHealth)
                .where(TeamHealth.team_id == team_id)
                .order_by(TeamHealth.assessed_at.desc())
                .limit(sprints * len(HEALTH_DIMENSIONS))
            )
            records = result.scalars().all()

        # Group by ceremony
        ceremony_scores: dict[str, list[float]] = {}
        for record in records:
            if record.ceremony_id not in ceremony_scores:
                ceremony_scores[record.ceremony_id] = []
            ceremony_scores[record.ceremony_id].append(record.score)

        trend = []
        for cid, scores in reversed(list(ceremony_scores.items())):
            avg = round(sum(scores) / len(scores), 2)
            trend.append({
                "ceremony_id": cid,
                "score": avg,
                "dimensions": len(scores),
            })

        return trend

    async def detect_silent_participants(
        self,
        ceremony_id: str,
        team_member_count: int,
    ) -> dict[str, Any]:
        """Detect team members who didn't contribute to a ceremony."""
        async with async_session_factory() as session:
            from app.models.ceremony import BoardItem
            result = await session.execute(
                select(func.count(func.distinct(BoardItem.author_id)))
                .where(BoardItem.ceremony_id == ceremony_id)
            )
            participating = result.scalar() or 0

        silent = max(0, team_member_count - participating)

        return {
            "ceremony_id": ceremony_id,
            "team_member_count": team_member_count,
            "participating_count": participating,
            "silent_count": silent,
            "participation_rate": round(participating / max(team_member_count, 1) * 100, 1),
        }
