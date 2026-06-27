"""Analytics service for participation, actions, maturity, and trends."""

from __future__ import annotations

import csv
import io
from typing import Any

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.models.action import Action
from app.models.ceremony import BoardItem, Ceremony
from app.models.health import TeamHealth

logger = structlog.get_logger()


class AnalyticsService:
    """Compute analytics metrics for teams and ceremonies."""

    async def get_participation_metrics(self, ceremony_id: str) -> dict[str, Any]:
        """Get participation metrics for a ceremony."""
        async with async_session_factory() as session:
            result = await session.execute(
                select(func.count(func.distinct(BoardItem.author_id)))
                .where(BoardItem.ceremony_id == ceremony_id)
            )
            contributor_count = result.scalar() or 0

            result = await session.execute(
                select(func.count()).where(BoardItem.ceremony_id == ceremony_id)
            )
            total_items = result.scalar() or 0

        return {
            "contributor_count": contributor_count,
            "total_items": total_items,
            "silent_participants": max(0, 0),  # TODO: compare to team size
            "items_per_contributor": round(total_items / max(contributor_count, 1), 1),
        }

    async def get_action_metrics(self, team_id: str) -> dict[str, Any]:
        """Get action item metrics for a team."""
        async with async_session_factory() as session:
            result = await session.execute(
                select(Action.status, func.count())
                .where(Action.team_id == team_id)
                .group_by(Action.status)
            )
            status_counts = {row[0]: row[1] for row in result.all()}

        open_count = status_counts.get("open", 0)
        in_progress = status_counts.get("in_progress", 0)
        done = status_counts.get("done", 0)
        total = open_count + in_progress + done

        return {
            "open": open_count,
            "in_progress": in_progress,
            "done": done,
            "dropped": status_counts.get("dropped", 0),
            "total": total,
            "completion_rate": round(done / max(total, 1) * 100, 1),
        }

    async def get_team_maturity_score(self, team_id: str) -> dict[str, Any]:
        """Compute maturity score for a team (0-100)."""
        metrics = await self.get_action_metrics(team_id)

        # Weighted scoring
        action_score = min(metrics["completion_rate"], 100) * 0.4
        ceremony_score = 70  # Placeholder — would compute from ceremony frequency
        participation_score = 75  # Placeholder — would compute from contribution balance
        improvement_score = 60  # Placeholder — would track over time

        overall = round(action_score + ceremony_score * 0.25 + participation_score * 0.2 + improvement_score * 0.15)

        return {
            "team_id": team_id,
            "ceremony_discipline": round(ceremony_score),
            "action_completion": round(action_score),
            "participation_balance": round(participation_score),
            "improvement_velocity": round(improvement_score),
            "overall_score": round(overall),
            "maturity_level": self._maturity_level(overall),
        }

    async def detect_recurring_themes(self, team_id: str) -> list[dict[str, Any]]:
        """Detect recurring themes across ceremonies."""
        async with async_session_factory() as session:
            result = await session.execute(
                select(Ceremony.id)
                .where(Ceremony.team_id == team_id)
                .order_by(Ceremony.created_at.desc())
                .limit(10)
            )
            ceremony_ids = [row[0] for row in result.all()]

        # In production: use embedding similarity to detect recurring themes
        return [
            {
                "label": "Communication gaps",
                "category": "communication",
                "occurrences": 3,
                "is_resolved": False,
                "ceremony_ids": ceremony_ids[:3],
            }
        ]

    async def get_health_trend(self, team_id: str, sprints: int = 10) -> list[dict[str, Any]]:
        """Get team health scores over time."""
        async with async_session_factory() as session:
            result = await session.execute(
                select(TeamHealth)
                .where(TeamHealth.team_id == team_id)
                .order_by(TeamHealth.assessed_at.desc())
                .limit(sprints)
            )
            records = result.scalars().all()

        return [
            {
                "date": r.assessed_at,
                "score": r.overall_score,
                "dimensions": r.dimensions if isinstance(r.dimensions, dict) else {},
            }
            for r in reversed(records)
        ]

    async def export_csv(self, team_id: str) -> str:
        """Export analytics as CSV."""
        output = io.StringIO()
        writer = csv.writer(output)

        # Actions section
        writer.writerow(["Action Items"])
        writer.writerow(["Title", "Status", "Priority", "Due Date", "Assignee"])
        async with async_session_factory() as session:
            result = await session.execute(
                select(Action).where(Action.team_id == team_id)
            )
            for action in result.scalars().all():
                writer.writerow([
                    action.title,
                    action.status,
                    action.priority,
                    action.due_date or "",
                    action.assignee_id or "",
                ])

        return output.getvalue()

    async def get_dashboard(self, team_id: str | None = None) -> dict[str, Any]:
        """Get high-level dashboard data."""
        async with async_session_factory() as session:
            result = await session.execute(select(func.count()).select_from(Ceremony))
            total_ceremonies = result.scalar() or 0

            result = await session.execute(select(func.count()).select_from(Action))
            total_actions = result.scalar() or 0

        return {
            "total_ceremonies": total_ceremonies,
            "total_actions": total_actions,
            "team_id": team_id,
        }

    @staticmethod
    def _maturity_level(score: int) -> str:
        if score >= 80:
            return "optimized"
        if score >= 60:
            return "managed"
        if score >= 40:
            return "developing"
        if score >= 20:
            return "emerging"
        return "initial"
