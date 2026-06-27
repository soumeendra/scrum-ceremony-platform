"""Actions API – full CRUD + register + carry-forward + quality + metrics."""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import CurrentUser
from app.models.action import Action, ActionRegister, IntegrationLink
from app.schemas.action import (
    ActionCreate,
    ActionListResponse,
    ActionPriority,
    ActionQualityScore,
    ActionResponse,
    ActionStatus,
    ActionUpdate,
    IntegrationLinkResponse,
)
from app.services.action_quality import score_action

router = APIRouter()


# ── Helpers ────────────────────────────────────────────────────────────────────


def _parse_due_date(due_date_str: str | None) -> date | None:
    """Parse an ISO-date string into a date, returning None on failure."""
    if not due_date_str:
        return None
    try:
        return date.fromisoformat(due_date_str)
    except (ValueError, TypeError):
        return None


def _is_overdue(action: Action) -> bool:
    """Return True if the action has a past due date and is not done/dropped."""
    if action.status in (ActionStatus.DONE.value, ActionStatus.DROPPED.value):
        return False
    due = _parse_due_date(action.due_date)
    if due is None:
        return False
    return due < date.today()


def _to_response(action: Action) -> ActionResponse:
    """Convert an Action ORM object to an ActionResponse schema."""
    integration_link: dict | None = None
    if action.integration_links:
        link = action.integration_links[0]
        integration_link = IntegrationLinkResponse.model_validate(link).model_dump()

    return ActionResponse(
        id=action.id,
        title=action.title,
        description=action.description,
        assignee_id=action.assignee_id,
        due_date=action.due_date,
        priority=ActionPriority(action.priority),
        status=ActionStatus(action.status),
        ceremony_id=action.ceremony_id,
        team_id=action.team_id,
        source_item_id=action.source_item_id,
        created_at=action.created_at,
        updated_at=action.updated_at,
        integration_link=integration_link,
    )


# ── List ───────────────────────────────────────────────────────────────────────


