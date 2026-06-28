"""Shared ceremonies API — sprint review, decision log, experiment tracking."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.security import CurrentUser
from app.services.shared_ceremonies import (
    DecisionLog,
    ExperimentTracker,
    SharedActionRegister,
)

router = APIRouter()


# ── Shared Action Register ────────────────────────────────────────────────────

@router.get("/actions", summary="Get shared action register")
async def get_shared_actions(
    user: CurrentUser,
    ceremony_type: str | None = None,
    status: str | None = None,
) -> dict:
    """Get all actions across all ceremonies for the tenant."""
    filters = {}
    if ceremony_type:
        filters["ceremony_type"] = ceremony_type
    if status:
        filters["status"] = status

    actions = await SharedActionRegister.get_actions(
        team_id="",  # TODO: get from user's team
        filters=filters if filters else None,
    )
    return {"actions": actions, "total": len(actions)}


@router.get("/actions/metrics", summary="Get action metrics by source")
async def get_action_metrics_by_source(user: CurrentUser) -> dict:
    """Get action metrics broken down by ceremony type."""
    metrics = await SharedActionRegister.get_metrics("")
    return metrics


# ── Decision Log ──────────────────────────────────────────────────────────────

@router.post("/decisions", summary="Log a decision")
async def log_decision(
    user: CurrentUser,
    ceremony_id: str,
    ceremony_type: str,
    title: str,
    context: str,
    decision: str,
    rationale: str,
    stakeholders: list[str] | None = None,
) -> dict:
    """Log a decision made during a ceremony."""
    result = await DecisionLog.log_decision(
        ceremony_id=ceremony_id,
        ceremony_type=ceremony_type,
        title=title,
        context=context,
        decision=decision,
        rationale=rationale,
        stakeholders=stakeholders,
    )
    return result


@router.get("/decisions", summary="Get decision log")
async def get_decisions(user: CurrentUser) -> dict:
    """Get all decisions for the tenant."""
    decisions = await DecisionLog.get_decisions("")
    return {"decisions": decisions, "total": len(decisions)}


# ── Improvement Experiments ───────────────────────────────────────────────────

@router.post("/experiments", summary="Start an experiment")
async def start_experiment(
    user: CurrentUser,
    hypothesis: str,
    action: str,
    expected_impact: str,
) -> dict:
    """Start tracking an improvement experiment."""
    return await ExperimentTracker.start_experiment(hypothesis, action, expected_impact)


@router.post("/experiments/{experiment_id}/complete", summary="Complete an experiment")
async def complete_experiment(
    experiment_id: str,
    user: CurrentUser,
    actual_impact: str,
) -> dict:
    """Complete an experiment with actual impact."""
    return await ExperimentTracker.complete_experiment(experiment_id, actual_impact)


@router.get("/experiments", summary="Get experiments")
async def get_experiments(
    user: CurrentUser,
    status: str | None = None,
) -> dict:
    """Get improvement experiments."""
    experiments = await ExperimentTracker.get_experiments("", status)
    return {"experiments": experiments, "total": len(experiments)}
