"""Teams API – CRUD and membership endpoints."""

from __future__ import annotations

from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import CurrentUser, require_role
from app.models.team import Team, TeamMember

router = APIRouter()


# ── Placeholder schemas (replace with Pydantic schemas in app/schemas/) ────────
# These minimal inline schemas are scaffolds; replace with proper versions.


@router.get("/", summary="List teams")
async def list_teams(
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> dict:  # type: ignore[type-arg]
    """Return a paginated list of teams for the current tenant."""
    offset = (page - 1) * page_size
    stmt = select(Team).where(Team.tenant_id == user.org_id).offset(offset).limit(page_size)
    count_stmt = select(func.count()).select_from(Team).where(Team.tenant_id == user.org_id)

    total = (await db.execute(count_stmt)).scalar() or 0
    result = (await db.execute(stmt)).scalars().all()

    return {
        "items": [{"id": t.id, "name": t.name, "is_active": t.is_active} for t in result],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Create team")
async def create_team(
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    name: str = ...,
    description: str | None = None,
) -> dict:  # type: ignore[type-arg]
    """Create a new team under the current tenant."""
    team = Team(
        id=str(uuid4()),
        tenant_id=user.org_id,
        name=name,
        description=description,
    )
    db.add(team)
    await db.flush()
    return {"id": team.id, "name": team.name}