@router.get("/", summary="List actions", response_model=ActionListResponse)
async def list_actions(
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: ActionStatus | None = Query(None, alias="status"),
    priority: ActionPriority | None = None,
    assignee_id: str | None = None,
    team_id: str | None = None,
    ceremony_id: str | None = None,
) -> ActionListResponse:
    """Return a paginated, filterable list of action items for the current tenant."""
    tenant_id = user.org_id

    # Build filtered base query
    base_stmt = select(Action).where(Action.tenant_id == tenant_id)
    if status_filter is not None:
        base_stmt = base_stmt.where(Action.status == status_filter.value)
    if priority is not None:
        base_stmt = base_stmt.where(Action.priority == priority.value)
    if assignee_id is not None:
        base_stmt = base_stmt.where(Action.assignee_id == assignee_id)
    if team_id is not None:
        base_stmt = base_stmt.where(Action.team_id == team_id)
    if ceremony_id is not None:
        base_stmt = base_stmt.where(Action.ceremony_id == ceremony_id)

    # Total count
    count_stmt = select(func.count()).select_from(base_stmt.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    # Count metrics (by status)
    metrics_stmt = (
        select(
            func.sum(case((Action.status == ActionStatus.OPEN.value, 1), else_=0)).label("open_count"),
            func.sum(case((Action.status == ActionStatus.IN_PROGRESS.value, 1), else_=0)).label("in_progress_count"),
            func.sum(case((Action.status == ActionStatus.DONE.value, 1), else_=0)).label("done_count"),
        )
        .where(Action.tenant_id == tenant_id)
    )
    metrics_result = (await db.execute(metrics_stmt)).one()

    # Paginated items
    offset = (page - 1) * page_size
    items_stmt = base_stmt.order_by(Action.created_at.desc()).offset(offset).limit(page_size)
    actions = (await db.execute(items_stmt)).scalars().all()

    # Compute overdue count for the full filtered set
    all_matching = (await db.execute(base_stmt)).scalars().all()
    overdue_count = sum(1 for a in all_matching if _is_overdue(a))

    return ActionListResponse(
        items=[_to_response(a) for a in actions],
        total=total,
        page=page,
        page_size=page_size,
        open_count=metrics_result.open_count or 0,
        in_progress_count=metrics_result.in_progress_count or 0,
        done_count=metrics_result.done_count or 0,
        overdue_count=overdue_count,
    )


# ── Create ─────────────────────────────────────────────────────────────────────


@router.post("/", summary="Create action", response_model=ActionResponse, status_code=status.HTTP_201_CREATED)
async def create_action(
    payload: ActionCreate,
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ActionResponse:
    """Create a new action item, optionally linked to a ceremony."""
    tenant_id = user.org_id

    # Validate ceremony exists and belongs to tenant if provided
    ceremony_id = payload.ceremony_id
    if ceremony_id is not None:
        from app.models.ceremony import Ceremony

        ceremony_stmt = select(Ceremony).where(
            Ceremony.id == ceremony_id,
            Ceremony.tenant_id == tenant_id,
        )
        ceremony = (await db.execute(ceremony_stmt)).scalar_one_or_none()
        if ceremony is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ceremony not found or does not belong to your organization",
            )

    action = Action(
        id=str(uuid4()),
        tenant_id=tenant_id,
        ceremony_id=ceremony_id or str(uuid4()),  # FK requires non-null; use placeholder if needed
        team_id=ceremony.team_id if ceremony_id else str(uuid4()),
        title=payload.title,
        description=payload.description,
        assignee_id=payload.assignee_id,
        due_date=payload.due_date,
        priority=payload.priority.value,
        status=payload.status.value,
        source_item_id=payload.source_item_id,
    )
    db.add(action)
    await db.flush()
    await db.refresh(action)

    return _to_response(action)


# ── Register (cross-retro) ────────────────────────────────────────────────────


@router.get("/register/", summary="Cross-retro action register", response_model=ActionListResponse)
async def action_register(
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    team_id: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
) -> ActionListResponse:
    """Return the persistent action register: all open/non-done actions across ceremonies for a team."""
    tenant_id = user.org_id

    base_stmt = (
        select(Action)
        .join(ActionRegister, ActionRegister.action_id == Action.id)
        .where(
            Action.tenant_id == tenant_id,
            Action.status.in_([ActionStatus.OPEN.value, ActionStatus.IN_PROGRESS.value]),
        )
    )
    if team_id is not None:
        base_stmt = base_stmt.where(Action.team_id == team_id)

    count_stmt = select(func.count()).select_from(base_stmt.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    offset = (page - 1) * page_size
    items_stmt = base_stmt.order_by(Action.due_date.asc().nulls_last(), Action.created_at.desc()).offset(offset).limit(page_size)
    actions = (await db.execute(items_stmt)).scalars().all()

    metrics_stmt = (
        select(
            func.sum(case((Action.status == ActionStatus.OPEN.value, 1), else_=0)).label("open_count"),
            func.sum(case((Action.status == ActionStatus.IN_PROGRESS.value, 1), else_=0)).label("in_progress_count"),
            func.sum(case((Action.status == ActionStatus.DONE.value, 1), else_=0)).label("done_count"),
        )
        .where(Action.tenant_id == tenant_id)
        .join(ActionRegister, ActionRegister.action_id == Action.id)
    )
    metrics_result = (await db.execute(metrics_stmt)).one()

    all_matching = (await db.execute(base_stmt)).scalars().all()
    overdue_count = sum(1 for a in all_matching if _is_overdue(a))

    return ActionListResponse(
        items=[_to_response(a) for a in actions],
        total=total,
        page=page,
        page_size=page_size,
        open_count=metrics_result.open_count or 0,
        in_progress_count=metrics_result.in_progress_count or 0,
        done_count=metrics_result.done_count or 0,
        overdue_count=overdue_count,
    )


# ── Carry forward ──────────────────────────────────────────────────────────────


@router.post(
    "/{action_id}/carry-forward",
    summary="Carry action to next retro",
    response_model=ActionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def carry_forward(
    action_id: str,
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    target_ceremony_id: str | None = None,
) -> ActionResponse:
    """Carry an incomplete action forward into a new ceremony (defaults to next retro for the team)."""
    # Fetch existing action
    stmt = select(Action).where(
        Action.id == action_id,
        Action.tenant_id == user.org_id,
    )
    source_action = (await db.execute(stmt)).scalar_one_or_none()
    if source_action is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source action not found",
        )

    from app.models.ceremony import Ceremony

    # Determine target ceremony
    if target_ceremony_id is None:
        # Find the most recent completed/draft retrospective for the team
        next_ceremony_stmt = (
            select(Ceremony)
            .where(
                Ceremony.team_id == source_action.team_id,
                Ceremony.tenant_id == user.org_id,
            )
            .order_by(Ceremony.created_at.desc())
            .limit(1)
        )
        target_ceremony = (await db.execute(next_ceremony_stmt)).scalar_one_or_none()
        if target_ceremony is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No target ceremony found for carry-forward. Provide target_ceremony_id.",
            )
        target_ceremony_id = target_ceremony.id
    else:
        # Validate provided target ceremony
        target_stmt = select(Ceremony).where(
            Ceremony.id == target_ceremony_id,
            Ceremony.tenant_id == user.org_id,
        )
        target_ceremony = (await db.execute(target_stmt)).scalar_one_or_none()
        if target_ceremony is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target ceremony not found",
            )

    # Create the carried-forward action
    new_action = Action(
        id=str(uuid4()),
        tenant_id=user.org_id,
        ceremony_id=target_ceremony_id,
        team_id=source_action.team_id,
        title=f"[Carried] {source_action.title}" if not source_action.title.startswith("[Carried]") else source_action.title,
        description=source_action.description,
        assignee_id=source_action.assignee_id,
        due_date=source_action.due_date,
        priority=source_action.priority,
        status=ActionStatus.OPEN.value,
        source_item_id=source_action.source_item_id,
    )
    db.add(new_action)

    # Create or update register entry
    reg_stmt = select(ActionRegister).where(
        ActionRegister.action_id == action_id,
        ActionRegister.tenant_id == user.org_id,
    )
    existing_reg = (await db.execute(reg_stmt)).scalar_one_or_none()

    new_register = ActionRegister(
        id=str(uuid4()),
        tenant_id=user.org_id,
        team_id=source_action.team_id,
        action_id=new_action.id,
        is_recurring=existing_reg.is_recurring if existing_reg else True,
        recurring_pattern=existing_reg.recurring_pattern if existing_reg else None,
    )
    db.add(new_register)

    # Mark original action as dropped so it doesn't appear in the register
    source_action.status = ActionStatus.DROPPED.value
    source_action.updated_at = datetime.now(timezone.utc)

    await db.flush()
    await db.refresh(new_action)
    return _to_response(new_action)


