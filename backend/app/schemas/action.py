"""Action, ActionRegister, and IntegrationLink Pydantic schemas."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Annotated, Any

from pydantic import BaseModel, Field


# ── Enums ──────────────────────────────────────────────────────────────────────


class ActionPriority(str, Enum):
    """Priority levels for action items."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ActionStatus(str, Enum):
    """Lifecycle status of an action item."""

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    DROPPED = "dropped"


# ── Action schemas ─────────────────────────────────────────────────────────────


class ActionBase(BaseModel):
    """Base schema shared by action create/update operations."""

    title: Annotated[str, Field(min_length=1, max_length=500)]
    description: str | None = None
    assignee_id: str | None = None
    due_date: str | None = None
    priority: ActionPriority = ActionPriority.MEDIUM
    status: ActionStatus = ActionStatus.OPEN


class ActionCreate(ActionBase):
    """Schema for creating a new action item."""

    ceremony_id: str | None = None
    source_item_id: str | None = None


class ActionUpdate(BaseModel):
    """Schema for updating an action item. All fields optional."""

    title: Annotated[str | None, Field(min_length=1, max_length=500)] = None
    description: str | None = None
    assignee_id: str | None = None
    due_date: str | None = None
    priority: ActionPriority | None = None
    status: ActionStatus | None = None


class IntegrationLinkResponse(BaseModel):
    """Schema for an integration link returned to clients."""

    id: str
    provider: str
    external_id: str
    external_url: str | None = None
    sync_status: str

    model_config = {"from_attributes": True}


class ActionResponse(BaseModel):
    """Schema for action data returned to clients."""

    id: str
    title: str
    description: str | None = None
    assignee_id: str | None = None
    due_date: str | None = None
    priority: ActionPriority
    status: ActionStatus
    ceremony_id: str
    team_id: str
    source_item_id: str | None = None
    created_at: datetime
    updated_at: datetime
    integration_link: dict[str, Any] | None = None

    model_config = {"from_attributes": True}


class ActionListResponse(BaseModel):
    """Paginated list of actions with aggregate metrics."""

    items: list[ActionResponse]
    total: int
    page: int
    page_size: int
    open_count: int = 0
    in_progress_count: int = 0
    done_count: int = 0
    overdue_count: int = 0


# ── Quality score schema ───────────────────────────────────────────────────────


class ActionQualityScore(BaseModel):
    """Quality assessment for a single action item."""

    action_id: str
    score: Annotated[int, Field(ge=0, le=100)]
    issues: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
