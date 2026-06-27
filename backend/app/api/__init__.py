"""API router aggregation – registers all sub-routers."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.health import router as health_router
from app.api.teams import router as teams_router
from app.api.ceremonies import router as ceremonies_router
from app.api.actions import router as actions_router
from app.api.templates import router as templates_router
from app.api.analytics import router as analytics_router
from app.api.integrations import router as integrations_router

__all__ = [
    "health_router",
    "teams_router",
    "ceremonies_router",
    "actions_router",
    "templates_router",
    "analytics_router",
    "integrations_router",
]
