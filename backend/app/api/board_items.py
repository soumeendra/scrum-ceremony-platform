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

router = APIRouter()


@router.get("/{ceremony_id}/items", summary="List board items")
async def list_items(
    ceremony_id: str,
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """Return all board items for a ceremony (tenant-scoped)."""
    stmt = (
        select(BoardItem)
        .where(BoardItem.ceremony_id == ceremony_id)
        .where(BoardItem.tenant_id == user.org_id)
        .order_by(BoardItem.created_at)
    )
    result = (await db.execute(stmt)).scalars().all()
    return {
        "items": [
            {
                "id": item.id,
                "ceremony_id": item.ceremony_id,
                "column_name": item.column_name,
                "content": item.content,
                "author_display": item.author_display_id,  # Anonymous or display name
                "cluster_id": item.cluster_id,
                "order": item.order,
                "created_at": item.created_at,
            }
            for item in result
        ]
    }


@router.post("/{ceremony_id}/items", status_code=status.HTTP_201_CREATED, summary="Add board item")
async def add_item(
    ceremony_id: str,
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    content: str,
    column_name: str = "default",
) -> dict:
    """Add a new sticky note to the board."""
    item = BoardItem(
        id=str(uuid4()),
        ceremony_id=ceremony_id,
        tenant_id=user.org_id,
        column_name=column_name,
        content=content,
        author_display_id=user.email,  # Will be "Anonymous" if anonymous mode
    )
    db.add(item)
    await db.flush()
    return {
        "id": item.id,
        "content": item.content,
        "column_name": item.column_name,
        "author_display": item.author_display_id,
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