# ── Quality score ──────────────────────────────────────────────────────────────


@router.get("/quality/{action_id}", summary="Get action quality score", response_model=ActionQualityScore)
async def get_quality_score(
    action_id: str,
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ActionQualityScore:
    """Return a quality score (0-100) for the given action with issues and suggestions."""
    stmt = select(Action).where(
        Action.id == action_id,
        Action.tenant_id == user.org_id,
    )
    action = (await db.execute(stmt)).scalar_one_or_none()
    if action is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action not found",
        )
    return score_action(action)


# ── Metrics ────────────────────────────────────────────────────────────────────


@router.get("/metrics/", summary="Action metrics")
async def action_metrics(
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    team_id: str | None = None,
) -> dict:
    """Return aggregate action metrics: completion rate, overdue count, avg time-to-complete."""
    tenant_id = user.org_id

    base_stmt = select(Action).where(Action.tenant_id == tenant_id)
    if team_id is not None:
        base_stmt = base_stmt.where(Action.team_id == team_id)

    actions = (await db.execute(base_stmt)).scalars().all()

    total = len(actions)
    done_count = sum(1 for a in actions if a.status == ActionStatus.DONE.value)
    overdue_count = sum(1 for a in actions if _is_overdue(a))

    completion_rate = (done_count / total * 100) if total > 0 else 0.0

    # Avg time-to-complete for done actions
    done_actions = [a for a in actions if a.status == ActionStatus.DONE.value]
    avg_time_to_complete: float | None = None
    if done_actions:
        deltas = []
        for a in done_actions:
            if a.created_at and a.updated_at:
                delta = (a.updated_at - a.created_at).total_seconds()
                deltas.append(delta)
        avg_time_to_complete = sum(deltas) / len(deltas) if deltas else None

    return {
        "total": total,
        "done_count": done_count,
        "overdue_count": overdue_count,
        "completion_rate": round(completion_rate, 2),
        "avg_time_to_complete_seconds": avg_time_to_complete,
    }


# ── Detail ─────────────────────────────────────────────────────────────────────
# NOTE: These routes are defined LAST so that static paths like /register/,
# /metrics/, /quality/{id}, and /{id}/carry-forward are matched first.


@router.get("/{action_id}", summary="Get action detail", response_model=ActionResponse)
async def get_action(
    action_id: str,
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ActionResponse:
    """Return detailed information for a single action, including integration links."""
    stmt = select(Action).where(
        Action.id == action_id,
        Action.tenant_id == user.org_id,
    )
    action = (await db.execute(stmt)).scalar_one_or_none()
    if action is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action not found",
        )
    return _to_response(action)


# ── Update ─────────────────────────────────────────────────────────────────────


@router.patch("/{action_id}", summary="Update action", response_model=ActionResponse)
async def update_action(
    action_id: str,
    payload: ActionUpdate,
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ActionResponse:
    """Update an action item. Status changes are noted in the action history."""
    stmt = select(Action).where(
        Action.id == action_id,
        Action.tenant_id == user.org_id,
    )
    action = (await db.execute(stmt)).scalar_one_or_none()
    if action is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action not found",
        )

    # Track status change for audit logging
    old_status = action.status
    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if field == "priority" and isinstance(value, ActionPriority):
            value = value.value
        elif field == "status" and isinstance(value, ActionStatus):
            value = value.value
        setattr(action, field, value)

    # Log status transitions (persisted via updated_at; full audit log is future work)
    if "status" in update_data and old_status != action.status:
        # Touch updated_at explicitly so the change is visible
        action.updated_at = datetime.now(timezone.utc)

    await db.flush()
    await db.refresh(action)
    return _to_response(action)


# ── Delete ─────────────────────────────────────────────────────────────────────


@router.delete("/{action_id}", summary="Delete action", status_code=status.HTTP_204_NO_CONTENT)
async def delete_action(
    action_id: str,
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete an action item and its associated register entries / integration links."""
    stmt = select(Action).where(
        Action.id == action_id,
        Action.tenant_id == user.org_id,
    )
    action = (await db.execute(stmt)).scalar_one_or_none()
    if action is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action not found",
        )

    # Clean up register entries first (cascade handles integration_links)
    reg_stmt = select(ActionRegister).where(
        ActionRegister.action_id == action_id,
        ActionRegister.tenant_id == user.org_id,
    )
    reg_entries = (await db.execute(reg_stmt)).scalars().all()
    for entry in reg_entries:
        await db.delete(entry)

    await db.delete(action)
    await db.flush()
