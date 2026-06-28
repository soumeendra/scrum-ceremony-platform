"""Admin console and cross-team analytics API."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.security import CurrentUser, require_role
from app.services.admin_console import AdminConsoleService, CrossTeamAnalytics

router = APIRouter()


# ── Cross-Team Analytics ─────────────────────────────────────────────────────

@router.get("/analytics/heatmap/{org_id}", summary="Recurring issue heatmap")
async def recurring_heatmap(
    org_id: str,
    user: Annotated[CurrentUser, Depends(require_role("org_admin"))],
    min_occurrences: int = 3,
) -> dict:
    """Get a heatmap of recurring issues across all teams."""
    service = CrossTeamAnalytics()
    return await service.get_recurring_heatmap(org_id, min_occurrences)


@router.get("/analytics/team-comparison/{org_id}", summary="Team comparison")
async def team_comparison(
    org_id: str,
    user: Annotated[CurrentUser, Depends(require_role("org_admin"))],
) -> dict:
    """Compare metrics across all teams in the org."""
    service = CrossTeamAnalytics()
    return await service.get_team_comparison(org_id)


@router.get("/analytics/org-summary/{org_id}", summary="Org summary")
async def org_summary(
    org_id: str,
    user: Annotated[CurrentUser, Depends(require_role("org_admin"))],
) -> dict:
    """Get org-wide summary for executive dashboard."""
    service = CrossTeamAnalytics()
    return await service.get_org_summary(org_id)


# ── Admin Console ────────────────────────────────────────────────────────────

@router.get("/admin/stats", summary="Admin stats")
async def admin_stats(
    user: Annotated[CurrentUser, Depends(require_role("org_admin"))],
) -> dict:
    """Get high-level stats for the admin console."""
    service = AdminConsoleService()
    return await service.get_admin_stats(user.org_id or "")


@router.get("/admin/workspaces", summary="Workspace management")
async def workspace_management(
    user: Annotated[CurrentUser, Depends(require_role("org_admin"))],
) -> dict:
    """Get workspace list with stats."""
    service = AdminConsoleService()
    return await service.get_workspace_management(user.org_id or "")


@router.get("/admin/users", summary="User management")
async def user_management(
    user: Annotated[CurrentUser, Depends(require_role("org_admin"))],
) -> dict:
    """Get user list with roles."""
    service = AdminConsoleService()
    return await service.get_user_management(user.org_id or "")
