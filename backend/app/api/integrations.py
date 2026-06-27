"""Integrations API – ERPNext, Jira, Slack, etc."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import CurrentUser, require_role
from app.models.integration import IntegrationConfig

router = APIRouter()


@router.get("/", summary="List integrations")
async def list_integrations(
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:  # type: ignore[type-arg]
    """Return all integration configs for the current tenant."""
    stmt = select(IntegrationConfig).where(IntegrationConfig.tenant_id == user.org_id)
    result = (await db.execute(stmt)).scalars().all()
    return {
        "items": [
            {"id": ic.id, "provider": ic.provider, "is_active": ic.is_active}
            for ic in result
        ],
    }


@router.post("/sync/{provider}", summary="Trigger sync with an external provider")
async def trigger_sync(
    provider: str,
    user: Annotated[CurrentUser, Depends(require_role("admin", "scrum_master"))],
) -> dict:  # type: ignore[type-arg]
    """Enqueue a background sync job for the given provider."""
    # TODO: enqueue ARQ task
    return {"status": "queued", "provider": provider}
