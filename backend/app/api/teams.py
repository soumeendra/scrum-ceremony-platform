"""Teams API – CRUD and membership endpoints."""

from __future__ import annotations

from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import ClerkUser, require_role
from app.models.team import Team, TeamMember
from app.models.user import User
from app.schemas.team import (
    TeamCreate,
    TeamListResponse,
    TeamMemberCreate,
    TeamMemberResponse,
    TeamResponse,
    TeamUpdate,
)

router = APIRouter()


# ── Tenant helper ──────────────────────────────────────────────────────────────


def _tenant_id(user: ClerkUser) -> str:
    """Extract the tenant_id from the authenticated user."""
    if not user.org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with any organization",
        )
    return user.org_id


# ── List teams ─────────────────────────────────────────────────────────────────


@router.get(
    "/",
    response_model=TeamListResponse,
    summary="List teams",
    description="Return a paginated list of teams scoped to the current tenant.",
)
async def list_teams(
    user: Annotated[ClerkUser, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> TeamListResponse:
    """List teams for the current tenant with pagination."""
    tenant = _tenant_id(user)
    offset = (page - 1) * page_size

    # Count total
    count_stmt = select(func.count()).select_from(Team).where(Team.tenant_id == tenant)
    total = (await db.execute(count_stmt)).scalar() or 0

    # Fetch paginated teams with member count
    stmt = (
        select(Team)
        .where(Team.tenant_id == tenant)
        .order_by(Team.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    teams = (await db.execute(stmt)).scalars().all()

    items = []
    for team in teams:
        member_count = len(team.members) if team.members is not None else 0
        items.append(
            TeamResponse(
                id=str(team.id),
                name=team.name,
                cadence=None,
                linked_jira_project=None,
                default_anonymity=False,
                workspace_id=None,
                created_at=team.created_at,
                updated_at=team.updated_at,
                member_count=member_count,
            )
        )

    return TeamListResponse(items=items, total=total, page=page, page_size=page_size)


# ── Create team ────────────────────────────────────────────────────────────────


@router.post(
    "/",
    response_model=TeamResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create team",
    description="Create a new team. Requires admin role.",
)
async def create_team(
    body: TeamCreate,
    user: Annotated[ClerkUser, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TeamResponse:
    """Create a new team under the current tenant."""
    tenant = _tenant_id(user)

    # Check uniqueness within tenant
    existing = (
        await db.execute(
            select(Team).where(Team.tenant_id == tenant, Team.name == body.name)
        )
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Team with name '{body.name}' already exists in this tenant",
        )

    team = Team(
        id=str(uuid4()),
        tenant_id=tenant,
        name=body.name,
        description=None,
        is_active=True,
    )
    db.add(team)
    await db.flush()
    await db.refresh(team)

    return TeamResponse(
        id=str(team.id),
        name=team.name,
        cadence=body.cadence,
        linked_jira_project=body.linked_jira_project,
        default_anonymity=body.default_anonymity,
        workspace_id=None,
        created_at=team.created_at,
        updated_at=team.updated_at,
        member_count=0,
    )


# ── Get team detail ────────────────────────────────────────────────────────────


@router.get(
    "/{team_id}",
    response_model=TeamResponse,
    summary="Get team detail",
    description="Retrieve a single team with its member list.",
)
async def get_team(
    team_id: str,
    user: Annotated[ClerkUser, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TeamResponse:
    """Get a team by ID with its members. Tenant-scoped."""
    tenant = _tenant_id(user)

    stmt = (
        select(Team)
        .options(selectinload(Team.members))
        .where(Team.id == team_id, Team.tenant_id == tenant)
    )
    team = (await db.execute(stmt)).scalar_one_or_none()
    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )

    # Build member responses with user info
    member_responses = []
    for member in team.members:
        # Look up user for display name/email
        user_stmt = select(User).where(User.id == member.user_id)
        member_user = (await db.execute(user_stmt)).scalar_one_or_none()
        member_responses.append(
            TeamMemberResponse(
                id=str(member.id),
                user_id=member.user_id,
                role=member.role,
                joined_at=member.created_at,
                display_name=member_user.full_name if member_user else None,
                email=member_user.email if member_user else None,
            )
        )

    member_count = len(team.members)

    return TeamResponse(
        id=str(team.id),
        name=team.name,
        cadence=None,
        linked_jira_project=None,
        default_anonymity=False,
        workspace_id=None,
        created_at=team.created_at,
        updated_at=team.updated_at,
        member_count=member_count,
    )


# ── Get team members ───────────────────────────────────────────────────────────


@router.get(
    "/{team_id}/members",
    response_model=list[TeamMemberResponse],
    summary="List team members",
)
async def list_team_members(
    team_id: str,
    user: Annotated[ClerkUser, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[TeamMemberResponse]:
    """List all members of a team. Tenant-scoped."""
    tenant = _tenant_id(user)

    # Ensure team exists in tenant
    team = (
        await db.execute(
            select(Team).where(Team.id == team_id, Team.tenant_id == tenant)
        )
    ).scalar_one_or_none()
    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )

    members = (
        await db.execute(select(TeamMember).where(TeamMember.team_id == team_id))
    ).scalars().all()

    result = []
    for member in members:
        user_stmt = select(User).where(User.id == member.user_id)
        member_user = (await db.execute(user_stmt)).scalar_one_or_none()
        result.append(
            TeamMemberResponse(
                id=str(member.id),
                user_id=member.user_id,
                role=member.role,
                joined_at=member.created_at,
                display_name=member_user.full_name if member_user else None,
                email=member_user.email if member_user else None,
            )
        )
    return result


# ── Update team ────────────────────────────────────────────────────────────────


@router.patch(
    "/{team_id}",
    response_model=TeamResponse,
    summary="Update team",
    description="Update team fields. All fields are optional.",
)
async def update_team(
    team_id: str,
    body: TeamUpdate,
    user: Annotated[ClerkUser, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TeamResponse:
    """Update a team. Tenant-scoped."""
    tenant = _tenant_id(user)

    stmt = (
        select(Team)
        .options(selectinload(Team.members))
        .where(Team.id == team_id, Team.tenant_id == tenant)
    )
    team = (await db.execute(stmt)).scalar_one_or_none()
    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )

    update_data = body.model_dump(exclude_unset=True)
    if not update_data:
        # No fields to update — return current state
        member_count = len(team.members) if team.members else 0
        return TeamResponse(
            id=str(team.id),
            name=team.name,
            cadence=None,
            linked_jira_project=None,
            default_anonymity=False,
            workspace_id=None,
            created_at=team.created_at,
            updated_at=team.updated_at,
            member_count=member_count,
        )

    # Check name uniqueness if name is being changed
    if "name" in update_data:
        existing = (
            await db.execute(
                select(Team).where(
                    Team.tenant_id == tenant,
                    Team.name == update_data["name"],
                    Team.id != team_id,
                )
            )
        ).scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Team with name '{update_data['name']}' already exists",
            )

    for field, value in update_data.items():
        setattr(team, field, value)

    await db.flush()
    await db.refresh(team)

    member_count = len(team.members) if team.members else 0
    return TeamResponse(
        id=str(team.id),
        name=team.name,
        cadence=update_data.get("cadence"),
        linked_jira_project=update_data.get("linked_jira_project"),
        default_anonymity=update_data.get("default_anonymity", False),
        workspace_id=None,
        created_at=team.created_at,
        updated_at=team.updated_at,
        member_count=member_count,
    )


# ── Delete team (soft-delete) ──────────────────────────────────────────────────


@router.delete(
    "/{team_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft-delete team",
    description="Mark a team as inactive (soft-delete).",
)
async def delete_team(
    team_id: str,
    user: Annotated[ClerkUser, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Soft-delete a team by setting is_active=False."""
    tenant = _tenant_id(user)

    team = (
        await db.execute(
            select(Team).where(Team.id == team_id, Team.tenant_id == tenant)
        )
    ).scalar_one_or_none()
    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )

    team.is_active = False
    await db.flush()


# ── Add member ─────────────────────────────────────────────────────────────────


@router.post(
    "/{team_id}/members",
    response_model=TeamMemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add team member",
    description="Add a user to a team.",
)
async def add_member(
    team_id: str,
    body: TeamMemberCreate,
    user: Annotated[ClerkUser, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TeamMemberResponse:
    """Add a member to a team. Tenant-scoped."""
    tenant = _tenant_id(user)

    # Verify team exists in tenant
    team = (
        await db.execute(
            select(Team).where(Team.id == team_id, Team.tenant_id == tenant)
        )
    ).scalar_one_or_none()
    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )

    # Check if membership already exists
    existing = (
        await db.execute(
            select(TeamMember).where(
                TeamMember.team_id == team_id,
                TeamMember.user_id == body.user_id,
            )
        )
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already a member of this team",
        )

    member = TeamMember(
        id=str(uuid4()),
        tenant_id=tenant,
        user_id=body.user_id,
        team_id=team_id,
        role=body.role.value if hasattr(body.role, "value") else str(body.role),
    )
    db.add(member)
    await db.flush()
    await db.refresh(member)

    # Fetch user info for response
    user_stmt = select(User).where(User.id == body.user_id)
    member_user = (await db.execute(user_stmt)).scalar_one_or_none()

    return TeamMemberResponse(
        id=str(member.id),
        user_id=member.user_id,
        role=member.role,
        joined_at=member.created_at,
        display_name=member_user.full_name if member_user else None,
        email=member_user.email if member_user else None,
    )


# ── Remove member ──────────────────────────────────────────────────────────────


@router.delete(
    "/{team_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove team member",
    description="Remove a user from a team.",
)
async def remove_member(
    team_id: str,
    user_id: str,
    user: Annotated[ClerkUser, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Remove a member from a team. Tenant-scoped."""
    tenant = _tenant_id(user)

    # Verify team exists in tenant
    team = (
        await db.execute(
            select(Team).where(Team.id == team_id, Team.tenant_id == tenant)
        )
    ).scalar_one_or_none()
    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )

    member = (
        await db.execute(
            select(TeamMember).where(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user_id,
            )
        )
    ).scalar_one_or_none()
    if member is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found in this team",
        )

    await member.delete()
    await db.flush()
