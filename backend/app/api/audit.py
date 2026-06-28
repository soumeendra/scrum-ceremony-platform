"""Audit log API — immutable audit trail for compliance and debugging."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.core.security import CurrentUser, require_role
from app.models.integration import AuditEvent

router = APIRouter()


@router.get("/audit", summary="List audit events")
async def list_audit_events(
    user: Annotated[CurrentUser, Depends(require_role("org_admin", "workspace_admin"))],
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    action: str | None = Query(None, description="Filter by action type"),
    resource_type: str | None = Query(None, description="Filter by resource type"),
    actor_id: str | None = Query(None, description="Filter by actor"),
) -> dict:
    """List audit events with filtering and pagination (admin only)."""
    async with async_session_factory() as session:
        query = select(AuditEvent).where(AuditEvent.tenant_id == user.org_id)

        if action:
            query = query.where(AuditEvent.action == action)
        if resource_type:
            query = query.where(AuditEvent.resource_type == resource_type)
        if actor_id:
            query = query.where(AuditEvent.actor_id == actor_id)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = (await session.execute(count_query)).scalar() or 0

        # Paginate
        offset = (page - 1) * page_size
        query = query.order_by(AuditEvent.created_at.desc()).offset(offset).limit(page_size)

        result = await session.execute(query)
        events = result.scalars().all()

    return {
        "items": [
            {
                "id": e.id,
                "actor_id": e.actor_id,
                "action": e.action,
                "resource_type": e.resource_type,
                "resource_id": e.resource_id,
                "detail": e.detail,
                "created_at": e.created_at,
            }
            for e in events
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/audit/{event_id}", summary="Get audit event detail")
async def get_audit_event(
    event_id: str,
    user: Annotated[CurrentUser, Depends(require_role("org_admin"))],
) -> dict:
    """Get a specific audit event (admin only)."""
    async with async_session_factory() as session:
        result = await session.execute(
            select(AuditEvent)
            .where(AuditEvent.id == event_id)
            .where(AuditEvent.tenant_id == user.org_id)
        )
        event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(status_code=404, detail="Audit event not found")

    return {
        "id": event.id,
        "actor_id": event.actor_id,
        "action": event.action,
        "resource_type": event.resource_type,
        "resource_id": event.resource_id,
        "detail": event.detail,
        "created_at": event.created_at,
    }


@router.post("/audit/log", summary="Log an audit event")
async def log_audit_event(
    user: CurrentUser,
    action: str,
    resource_type: str,
    resource_id: str,
    detail: str | None = None,
) -> dict:
    """Log a new audit event (system use, requires authentication)."""
    async with async_session_factory() as session:
        event = AuditEvent(
            actor_id=user.id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            tenant_id=user.org_id or "",
            detail=detail,
        )
        session.add(event)
        await session.commit()

    return {"id": event.id, "logged": True}
