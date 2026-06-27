"""Tests for action CRUD, register, carry-forward, and quality scoring."""

from __future__ import annotations

from unittest.mock import patch
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import ClerkUser, get_current_user
from app.models.action import Action, ActionRegister, IntegrationLink
from app.models.ceremony import Ceremony
from app.models.team import Team
from app.schemas.action import ActionPriority, ActionStatus


# ── Helpers ────────────────────────────────────────────────────────────────────


def _make_auth_user(
    org_id: str | None = None,
    role: str = "member",
    user_id: str | None = None,
) -> ClerkUser:
    return ClerkUser(
        id=user_id or str(uuid4()),
        email="test@example.com",
        org_id=org_id or str(uuid4()),
        role=role,
    )


def _auth_headers() -> dict[str, str]:
    return {"Authorization": "Bearer mock-token"}


async def _seed_team_and_ceremony(
    db: AsyncSession,
    tenant_id: str,
    team_id: str | None = None,
    ceremony_id: str | None = None,
) -> tuple[str, str]:
    """Create a team and ceremony, returning (team_id, ceremony_id)."""
    tid = team_id or str(uuid4())
    cid = ceremony_id or str(uuid4())

    team = Team(
        id=tid,
        tenant_id=tenant_id,
        name="Test Team",
    )
    db.add(team)

    ceremony = Ceremony(
        id=cid,
        tenant_id=tenant_id,
        team_id=tid,
        title="Test Retro",
        ceremony_type="retrospective",
    )
    db.add(ceremony)
    await db.flush()
    return tid, cid


async def _seed_action(
    db: AsyncSession,
    tenant_id: str,
    team_id: str,
    ceremony_id: str,
    *,
    title: str = "Fix the login bug",
    description: str | None = None,
    assignee_id: str | None = None,
    due_date: str | None = None,
    priority: str = "medium",
    status: str = "open",
) -> str:
    """Create an action and return its ID."""
    action_id = str(uuid4())
    action = Action(
        id=action_id,
        tenant_id=tenant_id,
        ceremony_id=ceremony_id,
        team_id=team_id,
        title=title,
        description=description,
        assignee_id=assignee_id,
        due_date=due_date,
        priority=priority,
        status=status,
    )
    db.add(action)
    await db.flush()
    return action_id


def _override_auth(app, user: ClerkUser):
    """Set up auth override and return a cleanup function."""

    async def _override():
        return user

    original = dict(app.dependency_overrides)
    app.dependency_overrides[get_current_user] = _override

    def cleanup():
        app.dependency_overrides = original

    return cleanup


# ── Test: Create action ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_action(
    client: AsyncClient,
    async_db_session: AsyncSession,
) -> None:
    """POST /api/v1/actions should create a new action item."""
    user = _make_auth_user(org_id="tenant-1", role="member", user_id="user-1")
    from app.main import app

    cleanup = _override_auth(app, user)
    try:
        team_id, ceremony_id = await _seed_team_and_ceremony(
            async_db_session, tenant_id="tenant-1"
        )

        response = await client.post(
            "/api/v1/actions/",
            headers=_auth_headers(),
            json={
                "title": "Improve CI pipeline speed",
                "description": "Reduce build times by 30%",
                "assignee_id": "user-1",
                "due_date": "2026-07-15",
                "priority": "high",
                "status": "open",
                "ceremony_id": ceremony_id,
            },
        )
    finally:
        cleanup()

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Improve CI pipeline speed"
    assert body["description"] == "Reduce build times by 30%"
    assert body["assignee_id"] == "user-1"
    assert body["due_date"] == "2026-07-15"
    assert body["priority"] == "high"
    assert body["status"] == "open"
    assert body["ceremony_id"] == ceremony_id
    assert "id" in body
    assert "created_at" in body
    assert "updated_at" in body


# ── Test: List actions with filters ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_actions_with_filters(
    client: AsyncClient,
    async_db_session: AsyncSession,
) -> None:
    """GET /api/v1/actions should support status, priority, and assignee filters."""
    user = _make_auth_user(org_id="tenant-2", role="member", user_id="user-2")
    from app.main import app

    cleanup = _override_auth(app, user)
    try:
        team_id, ceremony_id = await _seed_team_and_ceremony(
            async_db_session, tenant_id="tenant-2"
        )

        # Seed actions with different statuses/priorities
        await _seed_action(
            async_db_session, "tenant-2", team_id, ceremony_id,
            title="Action A", priority="high", status="open", assignee_id="user-2",
        )
        await _seed_action(
            async_db_session, "tenant-2", team_id, ceremony_id,
            title="Action B", priority="low", status="done", assignee_id="user-3",
        )
        await _seed_action(
            async_db_session, "tenant-2", team_id, ceremony_id,
            title="Action C", priority="high", status="in_progress", assignee_id="user-2",
        )

        # Filter by status=open
        response = await client.get(
            "/api/v1/actions/",
            headers=_auth_headers(),
            params={"status": "open"},
        )
    finally:
        cleanup()

    assert response.status_code == 200
    body = response.json()
    assert "items" in body
    assert "total" in body
    assert "open_count" in body
    assert "in_progress_count" in body
    assert "done_count" in body
    assert "overdue_count" in body
    assert body["total"] >= 1
    # All returned items should be "open"
    for item in body["items"]:
        assert item["status"] == "open"


