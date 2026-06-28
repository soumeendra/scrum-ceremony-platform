"""Onboarding service — setup wizard, email sequences, and first-retro flow."""

from __future__ import annotations

from typing import Any

import structlog

logger = structlog.get_logger()

# ── Onboarding Email Sequence ────────────────────────────────────────────────

ONBOARDING_EMAILS = [
    {
        "day": 0,
        "subject": "Welcome to Scrum Ceremony Platform!",
        "template": "welcome",
        "description": "Welcome + quick start guide",
    },
    {
        "day": 1,
        "subject": "Create your first team",
        "template": "create_team",
        "description": "Guide to creating a team and inviting members",
    },
    {
        "day": 2,
        "subject": "Run your first retrospective",
        "template": "first_retro",
        "description": "Step-by-step retro setup walkthrough",
    },
    {
        "day": 5,
        "subject": "Pro tips for better retros",
        "template": "pro_tips",
        "description": "Best practices for facilitation",
    },
    {
        "day": 7,
        "subject": "Meet your AI facilitator",
        "template": "ai_intro",
        "description": "Introduce AI clustering and summary features",
    },
    {
        "day": 10,
        "subject": "What's your team health score?",
        "template": "health_check",
        "description": "Prompt to run first health check",
    },
    {
        "day": 14,
        "subject": "Your trial is ending — upgrade to keep your data",
        "template": "trial_ending",
        "description": "Conversion prompt with pricing",
    },
]


class OnboardingService:
    """Manage user onboarding flow and email sequences."""

    @staticmethod
    def get_onboarding_step(user: dict[str, Any]) -> dict[str, Any]:
        """Determine the current onboarding step for a user."""
        has_team = user.get("has_team", False)
        has_ceremony = user.get("has_ceremony", False)
        has_invited = user.get("has_invited", False)
        has_ai_tried = user.get("has_ai_tried", False)

        if not has_team:
            return {
                "step": "create_team",
                "title": "Create Your First Team",
                "description": "Set up your team to start running retrospectives",
                "action_url": "/teams/create",
            }

        if not has_invited:
            return {
                "step": "invite_team",
                "title": "Invite Your Team",
                "description": "Add team members to collaborate on retros",
                "action_url": "/teams/invite",
            }

        if not has_ceremony:
            return {
                "step": "first_retro",
                "title": "Run Your First Retro",
                "description": "Choose a template and start facilitating",
                "action_url": "/ceremonies/create",
            }

        if not has_ai_tried:
            return {
                "step": "try_ai",
                "title": "Try AI Features",
                "description": "Let AI cluster your themes and suggest actions",
                "action_url": "/ceremonies/latest/ai",
            }

        return {
            "step": "complete",
            "title": "You're all set!",
            "description": "Explore advanced features",
            "action_url": "/dashboard",
        }

    @staticmethod
    def get_pending_emails(user: dict[str, Any]) -> list[dict[str, Any]]:
        """Get onboarding emails that should be sent to the user."""
        day = user.get("days_since_signup", 0)
        return [
            email for email in ONBOARDING_EMAILS
            if email["day"] == day
        ]

    @staticmethod
    def mark_step_complete(user: dict[str, Any], step: str) -> dict[str, Any]:
        """Mark an onboarding step as completed."""
        user[f"step_{step}_complete"] = True
        return user
