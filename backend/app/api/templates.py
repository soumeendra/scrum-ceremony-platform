"""Templates API – ceremony template management endpoints."""

from __future__ import annotations

from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import ClerkUser
from app.models.template import Template
from app.schemas.template import (
    TemplateCreate,
    TemplateListResponse,
    TemplateResponse,
    TemplateUpdate,
    TemplateScope,
    CeremonyType,
)

router = APIRouter()

# ── Built-in default templates ─────────────────────────────────────────────────

DEFAULT_TEMPLATES = [
    {
        "id": "default-retro-1",
        "name": "Start / Stop / Continue",
        "ceremony_type": "retrospective",
        "scope": "org",
        "owner_id": None,
        "phases": [
            {"name": "reflection", "description": "Reflect on the sprint"},
            {"name": "sharing", "description": "Share reflections with the team"},
            {"name": "action", "description": "Define action items"},
        ],
        "columns": [
            {"key": "start", "label": "Start", "color": "#ef4444"},
            {"key": "stop", "label": "Stop", "color": "#f59e0b"},
            {"key": "continue", "label": "Continue", "color": "#10b981"},
        ],
        "is_locked": True,
        "is_default": True,
    },
    {
        "id": "default-retro-2",
        "name": "Mad / Sad / Glad",
        "ceremony_type": "retrospective",
        "scope": "org",
        "owner_id": None,
        "phases": [
            {"name": "reflection", "description": "Reflect on emotions"},
            {"name": "sharing", "description": "Share with the team"},
            {"name": "voting", "description": "Vote on important items"},
            {"name": "actions", "description": "Define next steps"},
        ],
        "columns": [
            {"key": "mad", "label": "Mad", "color": "#dc2626"},
            {"key": "sad", "label": "Sad", "color": "#2563eb"},
            {"key": "glad", "label": "Glad", "color": "#16a34a"},
        ],
        "is_locked": True,
        "is_default": True,
    },
    {
        "id": "default-retro-3",
        "name": "4Ls: Liked / Learned / Lacked / Longed For",
        "ceremony_type": "retrospective",
        "scope": "org",
        "owner_id": None,
        "phases": [
            {"name": "individual", "description": "Write down thoughts"},
            {"name": "group", "description": "Group similar items"},
            {"name": "discuss", "description": "Discuss as a team"},
            {"name": "decide", "description": "Decide on actions"},
        ],
        "columns": [
            {"key": "liked", "label": "Liked", "color": "#10b981"},
            {"key": "learned", "label": "Learned", "color": "#3b82f6"},
            {"key": "lacked", "label": "Lacked", "color": "#f59e0b"},
            {"key": "longed_for", "label": "Longed For", "color": "#8b5cf6"},
        ],
        "is_locked": True,
        "is_default": True,
    },
    {
        "id": "default-standup-1",
        "name": "Daily Standup",
        "ceremony_type": "standup",
        "scope": "org",
        "owner_id": None,
        "phases": [
            {"name": "round_robin", "description": "Each member gives an update"},
            {"name": "blockers", "description": "Discuss blockers"},
        ],
        "columns": [
            {"key": "yesterday", "label": "Yesterday", "color": "#6b7280"},
            {"key": "today", "label": "Today", "color": "#0ea5e9"},
            {"key": "blockers", "label": "Blockers", "color": "#ef4444"},
        ],
        "is_locked": True,
        "is_default": True,
    },
    {
        "id": "default-planning-1",
        "name": "Sprint Planning",
        "ceremony_type": "planning",
        "scope": "org",
        "owner_id": None,
        "phases": [
            {"name": "review", "description": "Review sprint goal and capacity"},
            {"name": "select", "description": "Select backlog items"},
            {"name": "decompose", "description": "Decompose into tasks"},
            {"name": "commit", "description": "Team commits to the sprint"},
        ],
        "columns": [
            {"key": "todo", "label": "To Do", "color": "#6b7280"},
            {"key": "in_progress", "label": "In Progress", "color": "#f59e0b"},
            {"key": "done", "label": "Done", "color": "#10b981"},
        ],
        "is_locked": True,
        "is_default": True,
    },
]


# ── Tenant helper ──────────────────────────────────────────────────────────────