# ── Test: Update action status ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_action_status(
    client: AsyncClient,
    async_db_session: AsyncSession,
) -> None:
    """PATCH /api/v1/actions/{id} should update status and return the action."""
    user = _make_auth_user(org_id="tenant-3", role="member", user_id="user-3")
    from app.main import app

    cleanup = _override_auth(app, user)
    try:
        team_id, ceremony_id = await _seed_team_and_ceremony(
            async_db_session, tenant_id="tenant-3"
        )
        action_id = await _seed_action(
            async_db_session, "tenant-3", team_id, ceremony_id,
            title="Update me", status="open",
        )

        response = await client.patch(
            f"/api/v1/actions/{action_id}",
            headers=_auth_headers(),
            json={"status": "in_progress"},
        )
    finally:
        cleanup()

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == action_id
    assert body["status"] == "in_progress"


# ── Test: Action register cross-retro ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_action_register_cross_retro(
    client: AsyncClient,
    async_db_session: AsyncSession,
) -> None:
    """GET /api/v1/actions/register/ should return open actions across ceremonies."""
    user = _make_auth_user(org_id="tenant-4", role="member", user_id="user-4")
    from app.main import app

    cleanup = _override_auth(app, user)
    try:
        team_id, ceremony_id = await _seed_team_and_ceremony(
            async_db_session, tenant_id="tenant-4"
        )

        # Create an action and register entry
        action_id = await _seed_action(
            async_db_session, "tenant-4", team_id, ceremony_id,
            title="Cross-retro action", status="open",
        )
        reg = ActionRegister(
            id=str(uuid4()),
            tenant_id="tenant-4",
            team_id=team_id,
            action_id=action_id,
            is_recurring=True,
        )
        async_db_session.add(reg)
        await async_db_session.flush()

        response = await client.get(
            "/api/v1/actions/register/",
            headers=_auth_headers(),
        )
    finally:
        cleanup()

    assert response.status_code == 200
    body = response.json()
    assert "items" in body
    assert body["total"] >= 1
    # The action should appear in the register
    titles = [item["title"] for item in body["items"]]
    assert "Cross-retro action" in titles


# ── Test: Action quality scoring ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_action_quality_scoring(
    client: AsyncClient,
    async_db_session: AsyncSession,
) -> None:
    """GET /api/v1/actions/quality/{id} should return a quality score."""
    user = _make_auth_user(org_id="tenant-5", role="member", user_id="user-5")
    from app.main import app

    cleanup = _override_auth(app, user)
    try:
        team_id, ceremony_id = await _seed_team_and_ceremony(
            async_db_session, tenant_id="tenant-5"
        )

        # Low-quality action (no assignee, no due date, vague title)
        low_q_id = await _seed_action(
            async_db_session, "tenant-5", team_id, ceremony_id,
            title="Fix stuff",
            description=None,
            assignee_id=None,
            due_date=None,
        )

        response = await client.get(
            f"/api/v1/actions/quality/{low_q_id}",
            headers=_auth_headers(),
        )
    finally:
        cleanup()

    assert response.status_code == 200
    body = response.json()
    assert "action_id" in body
    assert "score" in body
    assert "issues" in body
    assert "suggestions" in body
    assert body["action_id"] == low_q_id
    assert 0 <= body["score"] <= 100
    # Low-quality action should have a low score and some issues
    assert body["score"] < 60
    assert len(body["issues"]) > 0


# ── Test: Carry forward ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_carry_forward(
    client: AsyncClient,
    async_db_session: AsyncSession,
) -> None:
    """POST /api/v1/actions/{id}/carry-forward should create a new action in target ceremony."""
    user = _make_auth_user(org_id="tenant-6", role="member", user_id="user-6")
    from app.main import app

    cleanup = _override_auth(app, user)
    try:
        team_id, ceremony_id_1 = await _seed_team_and_ceremony(
            async_db_session, tenant_id="tenant-6"
        )
        # Create a second ceremony to carry forward to
        ceremony_id_2 = str(uuid4())
        ceremony2 = Ceremony(
            id=ceremony_id_2,
            tenant_id="tenant-6",
            team_id=team_id,
            title="Next Retro",
            ceremony_type="retrospective",
        )
        async_db_session.add(ceremony2)
        await async_db_session.flush()

        source_id = await _seed_action(
            async_db_session, "tenant-6", team_id, ceremony_id_1,
            title="Carry this forward",
            status="open",
            assignee_id="user-6",
            due_date="2026-08-01",
        )

        response = await client.post(
            f"/api/v1/actions/{source_id}/carry-forward",
            headers=_auth_headers(),
            params={"target_ceremony_id": ceremony_id_2},
        )
    finally:
        cleanup()

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "[Carried] Carry this forward"
    assert body["ceremony_id"] == ceremony_id_2
    assert body["assignee_id"] == "user-6"
    assert body["due_date"] == "2026-08-01"
    assert body["status"] == "open"
    assert body["id"] != source_id  # New action ID
