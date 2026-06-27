"""Board Items API – CRUD for sticky notes on the ceremony board."""

from __future__ import annotations

from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import CurrentUser
from app.models.ceremony import BoardItem
from app.services.anonymity import AnonymityEngine

router = APIRouter()


@router.get("/{ceremony_id}/items", summary="List board items")
async def list_items(
    ceremony_id: str,
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """Return all board items for a ceremony (anonymized)."""
    items = await AnonymityEngine.get_display_items(db, ceremony_id)
    return {"items": items}


@router.post("/{ceremony_id}/items", status_code=status.HTTP_201_CREATED, summary="Add board item")
async def add_item(
    ceremony_id: str,
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    content: str,
    column_name: str = "default",
    is_anonymous: bool = False,
) -> dict:
    """Add a new sticky note to the board (with optional anonymity)."""
    item = await AnonymityEngine.create_board_item(
        db=db,
        ceremony_id=ceremony_id,
        tenant_id=user.org_id,
        content=content,
        column_name=column_name,
        user_id=user.id,
        is_anonymous=is_anonymous,
    )
    return {
        "id": item.id,
        "content": item.content,
        "column_name": item.column_name,
        "is_anonymous": item.is_anonymous,
        "author_display": "Anonymous" if item.is_anonymous else item.author_display,
    }


@router.delete("/{ceremony_id}/items/{item_id}", summary="Delete board item")
async def delete_item(
    ceremony_id: str,
    item_id: str,
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """Delete a board item (only by author or facilitator)."""
    stmt = (
        select(BoardItem)
        .where(BoardItem.id == item_id)
        .where(BoardItem.tenant_id == user.org_id)
    )
    item = (await db.execute(stmt)).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    await db.delete(item)
    return {"deleted": item_id}