def _tenant_id(user: ClerkUser) -> str:
    """Extract the tenant_id from the authenticated user."""
    if not user.org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with any organization",
        )
    return user.org_id


# ── List templates ─────────────────────────────────────────────────────────────


@router.get(
    "/",
    response_model=TemplateListResponse,
    summary="List templates",
    description="Return a paginated list of ceremony templates for the current tenant (includes org, workspace, and team-scoped templates).",
)
async def list_templates(
    user: Annotated[ClerkUser, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    ceremony_type: Annotated[CeremonyType | None, Query()] = None,
) -> TemplateListResponse:
    """List templates for the current tenant with pagination."""
    tenant = _tenant_id(user)
    offset = (page - 1) * page_size

    # Build base query
    base_where = [Template.tenant_id == tenant]
    if ceremony_type is not None:
        base_where.append(
            Template.ceremony_type
            if isinstance(ceremony_type, str)
            else Template.ceremony_type == ceremony_type.value
        )

    # Count total
    count_stmt = select(func.count()).select_from(Template)
    for clause in base_where:
        count_stmt = count_stmt.where(clause)
    total = (await db.execute(count_stmt)).scalar() or 0

    # Fetch paginated
    data_stmt = select(Template)
    for clause in base_where:
        data_stmt = data_stmt.where(clause)
    data_stmt = data_stmt.order_by(Template.created_at.desc()).offset(offset).limit(page_size)
    templates = (await db.execute(data_stmt)).scalars().all()

    items = [
        TemplateResponse(
            id=str(t.id),
            name=t.name,
            ceremony_type=t.ceremony_type,
            scope=TemplateScope(t.scope) if t.scope else TemplateScope.TEAM,
            owner_id=getattr(t, "owner_id", None),
            phases=_parse_json_field(t.structure, "phases"),
            columns=_parse_json_field(t.structure, "columns"),
            is_locked=getattr(t, "is_locked", False) or t.is_default,
            is_default=t.is_default,
            created_at=t.created_at,
        )
        for t in templates
    ]

    return TemplateListResponse(items=items, total=total, page=page, page_size=page_size)


# ── Get default templates ──────────────────────────────────────────────────────


@router.get(
    "/defaults",
    response_model=list[TemplateResponse],
    summary="Get default templates",
    description="Return the 5 built-in default ceremony templates.",
)
async def get_default_templates() -> list[TemplateResponse]:
    """Return the 5 built-in default templates."""
    return [
        TemplateResponse(
            id=t["id"],
            name=t["name"],
            ceremony_type=t["ceremony_type"],
            scope=TemplateScope(t["scope"]),
            owner_id=t["owner_id"],
            phases=t["phases"],
            columns=t["columns"],
            is_locked=t["is_locked"],
            is_default=t["is_default"],
            created_at=None,  # type: ignore[arg-type]
        )
        for t in DEFAULT_TEMPLATES
    ]


# ── Create template ────────────────────────────────────────────────────────────


@router.post(
    "/",
    response_model=TemplateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create custom template",
    description="Create a new custom ceremony template.",
)
async def create_template(
    body: TemplateCreate,
    user: Annotated[ClerkUser, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TemplateResponse:
    """Create a custom template for the current tenant."""
    tenant = _tenant_id(user)

    template = Template(
        id=str(uuid4()),
        tenant_id=tenant,
        name=body.name,
        ceremony_type=body.ceremony_type.value
        if hasattr(body.ceremony_type, "value")
        else str(body.ceremony_type),
        description=None,
        structure=_build_structure(body.phases, body.columns),
        is_default=False,
    )
    db.add(template)
    await db.flush()
    await db.refresh(template)

    return TemplateResponse(
        id=str(template.id),
        name=template.name,
        ceremony_type=template.ceremony_type,
        scope=body.scope,
        owner_id=body.owner_id or user.id,
        phases=body.phases,
        columns=body.columns,
        is_locked=body.is_locked,
        is_default=False,
        created_at=template.created_at,
    )


# ── Get template detail ────────────────────────────────────────────────────────


@router.get(
    "/{template_id}",
    response_model=TemplateResponse,
    summary="Get template detail",
    description="Retrieve a single template by ID.",
)
async def get_template(
    template_id: str,
    user: Annotated[ClerkUser, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TemplateResponse:
    """Get a template by ID. Tenant-scoped."""
    tenant = _tenant_id(user)

    template = (
        await db.execute(
            select(Template).where(
                Template.id == template_id, Template.tenant_id == tenant
            )
        )
    ).scalar_one_or_none()
    if template is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )

    return TemplateResponse(
        id=str(template.id),
        name=template.name,
        ceremony_type=template.ceremony_type,
        scope=TemplateScope(template.scope) if hasattr(template, "scope") else TemplateScope.TEAM,
        owner_id=getattr(template, "owner_id", None),
        phases=_parse_json_field(template.structure, "phases"),
        columns=_parse_json_field(template.structure, "columns"),
        is_locked=getattr(template, "is_locked", False) or template.is_default,
        is_default=template.is_default,
        created_at=template.created_at,
    )


# ── Update template ────────────────────────────────────────────────────────────


@router.patch(
    "/{template_id}",
    response_model=TemplateResponse,
    summary="Update template",
    description="Update a template. Cannot update locked templates.",
)
async def update_template(
    template_id: str,
    body: TemplateUpdate,
    user: Annotated[ClerkUser, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TemplateResponse:
    """Update a template. Only allowed if the template is not locked."""
    tenant = _tenant_id(user)

    template = (
        await db.execute(
            select(Template).where(
                Template.id == template_id, Template.tenant_id == tenant
            )
        )
    ).scalar_one_or_none()
    if template is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )

    # Cannot update locked or default templates
    is_locked = getattr(template, "is_locked", False) or template.is_default
    if is_locked:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot update a locked or default template",
        )

    update_data = body.model_dump(exclude_unset=True)

    # Merge phases/columns into structure JSON
    if "phases" in update_data or "columns" in update_data:
        current_phases = _parse_json_field(template.structure, "phases")
        current_columns = _parse_json_field(template.structure, "columns")
        new_phases = update_data.pop("phases", current_phases)
        new_columns = update_data.pop("columns", current_columns)
        template.structure = _build_structure(new_phases, new_columns)

    for field, value in update_data.items():
        if field == "ceremony_type" and value is not None:
            value = value.value if hasattr(value, "value") else str(value)
        setattr(template, field, value)

    await db.flush()
    await db.refresh(template)

    return TemplateResponse(
        id=str(template.id),
        name=template.name,
        ceremony_type=template.ceremony_type,
        scope=TemplateScope(template.scope) if hasattr(template, "scope") else TemplateScope.TEAM,
        owner_id=getattr(template, "owner_id", None),
        phases=_parse_json_field(template.structure, "phases"),
        columns=_parse_json_field(template.structure, "columns"),
        is_locked=getattr(template, "is_locked", False) or template.is_default,
        is_default=template.is_default,
        created_at=template.created_at,
    )


# ── Delete template ────────────────────────────────────────────────────────────


@router.delete(
    "/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete template",
    description="Delete a custom template. Cannot delete locked or default templates.",
)
async def delete_template(
    template_id: str,
    user: Annotated[ClerkUser, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete a custom template. Not allowed for locked or default templates."""
    tenant = _tenant_id(user)

    template = (
        await db.execute(
            select(Template).where(
                Template.id == template_id, Template.tenant_id == tenant
            )
        )
    ).scalar_one_or_none()
    if template is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )

    if template.is_default:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete a default template",
        )

    is_locked = getattr(template, "is_locked", False)
    if is_locked:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete a locked template",
        )

    await template.delete()
    await db.flush()


# ── Helpers ────────────────────────────────────────────────────────────────────


def _parse_json_field(structure: str | dict | None, key: str) -> list[dict]:
    """Parse a JSON structure field and return a list for the given key."""
    import json

    if structure is None:
        return []
    if isinstance(structure, dict):
        return structure.get(key, [])  # type: ignore[return-value]
    try:
        parsed = json.loads(structure)
        return parsed.get(key, [])  # type: ignore[return-value]
    except (json.JSONDecodeError, TypeError):
        return []


def _build_structure(phases: list[dict], columns: list[dict]) -> str:
    """Build a JSON string for the template structure."""
    import json

    return json.dumps({"phases": phases, "columns": columns})
