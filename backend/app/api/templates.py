"""Templates API – ceremony template management endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import CurrentUser
from app.models.template import Template

router = APIRouter()


@router.get("/", summary="List templates")
async def list_templates(
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> dict:  # type: ignore[type-arg]
    """Return a paginated list of ceremony templates for the current tenant."""
    offset = (page - 1) * page_size
    stmt = (
        select(Template)
        .where(Template.tenant_id == user.org_id)
        .offset(offset)
        .limit(page_size)
    )
    result = (await db.execute(stmt)).scalars().all()
    return {
        "items": [
            {"id": t.id, "name": t.name, "ceremony_type": t.ceremony_type}
            for t in result
        ],
        "page": page,
        "page_size": page_size,
    }
