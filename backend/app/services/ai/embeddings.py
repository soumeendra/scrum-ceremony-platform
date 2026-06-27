"""Embedding service for semantic similarity and clustering."""

from __future__ import annotations

import math
from typing import Any

import structlog
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.services.ai.ollama_client import OllamaClient

logger = structlog.get_logger()


class EmbeddingService:
    """Generate and store embeddings for board items."""

    def __init__(self):
        self.client = OllamaClient()

    async def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a batch of texts."""
        return await self.client.embed(texts)

    async def generate_single(self, text_content: str) -> list[float]:
        """Generate embedding for a single text."""
        results = await self.generate_embeddings([text_content])
        return results[0] if results else [0.0] * 1024

    async def store_embeddings(self, board_item_id: str, embedding: list[float]) -> None:
        """Store embedding in pgvector."""
        async with async_session_factory() as session:
            await session.execute(
                text(
                    "INSERT INTO embeddings (board_item_id, embedding, model, created_at) "
                    "VALUES (:item_id, :embedding, :model, NOW()) "
                    "ON CONFLICT (board_item_id) DO UPDATE SET embedding = :embedding"
                ),
                {
                    "item_id": board_item_id,
                    "embedding": str(embedding),
                    "model": "mxbai-embed-large",
                },
            )
            await session.commit()

    async def find_similar(
        self, query_embedding: list[float], top_k: int = 5
    ) -> list[dict[str, Any]]:
        """Find similar items using cosine similarity."""
        async with async_session_factory() as session:
            result = await session.execute(
                text(
                    "SELECT board_item_id, 1 - (embedding <=> :query) AS similarity "
                    "FROM embeddings ORDER BY embedding <=> :query LIMIT :top_k"
                ),
                {"query": str(query_embedding), "top_k": top_k},
            )
            return [
                {"board_item_id": row[0], "similarity": row[1]}
                for row in result.fetchall()
            ]

    @staticmethod
    def cosine_similarity(a: list[float], b: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)
