"""Clustering service for grouping similar board items."""

from __future__ import annotations

import json
import math
from typing import Any

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.models.ceremony import BoardItem, Cluster
from app.services.ai.embeddings import EmbeddingService
from app.services.ai.ollama_client import OllamaClient

logger = structlog.get_logger()


class ClusteringService:
    """Cluster board items using embeddings + cosine similarity."""

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.llm = OllamaClient()

    async def cluster_notes(self, ceremony_id: str) -> list[dict[str, Any]]:
        """Full clustering pipeline: fetch notes → embed → cluster → label."""
        # Fetch notes
        async with async_session_factory() as session:
            result = await session.execute(
                select(BoardItem).where(BoardItem.ceremony_id == ceremony_id)
            )
            notes = result.scalars().all()

        if len(notes) < 2:
            return []

        # Generate embeddings
        texts = [note.content for note in notes]
        embeddings = await self.embedding_service.generate_embeddings(texts)

        # Simple clustering using cosine similarity threshold
        clusters = self._cluster_by_similarity(
            [{"id": n.id, "text": n.content, "embedding": e} for n, e in zip(notes, embeddings)]
        )

        # Label each cluster using Gemma 9B
        labeled_clusters = []
        for cluster_items in clusters:
            label = await self.label_cluster([item["text"] for item in cluster_items])
            labeled_clusters.append({
                "title": label,
                "items": [item["id"] for item in cluster_items],
                "source": "ai",
                "ai_confidence": 0.8,
            })

        return labeled_clusters

    def _cluster_by_similarity(
        self, items: list[dict[str, Any]], threshold: float = 0.6
    ) -> list[list[dict[str, Any]]]:
        """Group items by cosine similarity threshold."""
        clusters: list[list[dict[str, Any]]] = []
        assigned = set()

        for i, item in enumerate(items):
            if item["id"] in assigned:
                continue
            cluster = [item]
            assigned.add(item["id"])

            for j, other in enumerate(items):
                if other["id"] in assigned:
                    continue
                sim = EmbeddingService.cosine_similarity(
                    item["embedding"], other["embedding"]
                )
                if sim >= threshold:
                    cluster.append(other)
                    assigned.add(other["id"])

            clusters.append(cluster)

        return clusters

    async def label_cluster(self, notes: list[str]) -> str:
        """Generate a label for a cluster using Gemma 9B."""
        prompt = (
            f"These are feedback notes from a retrospective:\n\n"
            + "\n".join(f"- {note}" for note in notes[:10])
            + "\n\nGenerate a short, descriptive label (3-5 words) for this theme. "
            "Respond with ONLY the label, nothing else."
        )

        result = await self.llm.generate(prompt)
        return result.get("text", "Untitled Theme").strip()

    async def get_clusters(self, ceremony_id: str) -> list[Cluster]:
        """Retrieve stored clusters for a ceremony."""
        async with async_session_factory() as session:
            result = await session.execute(
                select(Cluster).where(Cluster.ceremony_id == ceremony_id)
            )
            return list(result.scalars().all())

    async def approve_cluster(self, cluster_id: str, user_id: str) -> Cluster | None:
        """Approve an AI-suggested cluster."""
        async with async_session_factory() as session:
            result = await session.execute(select(Cluster).where(Cluster.id == cluster_id))
            cluster = result.scalar_one_or_none()
            if cluster:
                cluster.approved_by = user_id
                await session.commit()
            return cluster
