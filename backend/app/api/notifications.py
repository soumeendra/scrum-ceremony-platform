"""Slack and Teams notification API endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.security import CurrentUser
from app.integrations.notifications import SlackService, TeamsService

router = APIRouter()


@router.post("/slack/send", summary="Send Slack message")
async def send_slack(
    user: CurrentUser,
    channel: str,
    text: str,
) -> dict:
    """Send a message to a Slack channel."""
    service = SlackService()
    result = await service.send_message(channel, text)
    return result


@router.post("/slack/retro-summary", summary="Send retro summary to Slack")
async def send_slack_retro(
    user: CurrentUser,
    channel: str,
    ceremony_title: str,
    summary: str,
    action_count: int = 0,
) -> dict:
    """Send a retro summary to Slack."""
    service = SlackService()
    result = await service.send_retro_summary(channel, ceremony_title, summary, action_count)
    return result


@router.post("/teams/send", summary="Send Teams message")
async def send_teams(
    user: CurrentUser,
    text: str,
) -> dict:
    """Send a message to Microsoft Teams."""
    service = TeamsService()
    result = await service.send_message(text)
    return result


@router.post("/teams/retro-summary", summary="Send retro summary to Teams")
async def send_teams_retro(
    user: CurrentUser,
    title: str,
    description: str,
    facts: dict[str, str] | None = None,
) -> dict:
    """Send a retro summary as a Teams adaptive card."""
    service = TeamsService()
    result = await service.send_adaptive_card(title, description, facts)
    return result
