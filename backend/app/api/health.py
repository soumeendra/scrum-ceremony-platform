"""Health check endpoint – reports status of all backing services."""

from __future__ import annotations

from datetime import datetime, timezone

import redis.asyncio as aioredis
import structlog
from fastapi import APIRouter
from sqlalchemy import text

from app.core.config import settings
from app.core.database import async_session_factory

logger = structlog.get_logger()

router = APIRouter()


@router.get("/health", tags=["health"])
async def health_check() -> dict:  # type: ignore[type-arg]
    """Return the health status of the API and all dependent services."""
    checks: dict[str, str] = {}

    # ── Database ──────────────────────────────────────────────────────────
    try:
        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as exc:
        logger.error("health.db_fail", error=str(exc))
        checks["database"] = "error"

    # ── Redis ─────────────────────────────────────────────────────────────
    try:
        r = aioredis.from_url(settings.REDIS_URL, socket_connect_timeout=3)
        await r.ping()
        await r.aclose()
        checks["redis"] = "ok"
    except Exception as exc:
        logger.error("health.redis_fail", error=str(exc))
        checks["redis"] = "error"

    overall = "ok" if all(v == "ok" for v in checks.values()) else "degraded"

    return {
        "status": overall,
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "env": settings.ENV,
        "checks": checks,
    }
