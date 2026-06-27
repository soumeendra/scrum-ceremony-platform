"""Ceremonies API – ceremony lifecycle and facilitator endpoints."""

from __future__ import annotations

from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import CurrentUser, require_role
from app.models.ceremony import Ceremony, CeremonyStateEnum
from app.services.anonymity import AnonymityConfig, AnonymityEngine

router = APIRouter()

VALID_TRANSITIONS = {
    "draft": ["collect"],
    "collect": ["cluster", "vote", "action"],
    "cluster": ["vote", "action"],
    "vote": ["discuss", "action"],
    "discuss": ["action"],
    "action": ["completed"],
    "completed": [],
}


@router.get("/", summary="List ceremonies")
async def list_ceremonies(
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """Return ceremonies for the current tenant."""
    stmt = (
        select(Ceremony)
        .where(Ceremony.tenant_id == user.org_id)
        .order_by(Ceremony.created_at.desc())
    )
    result = (await db.execute(stmt)).scalars().all()
    return {
        "items": [
            {
                "id": c.id,
                "title": c.title,
                "type": c.ceremony_type,
                "state": c.state,
                "current_phase": c.current_phase,
                "created_at": c.created_at,
            }
            for c in result
        ]
    }


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Create ceremony")
async def create_ceremony(
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    title: str,
    ceremony_type: str = "retrospective",
    team_id: str | None = None,
    template_id: str | None = None,
) -> dict:
    """Create a new ceremony."""
    ceremony = Ceremony(
        id=str(uuid4()),
        tenant_id=user.org_id,
        team_id=team_id,
        template_id=template_id,
        title=title,
        ceremony_type=ceremony_type,
    )
    db.add(ceremony)
    await db.flush()
    return {
        "id": ceremony.id,
        "title": ceremony.title,
        "state": ceremony.state,
        "current_phase": ceremony.current_phase,
    }


@router.get("/{ceremony_id}", summary="Get ceremony detail")
async def get_ceremony(
    ceremony_id: str,
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """Get ceremony details including anonymity config."""
    stmt = (
        select(Ceremony)
        .where(Ceremony.id == ceremony_id)
        .where(Ceremony.tenant_id == user.org_id)
    )
    ceremony = (await db.execute(stmt)).scalar_one_or_none()
    if not ceremony:
        raise HTTPException(status_code=404, detail="Ceremony not found")

    return {
        "id": ceremony.id,
        "title": ceremony.title,
        "type": ceremony.ceremony_type,
        "state": ceremony.state,
        "current_phase": ceremony.current_phase,
        "anonymity_config": AnonymityConfig.from_json(ceremony.anonymity_config),
        "team_id": ceremony.team_id,
        "template_id": ceremony.template_id,
        "created_at": ceremony.created_at,
    }


@router.post("/{ceremony_id}/advance", summary="Advance ceremony phase")
async def advance_phase(
    ceremony_id: str,
    user: Annotated[CurrentUser, Depends(require_role("facilitator", "org_admin"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """Advance the ceremony to the next phase (facilitator only)."""
    stmt = (
        select(Ceremony)
        .where(Ceremony.id == ceremony_id)
        .where(Ceremony.tenant_id == user.org_id)
    )
    ceremony = (await db.execute(stmt)).scalar_one_or_none()
    if not ceremony:
        raise HTTPException(status_code=404, detail="Ceremony not found")

    current = ceremony.current_phase
    valid_next = VALID_TRANSITIONS.get(current, [])

    if not valid_next:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot advance from '{current}' (terminal state)"
        )

    next_phase = valid_next[0]
    ceremony.current_phase = next_phase

    # Log state transition
    from app.models.ceremony import CeremonyState
    state_log = CeremonyState(
        ceremony_id=ceremony.id,
        tenant_id=user.org_id,
        from_state=current,
        to_state=next_phase,
        changed_by=user.id,
    )
    db.add(state_log)

    return {
        "id": ceremony.id,
        "current_phase": next_phase,
        "previous_phase": current,
    }


@router.patch("/{ceremony_id}/anonymity", summary="Update anonymity config")
async def update_anonymity(
    ceremony_id: str,
    user: Annotated[CurrentUser, Depends(require_role("facilitator", "org_admin"))],
    db: Annotated[AsyncSession, Depends(get_db)],
    collect: str | None = None,
    vote: str | None = None,
    discuss: str | None = None,
    quiet_mode: bool | None = None,
) -> dict:
    """Update anonymity configuration for a ceremony (facilitator only)."""
    stmt = (
        select(Ceremony)
        .where(Ceremony.id == ceremony_id)
        .where(Ceremony.tenant_id == user.org_id)
    )
    ceremony = (await db.execute(stmt)).scalar_one_or_none()
    if not ceremony:
        raise HTTPException(status_code=404, detail="Ceremony not found")

    config = AnonymityConfig.from_json(ceremony.anonymity_config)
    if collect:
        config.collect = collect
    if vote:
        config.vote = vote
    if discuss:
        config.discuss = discuss
    if quiet_mode is not None:
        config.quiet_mode = quiet_mode

    ceremony.anonymity_config = config.to_json()

    return {
        "id": ceremony.id,
        "anonymity_config": config,
    }


@router.get("/{ceremony_id}/participants", summary="Get participants")
async def get_participants(
    ceremony_id: str,
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """Get participant count and presence info for a ceremony."""
    # TODO: Return actual participant list from WebSocket room manager
    from app.ws.server import room_manager
    room = room_manager.get(ceremony_id)

    participants = []
    if room:
        for p in room.participants.values():
            participants.append({
                "user_id": p.user_id,
                "display_name": p.display_name,
                "connected_at": p.connected_at,
            })

    return {
        "ceremony_id": ceremony_id,
        "participant_count": len(participants),
        "participants": participants,
    }
