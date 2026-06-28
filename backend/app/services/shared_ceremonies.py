"""Sprint review, decision log, and shared action register service."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


# ── Shared Action Register ────────────────────────────────────────────────────

class SharedActionRegister:
    """Cross-ceremony action register spanning retros, standups, poker, and reviews."""

    @staticmethod
    async def get_actions(
        team_id: str,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Get all actions across all ceremonies for a team with optional filters."""
        # In production: query actions table with team_id + filters
        filters = filters or {}
        ceremony_type = filters.get("ceremony_type")
        status = filters.get("status")
        priority = filters.get("priority")

        return [
            {
                "id": "action-001",
                "title": "Implement estimation poker",
                "status": "open",
                "priority": "high",
                "source_ceremony_type": "retrospective",
                "source_ceremony_id": "ceremony-001",
                "created_at": "2026-06-27",
            }
        ]

    @staticmethod
    async def get_metrics(team_id: str) -> dict[str, Any]:
        """Get action metrics across all ceremony types."""
        return {
            "team_id": team_id,
            "by_source": {
                "retrospective": {"total": 5, "completed": 2},
                "async_standup": {"total": 3, "completed": 1},
                "planning_poker": {"total": 0, "completed": 0},
                "sprint_review": {"total": 1, "completed": 0},
            },
            "total": 9,
            "completed": 3,
            "completion_rate": 33.3,
        }


# ── Decision Log ──────────────────────────────────────────────────────────────

class DecisionEntry(BaseModel):
    """A decision made during a ceremony."""
    id: str
    ceremony_id: str
    ceremony_type: str
    title: str
    context: str
    decision: str
    rationale: str
    stakeholders: list[str]
    created_at: str


class DecisionLog:
    """Log decisions made during ceremonies."""

    @staticmethod
    async def log_decision(
        ceremony_id: str,
        ceremony_type: str,
        title: str,
        context: str,
        decision: str,
        rationale: str,
        stakeholders: list[str] | None = None,
    ) -> dict[str, Any]:
        """Log a new decision."""
        return {
            "id": f"decision-{ceremony_id[:8]}",
            "ceremony_id": ceremony_id,
            "ceremony_type": ceremony_type,
            "title": title,
            "context": context,
            "decision": decision,
            "rationale": rationale,
            "stakeholders": stakeholders or [],
            "created_at": "2026-06-27T00:00:00Z",
        }

    @staticmethod
    async def get_decisions(team_id: str) -> list[dict[str, Any]]:
        """Get all decisions for a team."""
        return []


# ── Improvement Experiment ─────────────────────────────────────────────────────

class ExperimentEntry(BaseModel):
    """An improvement experiment tracked across sprints."""
    id: str
    hypothesis: str
    action: str
    expected_impact: str
    actual_impact: str | None = None
    status: str = "running"  # running, completed, abandoned
    started_at: str
    ended_at: str | None = None


class ExperimentTracker:
    """Track improvement experiments: hypothesis → action → outcome."""

    @staticmethod
    async def start_experiment(
        hypothesis: str,
        action: str,
        expected_impact: str,
    ) -> dict[str, Any]:
        """Start tracking an improvement experiment."""
        return {
            "id": f"exp-{hash(hypothesis) % 10000}",
            "hypothesis": hypothesis,
            "action": action,
            "expected_impact": expected_impact,
            "status": "running",
            "started_at": "2026-06-27T00:00:00Z",
        }

    @staticmethod
    async def complete_experiment(
        experiment_id: str,
        actual_impact: str,
    ) -> dict[str, Any]:
        """Complete an experiment with actual impact."""
        return {
            "id": experiment_id,
            "actual_impact": actual_impact,
            "status": "completed",
            "ended_at": "2026-07-27T00:00:00Z",
        }

    @staticmethod
    async def get_experiments(team_id: str, status: str | None = None) -> list[dict[str, Any]]:
        """Get improvement experiments for a team."""
        return []
