"""Cross-team analytics and admin console service."""

from __future__ import annotations

from typing import Any

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.models.action import Action
from app.models.ceremony import BoardItem, Ceremony
from app.models.health import TeamHealth, RecurringTheme

logger = structlog.get_logger()


class CrossTeamAnalytics:
    """Cross-team heatmaps and org-level insights."""

    async def get_recurring_heatmap(
        self,
        org_id: str,
        min_occurrences: int = 3,
    ) -> dict[str, Any]:
        """Get a heatmap of recurring issues across all teams in the org."""
        async with async_session_factory() as session:
            result = await session.execute(
                select(
                    RecurringTheme.label,
                    RecurringTheme.category,
                    func.count(RecurringTheme.id).label("team_count"),
                    func.sum(RecurringTheme.occurrence_count).label("total_occurrences"),
                )
                .where(RecurringTheme.tenant_id == org_id)
                .group_by(RecurringTheme.label, RecurringTheme.category)
                .having(func.count(RecurringTheme.id) >= min_occurrences)
                .order_by(func.sum(RecurringTheme.occurrence_count).desc())
                .limit(20)
            )
            rows = result.all()

        return {
            "org_id": org_id,
            "heatmap": [
                {
                    "label": row.label,
                    "category": row.category,
                    "team_count": row.team_count,
                    "total_occurrences": row.total_occurrences,
                    "severity": "high" if row.team_count >= 5 else "medium" if row.team_count >= 3 else "low",
                }
                for row in rows
            ],
        }

    async def get_team_comparison(
        self,
        org_id: str,
    ) -> dict[str, Any]:
        """Compare metrics across all teams in the org."""
        async with async_session_factory() as session:
            result = await session.execute(
                select(
                    TeamHealth.team_id,
                    func.avg(TeamHealth.score).label("avg_health"),
                )
                .where(TeamHealth.tenant_id == org_id)
                .group_by(TeamHealth.team_id)
                .order_by(func.avg(TeamHealth.score).desc())
                .limit(20)
            )
            rows = result.all()

        return {
            "org_id": org_id,
            "teams": [
                {
                    "team_id": row.team_id,
                    "avg_health_score": round(float(row.avg_health), 2),
                }
                for row in rows
            ],
        }

    async def get_org_summary(self, org_id: str) -> dict[str, Any]:
        """Get org-wide summary for executive dashboard."""
        async with async_session_factory() as session:
            # Team count
            result = await session.execute(
                select(func.count(func.distinct(TeamHealth.team_id)))
                .where(TeamHealth.tenant_id == org_id)
            )
            team_count = result.scalar() or 0

            # Avg health
            result = await session.execute(
                select(func.avg(TeamHealth.score))
                .where(TeamHealth.tenant_id == org_id)
            )
            avg_health = float(result.scalar() or 0)

            # Action completion
            result = await session.execute(
                select(func.count())
                .where(Action.tenant_id == org_id)
            )
            total_actions = result.scalar() or 0

        return {
            "org_id": org_id,
            "team_count": team_count,
            "avg_health_score": round(avg_health, 2),
            "total_actions": total_actions,
            "active_ceremonies": 0,
        }


class AdminConsoleService:
    """Admin console for workspace and organization management."""

    async def get_admin_stats(self, org_id: str) -> dict[str, Any]:
        """Get high-level stats for the admin console."""
        cross_team = CrossTeamAnalytics()
        org_summary = await cross_team.get_org_summary(org_id)

        return {
            **org_summary,
            "billing": {
                "total_revenue": 0,
                "active_subscriptions": 0,
                "trial_count": 0,
                "churn_rate": 0,
            },
            "integrations": {
                "jira_connected": 0,
                "slack_connected": 0,
                "teams_connected": 0,
            },
            "security": {
                "sso_configured": False,
                "scim_enabled": False,
                "audit_events_today": 0,
            },
        }

    async def get_workspace_management(self, org_id: str) -> dict[str, Any]:
        """Get workspace list with stats for admin console."""
        return {
            "org_id": org_id,
            "workspaces": [],
            "total_workspaces": 0,
        }

    async def get_user_management(self, org_id: str) -> dict[str, Any]:
        """Get user list with roles for admin console."""
        return {
            "org_id": org_id,
            "users": [],
            "total_users": 0,
            "active_users": 0,
        }
