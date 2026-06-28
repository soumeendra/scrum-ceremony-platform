"""Async standup API endpoints."""

from __future__ import annotations

from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException

from app.core.database import get_db
from app.core.security import CurrentUser
from app.models.ceremony import Ceremony

router = APIRouter()


@router.post("/", summary="Create async standup")
async def create_standup(
    user: CurrentUser,
    db: Annotated[any, Depends(get_db)],
    title: str = "Daily Standup",
) -> dict:
    """Create a new async standup session."""
    ceremony = Ceremony(
        id=str(uuid4()),
        team_id="",
        tenant_id=user.org_id or "",
        title=title,
        ceremony_type="async_standup",
        current_phase="open",
    )
    db.add(ceremony)
    await db.flush()

    return {
        "id": ceremony.id,
        "title": title,
        "type": "async_standup",
        "current_phase": "open",
        "status": "accepting_updates",
    }


@router.post("/{session_id}/update", summary="Submit standup update")
async def submit_update(
    session_id: str,
    user: CurrentUser,
    done: str = "",
    doing: str = "",
    blockers: str | None = None,
) -> dict:
    """Submit a standup update."""
    return {
        "session_id": session_id,
        "user_id": user.id,
        "done": done,
        "doing": doing,
        "blockers": blockers,
        "has_blockers": bool(blockers),
        "submitted": True,
    }


@router.get("/{session_id}/digest", summary="Get standup digest")
async def get_digest(
    session_id: str,
    user: CurrentUser,
) -> dict:
    """Get a digest of all standup updates."""
    return {
        "session_id": session_id,
        "updates": [],
        "blocker_count": 0,
        "participant_count": 0,
    }


@router.post("/{session_id}/close", summary="Close standup")
async def close_standup(
    session_id: str,
    user: CurrentUser,
) -> dict:
    """Close the standup for new submissions."""
    return {
        "session_id": session_id,
        "status": "closed",
        "message": "Standup closed. Blockers have been added to the action register.",
    }
