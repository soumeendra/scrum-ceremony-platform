"""Pydantic schemas for AI service responses."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class SentimentLevel(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class ClusterSource(str, Enum):
    AI = "ai"
    MANUAL = "manual"


class PriorityLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ClusterResponse(BaseModel):
    id: str
    title: str
    item_ids: list[str] = Field(default_factory=list)
    source: ClusterSource = ClusterSource.AI
    ai_confidence: float | None = None
    approved_by: str | None = None
    created_at: str | None = None

    model_config = {"from_attributes": True}


class SummarySection(BaseModel):
    top_themes: list[str] = Field(default_factory=list)
    top_voted_items: list[str] = Field(default_factory=list)
    proposed_actions: list[str] = Field(default_factory=list)
    carry_forward: list[str] = Field(default_factory=list)


class SummaryResponse(BaseModel):
    ceremony_id: str
    content: SummarySection
    source: str = "ai"
    approved_by: str | None = None

    model_config = {"from_attributes": True}


class ExtractedAction(BaseModel):
    title: str
    description: str | None = None
    owner_hint: str | None = None
    priority_hint: PriorityLevel = PriorityLevel.MEDIUM


class ActionExtractionResponse(BaseModel):
    actions: list[ExtractedAction]


class NoteSentiment(BaseModel):
    text: str
    sentiment: SentimentLevel


class SentimentResponse(BaseModel):
    overall: SentimentLevel
    score: float = Field(ge=-1, le=1)
    per_note: list[NoteSentiment] = Field(default_factory=list)


class AIHealthResponse(BaseModel):
    ollama_available: bool
    fallback_available: bool
    models: list[str] = Field(default_factory=list)
