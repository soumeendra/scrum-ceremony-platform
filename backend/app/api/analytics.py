"""Analytics API – participation, actions, maturity, recurring themes, export."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import PlainTextResponse

from app.core.security import CurrentUser
from app.services.action_quality import score_action
from app.services.analytics import AnalyticsService
from app.services.recurring_detection import BlockerClassifier, RecurringThemeDetector

router = APIRouter()


@router.get("/dashboard", summary="Analytics dashboard")
async def analytics_dashboard(
    user: CurrentUser,
    team_id: str | None = None,
) -> dict:
    """Return high-level analytics dashboard."""
    service = AnalyticsService()
    return await service.get_dashboard(team_id)


@router.get("/participation/{ceremony_id}", summary="Participation metrics")
async def participation_metrics(
    ceremony_id: str,
    user: CurrentUser,
) -> dict:
    """Get participation metrics for a ceremony."""
    service = AnalyticsService()
    metrics = await service.get_participation_metrics(ceremony_id)
    return {"ceremony_id": ceremony_id, **metrics}


@router.get("/actions/{team_id}", summary="Action metrics")
async def action_metrics(
    team_id: str,
    user: CurrentUser,
) -> dict:
    """Get action item metrics for a team."""
    service = AnalyticsService()
    metrics = await service.get_action_metrics(team_id)
    return {"team_id": team_id, **metrics}


@router.get("/maturity/{team_id}", summary="Maturity score")
async def maturity_score(
    team_id: str,
    user: CurrentUser,
) -> dict:
    """Get team maturity score."""
    service = AnalyticsService()
    score = await service.get_team_maturity_score(team_id)
    return score


@router.get("/recurring/{team_id}", summary="Recurring themes")
async def recurring_themes(
    team_id: str,
    user: CurrentUser,
) -> dict:
    """Detect recurring themes across ceremonies."""
    detector = RecurringThemeDetector()
    themes = await detector.detect_for_team(team_id)
    return {"team_id": team_id, "themes": themes}


@router.post("/classify-blocker", summary="Classify a blocker")
async def classify_blocker(
    user: CurrentUser,
    text: str = ...,
) -> dict:
    """Classify a note into blocker categories."""
    result = BlockerClassifier.classify(text)
    return result


@router.post("/classify-batch", summary="Classify multiple notes")
async def classify_batch(
    user: CurrentUser,
    notes: list[str] = ...,
) -> dict:
    """Classify multiple notes into blocker categories."""
    results = BlockerClassifier.classify_batch(notes)
    return {"classifications": results}


@router.get("/action-quality/{action_id}", summary="Score action quality")
async def action_quality(
    action_id: str,
    user: CurrentUser,
) -> dict:
    """Score an action item's quality."""
    # In production: look up action by ID
    return {
        "action_id": action_id,
        "score": 75,
        "issues": [],
        "suggestions": [],
    }


@router.get("/export", summary="Export analytics as CSV")
async def export_analytics(
    user: CurrentUser,
    team_id: str | None = None,
) -> PlainTextResponse:
    """Export analytics as CSV."""
    service = AnalyticsService()
    csv_content = await service.export_csv(team_id or "")
    return PlainTextResponse(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=analytics.csv"},
    )


@router.get("/health/{team_id}", summary="Health trend")
async def health_trend(
    team_id: str,
    user: CurrentUser,
    sprints: int = Query(10, ge=1, le=50),
) -> dict:
    """Get team health trend over time."""
    service = AnalyticsService()
    trend = await service.get_health_trend(team_id, sprints)
    return {"team_id": team_id, "trend": trend}


# ── Health Check Endpoints ──────────────────────────────────────────────────

@router.post("/health/check/{ceremony_id}", summary="Submit health check")
async def submit_health_check(
    ceremony_id: str,
    user: CurrentUser,
    scores: dict[str, float],
    team_id: str | None = None,
    notes: str | None = None,
) -> dict:
    """Submit a health check assessment after a retro."""
    from app.services.health_service import HealthService
    service = HealthService()
    result = await service.submit_health_check(
        ceremony_id=ceremony_id,
        team_id=team_id or "",
        tenant_id=user.org_id,
        scores=scores,
        notes=notes,
    )
    return result


@router.get("/health/radar/{team_id}", summary="Health radar")
async def health_radar(
    team_id: str,
    user: CurrentUser,
    ceremony_id: str | None = None,
) -> dict:
    """Get health radar data for a team."""
    from app.services.health_service import HealthService
    service = HealthService()
    return await service.get_health_radar(team_id, ceremony_id)


@router.get("/participation/silent/{ceremony_id}", summary="Silent participants")
async def silent_participants(
    ceremony_id: str,
    user: CurrentUser,
    team_member_count: int = 10,
) -> dict:
    """Detect silent participants who didn't contribute."""
    from app.services.health_service import HealthService
    service = HealthService()
    return await service.detect_silent_participants(ceremony_id, team_member_count)
