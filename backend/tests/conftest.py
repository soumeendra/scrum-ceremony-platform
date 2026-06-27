"""Shared pytest fixtures for the test suite."""

from __future__ import annotations

import asyncio
from typing import AsyncGenerator
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.security import ClerkUser
from app.models.base import Base

# ── In-memory SQLite for fast unit tests ────────────────────────────────────────
TEST_DATABASE_URL = "sqlite+aiosqlite:///file::memory:?cache=shared&uri=true"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_session_factory = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)


# ── Event loop ─────────────────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def event_loop() -> asyncio.AbstractEventLoop:
    """Create a single event loop for the entire test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ── Database ───────────────────────────────────────────────────────────────────
@pytest_asyncio.fixture(autouse=True)
async def async_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a clean test database session, dropping all tables after each test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with test_session_factory() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ── HTTP Client ─────────────────────────────────────────────────────────────────
@pytest_asyncio.fixture
async def client(async_db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Provide an httpx AsyncClient wired to the FastAPI app."""
    from app.main import app
    from app.core.database import get_db

    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield async_db_session

    app.dependency_overrides[get_db] = _override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c

    app.dependency_overrides.clear()


# ── Auth bypass ─────────────────────────────────────────────────────────────────
@pytest.fixture
def auth_user() -> ClerkUser:
    """Return a mock authenticated user for tests."""
    return ClerkUser(
        id=str(uuid4()),
        email="test@example.com",
        org_id=str(uuid4()),
        role="member",
    )


# ── Sample domain fixtures ─────────────────────────────────────────────────────
@pytest.fixture
def sample_org_id() -> str:
    return str(uuid4())


@pytest.fixture
def sample_team_id() -> str:
    return str(uuid4())


@pytest.fixture
def sample_user_id() -> str:
    return str(uuid4())
