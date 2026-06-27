"""Analytics API – team health, recurring themes, ceremony metrics."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import CurrentUser

router = APIRouter()


@router.get("/dashboard", summary="Analytics dashboard")
async def analytics_dashboard(
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    team_id: str | None = None,
) -> dict:  # type: ignore[type-arg]
    """Return high-level analytics for the tenant or a specific team."""
    # Placeholder – wire up real aggregation queries
    return {
        "total_ceremonies": 0,
        "total_actions": 0,
        "avg_health_score": None,
        "team_id": team_id,
    }
