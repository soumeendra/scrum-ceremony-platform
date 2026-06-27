"""Ceremonies API – ceremony lifecycle endpoints."""

from __future__ import annotations

from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import CurrentUser
from app.models.ceremony import Ceremony

router = APIRouter()


@router.get("/", summary="List ceremonies")
async def list_ceremonies(
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> dict:  # type: ignore[type-arg]
    """Return a paginated list of ceremonies for the current tenant."""
    offset = (page - 1) * page_size
    stmt = (
        select(Ceremony)
        .where(Ceremony.tenant_id == user.org_id)
        .offset(offset)
        .limit(page_size)
    )
    result = (await db.execute(stmt)).scalars().all()
    return {
        "items": [
            {"id": c.id, "title": c.title, "state": c.state, "ceremony_type": c.ceremony_type}
            for c in result
        ],
        "page": page,
        "page_size": page_size,
    }


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Create ceremony")
async def create_ceremony(
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    title: str = ...,
    ceremony_type: str = ...,
    team_id: str = ...,
) -> dict:  # type: ignore[type-arg]
    """Create a new ceremony."""
    ceremony = Ceremony(
        id=str(uuid4()),
        tenant_id=user.org_id,
        title=title,
        ceremony_type=ceremony_type,
        team_id=team_id,
    )
    db.add(ceremony)
    await db.flush()
    return {"id": ceremony.id, "title": ceremony.title, "state": ceremony.state}
