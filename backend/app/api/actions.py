"""Actions API – action item management endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import CurrentUser
from app.models.action import Action

router = APIRouter()


@router.get("/", summary="List actions")
async def list_actions(
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> dict:  # type: ignore[type-arg]
    """Return a paginated list of action items for the current tenant."""
    offset = (page - 1) * page_size
    stmt = (
        select(Action)
        .where(Action.tenant_id == user.org_id)
        .offset(offset)
        .limit(page_size)
    )
    result = (await db.execute(stmt)).scalars().all()
    return {
        "items": [
            {"id": a.id, "title": a.title, "status": a.status, "priority": a.priority}
            for a in result
        ],
        "page": page,
        "page_size": page_size,
    }
