"""Basic health check test."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_returns_ok(client: AsyncClient) -> None:
    """GET /health should return 200 with a status field."""
    # Mock the DB and Redis checks so the test doesn't need real services
    with (
        patch("app.api.health.async_session_factory") as mock_sf,
        patch("app.api.health.aioredis.from_url") as mock_redis,
    ):
        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=None)
        mock_sf.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_sf.return_value.__aexit__ = AsyncMock(return_value=None)

        mock_r = AsyncMock()
        mock_r.ping = AsyncMock(return_value=True)
        mock_r.aclose = AsyncMock(return_value=None)
        mock_redis.return_value = mock_r

        response = await client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert "status" in body
    assert "checks" in body
    assert "database" in body["checks"]
    assert "redis" in body["checks"]


@pytest.mark.asyncio
async def test_health_structure(client: AsyncClient) -> None:
    """GET /health response contains expected top-level keys."""
    with (
        patch("app.api.health.async_session_factory") as mock_sf,
        patch("app.api.health.aioredis.from_url") as mock_redis,
    ):
        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=None)
        mock_sf.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_sf.return_value.__aexit__ = AsyncMock(return_value=None)

        mock_r = AsyncMock()
        mock_r.ping = AsyncMock(return_value=True)
        mock_r.aclose = AsyncMock(return_value=None)
        mock_redis.return_value = mock_r

        response = await client.get("/health")

    body = response.json()
    for key in ("status", "timestamp", "env", "checks"):
        assert key in body, f"Missing key: {key}"
