"""AI API — clustering, summaries, action extraction, sentiment analysis."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import CurrentUser
from app.schemas.ai import (
    ActionExtractionResponse,
    ClusterResponse,
    SentimentResponse,
    SummaryResponse,
)
from app.services.ai.clustering import ClusteringService
from app.services.ai.ollama_client import OllamaClient
from app.services.ai.summaries import SummaryService

router = APIRouter()


@router.post("/cluster/{ceremony_id}", summary="Trigger AI clustering")
async def trigger_clustering(
    ceremony_id: str,
    user: CurrentUser,
) -> dict:
    """Trigger AI clustering of board items for a ceremony."""
    service = ClusteringService()
    clusters = await service.cluster_notes(ceremony_id)
    return {"ceremony_id": ceremony_id, "clusters": clusters}


@router.get("/cluster/{ceremony_id}", summary="Get clusters")
async def get_clusters(
    ceremony_id: str,
    user: CurrentUser,
) -> dict:
    """Get stored clusters for a ceremony."""
    service = ClusteringService()
    clusters = await service.get_clusters(ceremony_id)
    return {
        "ceremony_id": ceremony_id,
        "clusters": [
            {
                "id": c.id,
                "title": c.title,
                "item_ids": c.item_ids or [],
                "source": c.source,
                "ai_confidence": c.ai_confidence,
                "approved_by": c.approved_by,
            }
            for c in clusters
        ],
    }


@router.post("/cluster/{cluster_id}/approve", summary="Approve cluster")
async def approve_cluster(
    cluster_id: str,
    user: CurrentUser,
) -> dict:
    """Approve an AI-suggested cluster."""
    service = ClusteringService()
    cluster = await service.approve_cluster(cluster_id, user.id)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    return {"id": cluster_id, "approved": True}


@router.post("/summary/{ceremony_id}", summary="Generate retro summary")
async def generate_summary(
    ceremony_id: str,
    user: CurrentUser,
) -> dict:
    """Generate an AI summary of the retro."""
    service = SummaryService()
    result = await service.generate_summary(ceremony_id)
    return {"ceremony_id": ceremony_id, "summary": result}


@router.post("/summary/{summary_id}/approve", summary="Approve summary")
async def approve_summary(
    summary_id: str,
    user: CurrentUser,
) -> dict:
    """Approve a generated summary."""
    return {"id": summary_id, "approved": True}


@router.post("/extract-actions/{ceremony_id}", summary="Extract action items")
async def extract_actions(
    ceremony_id: str,
    user: CurrentUser,
) -> ActionExtractionResponse:
    """Extract action items from retro notes."""
    service = SummaryService()
    actions = await service.extract_actions(ceremony_id)
    return ActionExtractionResponse(actions=actions)


@router.post("/sentiment/{ceremony_id}", summary="Analyze sentiment")
async def analyze_sentiment(
    ceremony_id: str,
    user: CurrentUser,
) -> SentimentResponse:
    """Analyze sentiment of retro notes."""
    service = SummaryService()
    result = await service.analyze_sentiment(ceremony_id)
    return SentimentResponse(**result)


@router.get("/health", summary="AI service health")
async def ai_health(
    user: CurrentUser,
) -> dict:
    """Check AI service health."""
    client = OllamaClient()
    ollama_ok = await client.health_check()
    models = await client.list_models() if ollama_ok else []

    return {
        "ollama_available": ollama_ok,
        "fallback_available": bool(client._fallback_url),
        "models": models,
    }
