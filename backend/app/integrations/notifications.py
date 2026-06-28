"""Slack and Microsoft Teams integration service and API."""

from __future__ import annotations

from typing import Any

import httpx
import structlog

from app.core.config import settings

logger = structlog.get_logger()


class SlackService:
    """Send notifications to Slack channels."""

    def __init__(self, bot_token: str = ""):
        self.bot_token = bot_token
        self.base_url = "https://slack.com/api"

    async def send_message(
        self,
        channel: str,
        text: str,
        blocks: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Send a message to a Slack channel."""
        payload: dict[str, Any] = {"channel": channel, "text": text}
        if blocks:
            payload["blocks"] = blocks

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(
                    f"{self.base_url}/chat.postMessage",
                    headers={"Authorization": f"Bearer {self.bot_token}"},
                    json=payload,
                )
                return resp.json()
        except Exception as exc:
            logger.error("slack.send_failed", error=str(exc))
            return {"error": str(exc)}

    async def send_retro_summary(
        self,
        channel: str,
        ceremony_title: str,
        summary: str,
        action_count: int,
    ) -> dict[str, Any]:
        """Send a retro summary to Slack."""
        blocks = [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*{ceremony_title}* completed"},
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": summary[:2000]},
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*{action_count}* action items created"},
            },
        ]
        return await self.send_message(channel, f"Retro: {ceremony_title}", blocks)


class TeamsService:
    """Send notifications to Microsoft Teams channels."""

    def __init__(self, webhook_url: str = ""):
        self.webhook_url = webhook_url

    async def send_message(self, text: str) -> dict[str, Any]:
        """Send a message to a Teams incoming webhook."""
        payload = {"text": text}

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(self.webhook_url, json=payload)
                return {"status": resp.status_code}
        except Exception as exc:
            logger.error("teams.send_failed", error=str(exc))
            return {"error": str(exc)}

    async def send_adaptive_card(
        self,
        title: str,
        description: str,
        facts: dict[str, str] | None = None,
        actions: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        """Send an adaptive card to Teams."""
        card = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.4",
                        "body": [
                            {"type": "TextBlock", "text": title, "weight": "Bolder", "size": "Medium"},
                            {"type": "TextBlock", "text": description, "wrap": True},
                        ],
                    },
                }
            ],
        }

        if facts:
            card["attachments"][0]["content"]["body"].append({
                "type": "FactSet",
                "facts": [{"title": k, "value": v} for k, v in facts.items()],
            })

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(self.webhook_url, json=card)
                return {"status": resp.status_code}
        except Exception as exc:
            logger.error("teams.card_failed", error=str(exc))
            return {"error": str(exc)}
