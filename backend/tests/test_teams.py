"""Tests for team CRUD endpoints."""

from __future__ import annotations

from unittest.mock import patch
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import ClerkUser
from app.models.team import Team, TeamMember
from app.models.user import User


# ── Helpers ────────────────────────────────────────────────────────────────────


def _make_auth_user(
    org_id: str | None = None,
    role: str = "member",
    user_id: str | None = None,
) -> ClerkUser:
    """Create a mock ClerkUser for testing."""
    return ClerkUser(
        id=user_id or str(uuid4()),
        email="test@example.com",
        org_id=org_id or str(uuid4()),
        role=role,
    )


def _auth_headers(user: ClerkUser) -> dict[str, str]:
    """Build Authorization headers for a mock user.

    The token itself is a dummy — we override get_current_user in tests.
    """
    return {"Authorization": "Bearer mock-token"}


# ── Fixtures ───────────────────────────────────────────────────────────────────


@pytest.fixture
def admin_user() -> ClerkUser:
    """Admin user in tenant A."""
    return _make_auth_user(org_id="tenant-a", role="org_admin", user_id="user-admin-a")


@pytest.fixture
def member_user() -> ClerkUser:
    """Regular member in tenant A."""
    return _make_auth_user(org_id="tenant-a", role="member", user_id="user-member-a")


@pytest.fixture
def other_tenant_user() -> ClerkUser:
    """User in tenant B (for isolation tests)."""
    return _make_auth_user(org_id="tenant-b", role="member", user_id="user-tenant-b")


@pytest.fixture
def admin_headers(admin_user: ClerkUser) -> dict[str, str]:
    return _auth_headers(admin_user)


@pytest.fixture
def member_headers(member_user: ClerkUser) -> dict[str, str]:
    return _auth_headers(member_user)


@pytest.fixture
def other_tenant_headers(other_tenant_user: ClerkUser) -> dict[str, str]:
    return _auth_headers(other_tenant_user)


# ── Test: Create team ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_team(
    client: AsyncClient,
    async_db_session: AsyncSession,
    admin_user: ClerkUser,
    admin_headers: dict[str, str],
) -> None:
    """POST /api/v1/teams should create a new team for the tenant."""
    from app.core.security import get_current_user

    async def _override():
        return admin_user

    # Override auth dependency
    from app.main import app

    original_overrides = dict(app.dependency_overrides)
    app.dependency_overrides[get_current_user] = _override

    try:
        response = await client.post(
            "/api/v1/teams/",
            headers=admin_headers,
            json={"name": "Engineering Team"},
        )
    finally:
        app.dependency_overrides = original_overrides

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Engineering Team"
    assert "id" in body
    assert "created_at" in body
    assert "updated_at" in body


# ── Test: List teams pagination ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_teams_pagination(
    client: AsyncClient,
    async_db_session: AsyncSession,
    admin_user: ClerkUser,
    admin_headers: dict[str, str],
) -> None:
    """GET /api/v1/teams should return paginated results."""
    from app.core.security import get_current_user
    from app.main import app

    async def _override():
        return admin_user

    app.dependency_overrides[get_current_user] = _override

    try:
        # Create multiple teams
        for i in range(5):
            resp = await client.post(
                "/api/v1/teams/",
                headers=admin_headers,
                json={"name": f"Team {i}"},
            )
            assert resp.status_code == 201

        # List with page_size=2
        response = await client.get(
            "/api/v1/teams/",
            headers=admin_headers,
            params={"page": 1, "page_size": 2},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert "items" in body
    assert "total" in body
    assert "page" in body
    assert "page_size" in body
    assert body["page"] == 1
    assert body["page_size"] == 2
    assert len(body["items"]) <= 2


# ── Test: Get team detail ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_team_detail(
    client: AsyncClient,
    async_db_session: AsyncSession,
    admin_user: ClerkUser,
    admin_headers: dict[str, str],
) -> None:
    """GET /api/v1/teams/{id} should return team details."""
    from app.core.security import get_current_user
    from app.main import app

    async def _override():
        return admin_user

    app.dependency_overrides[get_current_user] = _override

    try:
        # Create a team first
        create_resp = await client.post(
            "/api/v1/teams/",
            headers=admin_headers,
            json={"name": "Detail Test Team"},
        )
        team_id = create_resp.json()["id"]

        # Get detail
        response = await client.get(
            f"/api/v1/teams/{team_id}",
            headers=admin_headers,
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == team_id
    assert body["name"] == "Detail Test Team"
    assert "member_count" in body


# ── Test: Update team ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_team(
    client: AsyncClient,
    async_db_session: AsyncSession,
    admin_user: ClerkUser,
    admin_headers: dict[str, str],
) -> None:
    """PATCH /api/v1/teams/{id} should update team fields."""
    from app.core.security import get_current_user
    from app.main import app

    async def _override():
        return admin_user

    app.dependency_overrides[get_current_user] = _override

    try:
        # Create a team
        create_resp = await client.post(
            "/api/v1/teams/",
            headers=admin_headers,
            json={"name": "Original Name"},
        )
        team_id = create_resp.json()["id"]

        # Update
        response = await client.patch(
            f"/api/v1/teams/{team_id}",
            headers=admin_headers,
            json={"name": "Updated Name"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Updated Name"
    assert body["id"] == team_id


# ── Test: Add member ───────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_add_member(
    client: AsyncClient,
    async_db_session: AsyncSession,
    admin_user: ClerkUser,
    admin_headers: dict[str, str],
) -> None:
    """POST /api/v1/teams/{id}/members should add a member."""
    from app.core.security import get_current_user
    from app.main import app

    async def _override():
        return admin_user

    app.dependency_overrides[get_current_user] = _override

    try:
        # Create a team
        create_resp = await client.post(
            "/api/v1/teams/",
            headers=admin_headers,
            json={"name": "Member Test Team"},
        )
        team_id = create_resp.json()["id"]

        # Add member
        new_member_id = str(uuid4())
        response = await client.post(
            f"/api/v1/teams/{team_id}/members",
            headers=admin_headers,
            json={"user_id": new_member_id, "role": "member"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    body = response.json()
    assert body["user_id"] == new_member_id
    assert body["role"] == "member"
    assert "id" in body


# ── Test: Tenant isolation ─────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_tenant_isolation(
    client: AsyncClient,
    async_db_session: AsyncSession,
    admin_user: ClerkUser,
    other_tenant_user: ClerkUser,
    admin_headers: dict[str, str],
    other_tenant_headers: dict[str, str],
) -> None:
    """Teams from tenant A should not be visible to tenant B."""
    from app.core.security import get_current_user
    from app.main import app

    # Step 1: Create team as tenant A
    async def _override_admin():
        return admin_user

    app.dependency_overrides[get_current_user] = _override_admin

    team_id: str
    try:
        create_resp = await client.post(
            "/api/v1/teams/",
            headers=admin_headers,
            json={"name": "Tenant A Team"},
        )
        assert create_resp.status_code == 201
        team_id = create_resp.json()["id"]
    finally:
        app.dependency_overrides.clear()

    # Step 2: Try to access as tenant B — should get 404
    async def _override_other():
        return other_tenant_user

    app.dependency_overrides[get_current_user] = _override_other

    try:
        response = await client.get(
            f"/api/v1/teams/{team_id}",
            headers=other_tenant_headers,
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
