"""Onboarding and compliance API."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.security import CurrentUser
from app.services.onboarding import OnboardingService
from app.services.soc2 import SOC2Service

router = APIRouter()


# ── Onboarding ──────────────────────────────────────────────────────────────

@router.get("/onboarding/step", summary="Get current onboarding step")
async def get_onboarding_step(user: CurrentUser) -> dict:
    """Get the current onboarding step for the authenticated user."""
    user_data = {
        "has_team": False,  # TODO: check from DB
        "has_ceremony": False,
        "has_invited": False,
        "has_ai_tried": False,
        "days_since_signup": 3,
    }
    return OnboardingService.get_onboarding_step(user_data)


@router.get("/onboarding/emails", summary="Get pending onboarding emails")
async def get_pending_emails(user: CurrentUser) -> dict:
    """Get onboarding emails that should be sent."""
    user_data = {"days_since_signup": 3}
    emails = OnboardingService.get_pending_emails(user_data)
    return {"emails": emails}


# ── SOC 2 Readiness ─────────────────────────────────────────────────────────

@router.get("/soc2/readiness", summary="SOC 2 readiness status")
async def soc2_readiness(
    user: Annotated[CurrentUser, Depends(lambda: None)],  # Internal use
) -> dict:
    """Get overall SOC 2 readiness status."""
    return SOC2Service.get_readiness_summary()


@router.get("/soc2/controls/{control_id}", summary="Get control details")
async def get_control(control_id: str) -> dict:
    """Get details for a specific SOC 2 control."""
    control = SOC2Service.get_control(control_id)
    if not control:
        return {"error": "Control not found"}
    return control


@router.get("/soc2/gaps", summary="Get identified gaps")
async def get_gaps() -> dict:
    """Get all identified SOC 2 compliance gaps."""
    return {"gaps": SOC2Service.get_gaps()}
