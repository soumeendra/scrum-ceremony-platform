"""Template Pydantic schemas."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field


# ── Enums ──────────────────────────────────────────────────────────────────────


class CeremonyType(str, Enum):
    """Types of Scrum ceremonies."""

    RETROSPECTIVE = "retrospective"
    STANDUP = "standup"
    PLANNING = "planning"
    REVIEW = "review"


class TemplateScope(str, Enum):
    """Visibility scope of a template."""

    ORG = "org"
    WORKSPACE = "workspace"
    TEAM = "team"


# ── Template schemas ───────────────────────────────────────────────────────────


class TemplateBase(BaseModel):
    """Base schema shared by template create/update operations."""

    name: Annotated[str, Field(min_length=1, max_length=200)]
    ceremony_type: CeremonyType
    phases: list[dict] = Field(default_factory=list)
    columns: list[dict] = Field(default_factory=list)
    is_locked: bool = False


class TemplateCreate(TemplateBase):
    """Schema for creating a new template."""

    scope: TemplateScope = TemplateScope.TEAM
    owner_id: str | None = None


class TemplateUpdate(BaseModel):
    """Schema for updating a template. All fields optional."""

    name: Annotated[str | None, Field(min_length=1, max_length=200)] = None
    ceremony_type: CeremonyType | None = None
    phases: list[dict] | None = None
    columns: list[dict] | None = None
    is_locked: bool | None = None
    scope: TemplateScope | None = None


class TemplateResponse(BaseModel):
    """Schema for template data returned to clients."""

    id: str
    name: str
    ceremony_type: CeremonyType
    scope: TemplateScope
    owner_id: str | None = None
    phases: list[dict] = Field(default_factory=list)
    columns: list[dict] = Field(default_factory=list)
    is_locked: bool = False
    is_default: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


class TemplateListResponse(BaseModel):
    """Paginated list of templates."""

    items: list[TemplateResponse]
    total: int
    page: int
    page_size: int
