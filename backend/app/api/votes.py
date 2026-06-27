"""Voting API — dot voting with anonymous voter tokens."""

from __future__ import annotations

from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import CurrentUser
from app.models.ceremony import BoardItem, Vote

router = APIRouter()


@router.post("/{ceremony_id}/vote", summary="Cast a vote")
async def cast_vote(
    ceremony_id: str,
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    item_id: str,
    voter_token: str | None = None,
) -> dict:
    """Cast a dot vote on a board item.

    For anonymous voting, provide a voter_token (per-ceremony UUID).
    For named voting, user_id is used.
    """
    # Verify item exists and belongs to tenant
    item_stmt = select(BoardItem).where(
        BoardItem.id == item_id,
        BoardItem.tenant_id == user.org_id,
    )
    item = (await db.execute(item_stmt)).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Use voter_token for anonymous, user_id for named
    token = voter_token or user.id

    # Check for duplicate vote
    existing = await db.execute(
        select(Vote).where(
            Vote.board_item_id == item_id,
            Vote.voter_token == token,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Already voted on this item")

    # Create vote
    vote = Vote(
        board_item_id=item_id,
        ceremony_id=ceremony_id,
        tenant_id=user.org_id,
        user_id=user.id if not voter_token else None,
        voter_token=token,
        value=1,
    )
    db.add(vote)
    await db.flush()

    # Get total votes for this item
    total = await db.execute(
        select(func.count()).where(Vote.board_item_id == item_id)
    )
    vote_count = total.scalar() or 0

    return {
        "item_id": item_id,
        "total_votes": vote_count,
        "voted": True,
    }


@router.delete("/{ceremony_id}/vote", summary="Remove a vote")
async def remove_vote(
    ceremony_id: str,
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    item_id: str,
    voter_token: str | None = None,
) -> dict:
    """Remove a vote from a board item."""
    token = voter_token or user.id

    vote = await db.execute(
        select(Vote).where(
            Vote.board_item_id == item_id,
            Vote.voter_token == token,
            Vote.tenant_id == user.org_id,
        )
    )
    vote_record = vote.scalar_one_or_none()
    if not vote_record:
        raise HTTPException(status_code=404, detail="Vote not found")

    await db.delete(vote_record)

    # Get updated count
    total = await db.execute(
        select(func.count()).where(Vote.board_item_id == item_id)
    )
    vote_count = total.scalar() or 0

    return {
        "item_id": item_id,
        "total_votes": vote_count,
        "voted": False,
    }


@router.get("/{ceremony_id}/vote/results", summary="Get voting results")
async def vote_results(
    ceremony_id: str,
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """Get vote counts for all items in a ceremony."""
    stmt = (
        select(Vote.board_item_id, func.count().label("vote_count"))
        .where(Vote.tenant_id == user.org_id)
        .group_by(Vote.board_item_id)
    )
    results = (await db.execute(stmt)).all()

    return {
        "results": [
            {"item_id": row.board_item_id, "votes": row.vote_count}
            for row in results
        ]
    }


@router.get("/{ceremony_id}/vote/token", summary="Get voter token")
async def get_voter_token(
    ceremony_id: str,
    user: CurrentUser,
) -> dict:
    """Generate/retrieve a voter token for the current user in this ceremony.

    The token is a per-ceremony UUID that prevents double-voting
    without storing the user's identity in the vote record.
    """
    # In production, tokens would be stored per-user per-ceremony
    # For now, derive from user_id + ceremony_id
    import hashlib
    token = hashlib.sha256(f"{user.id}:{ceremony_id}".encode()).hexdigest()[:36]

    return {
        "voter_token": token,
        "ceremony_id": ceremony_id,
    }
