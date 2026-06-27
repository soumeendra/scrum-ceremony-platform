"""Integrations API — manage external system connections and sync."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import CurrentUser

router = APIRouter()


@router.post("/jira/connect", summary="Connect to Jira")
async def connect_jira(
    user: CurrentUser,
    base_url: str,
    client_id: str,
    client_secret: str,
) -> dict:
    """Store Jira OAuth credentials for the tenant."""
    # In production: store encrypted credentials in integration_configs
    return {
        "status": "connected",
        "base_url": base_url,
        "message": "Jira connection configured. Complete OAuth flow to activate.",
    }


@router.post("/jira/sync/{action_id}", summary="Sync action to Jira")
async def sync_to_jira(
    action_id: str,
    user: CurrentUser,
) -> dict:
    """Trigger sync of an action to Jira."""
    # In production: look up action, get tenant's Jira credentials, call SyncService
    return {
        "action_id": action_id,
        "status": "queued",
        "message": "Sync queued. Status will be updated asynchronously.",
    }


@router.get("/jira/status/{action_id}", summary="Get sync status")
async def get_sync_status(
    action_id: str,
    user: CurrentUser,
) -> dict:
    """Get the Jira sync status for an action."""
    return {
        "action_id": action_id,
        "sync_status": "pending",
        "external_id": None,
        "external_url": None,
    }


@router.get("/health", summary="Integration health check")
async def integration_health(
    user: CurrentUser,
) -> dict:
    """Get overall integration health."""
    return {
        "jira": {
            "connected": False,
            "status": "not_configured",
        },
        "overall": "degraded",
    }
