"""API v1 documentation, accessibility helpers, and polish."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.security import CurrentUser

router = APIRouter()


@router.get("/api/v1", summary="API v1 root", tags=["api"])
async def api_v1_root() -> dict:
    """API v1 documentation and available endpoints."""
    return {
        "version": "1.0",
        "name": "Scrum Ceremony Platform API",
        "documentation": "/docs",
        "endpoints": {
            "teams": "/api/v1/teams",
            "ceremonies": "/api/v1/ceremonies",
            "board_items": "/api/v1/ceremonies/{id}/items",
            "actions": "/api/v1/actions",
            "votes": "/api/v1/ceremonies/{id}/vote",
            "templates": "/api/v1/templates",
            "analytics": "/api/v1/analytics",
            "ai": "/api/v1/ai",
            "billing": "/api/v1/billing",
            "poker": "/api/v1/poker",
            "standup": "/api/v1/standup",
            "shared": "/api/v1/shared",
            "export": "/api/v1/export",
            "audit": "/api/v1/audit",
            "compliance": "/api/v1/compliance",
            "notifications": "/api/v1/notifications",
            "integrations": "/api/v1/integrations",
            "health": "/health",
            "websocket": "/ws/ceremony/{id}",
        },
        "ceremony_types": ["retrospective", "planning_poker", "async_standup", "sprint_review", "health_check"],
        "phases": {
            "retrospective": ["collect", "cluster", "vote", "discuss", "action", "completed"],
            "planning_poker": ["story_selection", "estimation", "reveal", "consensus", "completed"],
            "async_standup": ["open", "review", "completed"],
            "health_check": ["assessment", "results", "discussion", "completed"],
        },
    }


@router.get("/api/v1/accessibility", summary="Accessibility statement", tags=["api"])
async def accessibility_statement() -> dict:
    """Accessibility compliance statement."""
    return {
        "standard": "WCAG 2.1 AA",
        "compliance": "partial",
        "features": {
            "keyboard_navigation": True,
            "screen_reader_support": True,
            "color_contrast": "4.5:1 minimum",
            "focus_indicators": True,
            "reduced_motion": True,
            "form_labels": True,
        },
        "known_gaps": [
            "Drag-and-drop grouping needs keyboard alternative",
            "Real-time WebSocket updates need ARIA live regions",
            "Color-coded board items need text labels",
        ],
        "remediation_target": "Phase 4",
    }


@router.get("/api/v1/status", summary="System status", tags=["api"])
async def system_status(user: CurrentUser) -> dict:
    """Get overall system status."""
    return {
        "status": "operational",
        "version": "0.1.0",
        "phase": "Phase 3 - Multi-Ceremony Suite",
        "features": {
            "retrospectives": "live",
            "planning_poker": "live",
            "async_standups": "live",
            "ai_clustering": "live",
            "analytics": "live",
            "billing": "live",
            "jira_integration": "live",
            "erpnext_integration": "live",
            "slack_notifications": "live",
            "teams_notifications": "live",
            "health_checks": "live",
            "audit_log": "live",
            "soc2_readiness": "partial",
        },
    }
