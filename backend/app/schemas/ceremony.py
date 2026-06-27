"""Ceremony Pydantic schemas."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field


# ── Enums ──────────────────────────────────────────────────────────────────────


class CeremonyType(str, Enum):
    """Types of ceremonies."""

    RETROSPECTIVE = "retrospective"
    STANDUP = "standup"
    PLANNING = "planning"
    REVIEW = "review"


class CeremonyStatus(str, Enum):
    """Lifecycle status of a ceremony."""

    DRAFT = "draft"
    ACTIVE = "active"
    VOTING = "voting"
    ACTION_ITEMS = "action_items"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class CeremonyMode(str, Enum):
    """Ceremony participation mode."""

    LIVE = "live"
    ASYNC = "async"


# ── Ceremony schemas ───────────────────────────────────────────────────────────


class CeremonyBase(BaseModel):
    """Base schema shared by ceremony create/update operations."""

    title: Annotated[str, Field(min_length=1, max_length=255)]
    template_id: str | None = None
    type: CeremonyType = CeremonyType.RETROSPECTIVE
    mode: CeremonyMode = CeremonyMode.LIVE


class CeremonyCreate(CeremonyBase):
    """Schema for creating a new ceremony."""

    sprint_ref: str | None = None


class CeremonyUpdate(BaseModel):
    """Schema for updating a ceremony. All fields optional."""

    title: Annotated[str | None, Field(min_length=1, max_length=255)] = None
    status: CeremonyStatus | None = None
    current_phase: str | None = None
    sprint_ref: str | None = None


class CeremonyResponse(BaseModel):
    """Schema for ceremony data returned to clients."""

    id: str
    title: str
    type: CeremonyType
    status: CeremonyStatus
    current_phase: str | None = None
    mode: CeremonyMode = CeremonyMode.LIVE
    template_id: str | None = None
    team_id: str
    facilitator_id: str | None = None
    sprint_ref: str | None = None
    scheduled_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class CeremonyListResponse(BaseModel):
    """Paginated list of ceremonies."""

    items: list[CeremonyResponse]
    total: int
    page: int
    page_size: int
