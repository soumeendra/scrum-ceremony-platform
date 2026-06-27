"""Team and TeamMember Pydantic schemas."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field

# ── Enums ──────────────────────────────────────────────────────────────────────


class TeamCadence(str, Enum):
    """Sprint cadence options."""

    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"


class TeamMemberRole(str, Enum):
    """Roles a member can have within a team."""

    FACILITATOR = "facilitator"
    MEMBER = "member"


# ── Team schemas ───────────────────────────────────────────────────────────────


class TeamBase(BaseModel):
    """Base schema shared by team create/update operations."""

    name: Annotated[str, Field(min_length=1, max_length=200)]
    cadence: TeamCadence | None = None
    linked_jira_project: Annotated[str | None, Field(max_length=200)] = None
    default_anonymity: bool = False


class TeamCreate(TeamBase):
    """Schema for creating a new team."""

    pass


class TeamUpdate(BaseModel):
    """Schema for updating a team. All fields optional."""

    name: Annotated[str | None, Field(min_length=1, max_length=200)] = None
    cadence: TeamCadence | None = None
    linked_jira_project: Annotated[str | None, Field(max_length=200)] = None
    default_anonymity: bool | None = None


class TeamResponse(BaseModel):
    """Schema for team data returned to clients."""

    id: str
    name: str
    cadence: TeamCadence | None = None
    linked_jira_project: str | None = None
    default_anonymity: bool = False
    workspace_id: str | None = None
    created_at: datetime
    updated_at: datetime
    member_count: int = 0

    model_config = {"from_attributes": True}


class TeamListResponse(BaseModel):
    """Paginated list of teams."""

    items: list[TeamResponse]
    total: int
    page: int
    page_size: int


# ── TeamMember schemas ─────────────────────────────────────────────────────────


class TeamMemberBase(BaseModel):
    """Base schema for team membership."""

    user_id: str
    role: TeamMemberRole = TeamMemberRole.MEMBER


class TeamMemberCreate(TeamMemberBase):
    """Schema for adding a member to a team."""

    pass


class TeamMemberResponse(BaseModel):
    """Schema for team member data returned to clients."""

    id: str
    user_id: str
    role: TeamMemberRole = TeamMemberRole.MEMBER
    joined_at: datetime
    display_name: str | None = None
    email: str | None = None

    model_config = {"from_attributes": True}
