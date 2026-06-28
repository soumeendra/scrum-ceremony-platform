"""Planning poker API endpoints."""

from __future__ import annotations

from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException

from app.core.database import get_db
from app.core.security import CurrentUser
from app.models.ceremony import Ceremony
from app.services.poker import PokerService

router = APIRouter()


@router.post("/", summary="Create planning poker session")
async def create_poker_session(
    user: CurrentUser,
    db: Annotated[any, Depends(get_db)],
    title: str = "Sprint Planning Poker",
    stories: list[str] | None = None,
) -> dict:
    """Create a new planning poker session."""
    ceremony = Ceremony(
        id=str(uuid4()),
        team_id="",
        tenant_id=user.org_id or "",
        title=title,
        ceremony_type="planning_poker",
        current_phase="story_selection",
    )
    db.add(ceremony)
    await db.flush()

    return {
        "id": ceremony.id,
        "title": title,
        "type": "planning_poker",
        "current_phase": ceremony.current_phase,
        "stories": stories or [],
        "estimate_options": ["1", "2", "3", "5", "8", "13", "21", "?"],
    }


@router.post("/{session_id}/estimate", summary="Submit estimate")
async def submit_estimate(
    session_id: str,
    user: CurrentUser,
    story_id: str,
    estimate: str,
) -> dict:
    """Submit a hidden estimate for a story."""
    valid = ["1", "2", "3", "5", "8", "13", "21", "?"]
    if estimate not in valid:
        raise HTTPException(status_code=400, detail=f"Estimate must be one of: {valid}")

    return {
        "session_id": session_id,
        "story_id": story_id,
        "submitted": True,
        "estimate": estimate,
    }


@router.post("/{session_id}/reveal", summary="Reveal estimates")
async def reveal_estimates(
    session_id: str,
    user: CurrentUser,
    story_id: str,
) -> dict:
    """Reveal all estimates for a story (facilitator only)."""
    # In production: fetch estimates from DB, compute consensus
    return {
        "session_id": session_id,
        "story_id": story_id,
        "revealed": True,
        "estimates": [],
        "consensus": None,
        "has_consensus": False,
    }


@router.get("/{session_id}", summary="Get poker session")
async def get_poker_session(
    session_id: str,
    user: CurrentUser,
) -> dict:
    """Get poker session details."""
    return {
        "id": session_id,
        "type": "planning_poker",
        "current_phase": "story_selection",
    }
