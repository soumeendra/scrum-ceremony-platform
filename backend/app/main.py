"""Scrum Ceremony Platform – FastAPI application factory."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api import health_router, teams_router, ceremonies_router, board_items_router, actions_router, templates_router, analytics_router, integrations_router
from app.api.poker import router as poker_router
from app.api.standup import router as standup_router
from app.api.api_v1 import router as api_v1_router
from app.api.notifications import router as notifications_router
from app.api.shared_ceremonies import router as shared_ceremonies_router
from app.api.billing import router as billing_router
from app.api.ai import router as ai_router
from app.api.integrations import router as integration_api_router
from app.api.export import router as export_router
from app.api.audit import router as audit_router
from app.api.compliance import router as compliance_router
from app.ws.server import router as ws_router
from app.core.config import settings
from app.core.database import db_engine, async_session_factory, set_tenant_context
from app.core.security import ClerkJWKS

logger = structlog.get_logger()


# ---------------------------------------------------------------------------
# Lifespan (replaces deprecated on_event)
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:  # noqa: ARG001
    """Startup / shutdown hooks."""
    logger.info("app.starting", env=settings.ENV)
    # Pre-fetch Clerk JWKS so the first request isn't slow
    await ClerkJWKS.fetch()
    # Redis pool is created lazily by arq/redis clients, nothing to init here
    yield
    # Shutdown
    await db_engine.dispose()
    logger.info("app.stopped")


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------
def create_app() -> FastAPI:
    app = FastAPI(
        title="Scrum Ceremony Platform",
        version="0.1.0",
        docs_url="/docs" if settings.ENV != "production" else None,
        redoc_url="/redoc" if settings.ENV != "production" else None,
        lifespan=lifespan,
    )

    # ── Middleware ─────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def tenant_context_middleware(request: Request, call_next):  # type: ignore[no-untyped-def]
        """Extract tenant_id from JWT and set PostgreSQL session variable."""
        tenant_id: str | None = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header.split(" ", 1)[1]
            try:
                from app.core.security import verify_token

                user = await verify_token(token)
                tenant_id = user.org_id
            except Exception:
                # Unauthenticated request – no tenant context
                pass

        if tenant_id:
            async with async_session_factory() as session:
                await set_tenant_context(session, tenant_id)

        response: Response = await call_next(request)
        return response

    # ── Routers ────────────────────────────────────────────────────────────
    app.include_router(health_router)
    app.include_router(teams_router, prefix="/api/v1/teams", tags=["teams"])
    app.include_router(ceremonies_router, prefix="/api/v1/ceremonies", tags=["ceremonies"])
    app.include_router(board_items_router, prefix="/api/v1/ceremonies", tags=["board-items"])
    app.include_router(actions_router, prefix="/api/v1/actions", tags=["actions"])
    app.include_router(templates_router, prefix="/api/v1/templates", tags=["templates"])
    app.include_router(analytics_router, prefix="/api/v1/analytics", tags=["analytics"])
    app.include_router(integrations_router, prefix="/api/v1/integrations", tags=["integrations"])

    # ── WebSocket ──────────────────────────────────────────────────────────
    app.include_router(ws_router, prefix="/ws")

    # ── Voting ─────────────────────────────────────────────────────────────
    app.include_router(votes_router, prefix="/api/v1/ceremonies", tags=["votes"])

    # ── Integrations ───────────────────────────────────────────────────────
    app.include_router(integration_api_router, prefix="/api/v1/integrations", tags=["integrations"])

    # ── AI ─────────────────────────────────────────────────────────────────
    app.include_router(ai_router, prefix="/api/v1/ai", tags=["ai"])

    # ── Billing ────────────────────────────────────────────────────────────
    app.include_router(billing_router, prefix="/api/v1/billing", tags=["billing"])

    # ── Export & Audit ─────────────────────────────────────────────────────
    app.include_router(export_router, prefix="/api/v1/export", tags=["export"])
    app.include_router(audit_router, prefix="/api/v1/audit", tags=["audit"])

    # ── Compliance ─────────────────────────────────────────────────────────
    app.include_router(compliance_router, prefix="/api/v1/compliance", tags=["compliance"])

    # ── Multi-Ceremony ─────────────────────────────────────────────────────
    app.include_router(poker_router, prefix="/api/v1/poker", tags=["poker"])
    app.include_router(standup_router, prefix="/api/v1/standup", tags=["standup"])
    app.include_router(shared_ceremonies_router, prefix="/api/v1/shared", tags=["shared"])

    # ── Notifications ──────────────────────────────────────────────────────
    app.include_router(notifications_router, prefix="/api/v1/notifications", tags=["notifications"])

    # ── API Meta ───────────────────────────────────────────────────────────
    app.include_router(api_v1_router, tags=["api"])

    return app


app = create_app()
