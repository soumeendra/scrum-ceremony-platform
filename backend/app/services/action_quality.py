"""Action quality scoring service.

Evaluates action items against best-practice criteria and returns a
0-100 score with actionable issues and suggestions.
"""

from __future__ import annotations

import re

from app.models.action import Action
from app.schemas.action import ActionQualityScore


# ── Scoring weights ────────────────────────────────────────────────────────────

WEIGHTS: dict[str, int] = {
    "has_assignee": 20,
    "has_due_date": 15,
    "has_measurable_outcome": 25,
    "title_is_specific": 20,
    "description_has_steps": 20,
}

# Vague words that indicate a non-specific title
_VAGUE_WORDS = {"stuff", "things", "something", "somehow", "maybe", "improve", "better", "fix", "handle", "look into", "review"}

# Patterns suggesting a measurable outcome
_MEASURABLE_PATTERNS = [
    re.compile(r"\d+%"),  # percentage
    re.compile(r"\d+\s*(ms|s|sec|min|hr|hours?|days?|weeks?)"),  # time units
    re.compile(r"\d+\s*(users?|requests?|tickets?|bugs?|errors?)"),  # count units
    re.compile(r"(reduce|increase|decrease|achieve|reach|deliver|ship|close|resolve)\b", re.IGNORECASE),
]

# Patterns suggesting actionable steps in description
_STEP_PATTERNS = [
    re.compile(r"^\s*[-*•]\s+", re.MULTILINE),  # bullet points
    re.compile(r"^\s*\d+[.)]\s+", re.MULTILINE),  # numbered list
    re.compile(r"(first|then|next|finally|step\s+\d+)", re.IGNORECASE),
    re.compile(r"(subtask|task|action|follow.up|followup)", re.IGNORECASE),
]


def score_action(action: Action) -> ActionQualityScore:
    """Score an action item on a 0-100 scale.

    Checks:
    - has_assignee: action is assigned to someone
    - has_due_date: action has a target date
    - has_measurable_outcome: description contains measurable criteria
    - title_is_specific: title is concrete and actionable
    - description_has_steps: description contains actionable steps

    Returns an ActionQualityScore with the score, issues, and suggestions.
    """
    score = 0
    issues: list[str] = []
    suggestions: list[str] = []

    # 1. Has assignee
    if action.assignee_id:
        score += WEIGHTS["has_assignee"]
    else:
        issues.append("No assignee — action may not be completed")
        suggestions.append("Assign the action to a specific team member")

    # 2. Has due date
    if action.due_date:
        score += WEIGHTS["has_due_date"]
    else:
        issues.append("No due date — action may be deprioritized indefinitely")
        suggestions.append("Set a realistic due date to create accountability")

    # 3. Has measurable outcome
    measurable_text = f"{action.title or ''} {action.description or ''}"
    has_measurable = any(p.search(measurable_text) for p in _MEASURABLE_PATTERNS)
    if has_measurable:
        score += WEIGHTS["has_measurable_outcome"]
    else:
        issues.append("No measurable outcome — unclear when the action is complete")
        suggestions.append(
            "Add a measurable criterion (e.g., 'reduce latency by 20%', 'close 5 tickets')"
        )

    # 4. Title is specific
    title_lower = (action.title or "").lower()
    title_words = set(title_lower.split())
    is_specific = (
        len(action.title or "") >= 10
        and not any(vague in title_lower for vague in _VAGUE_WORDS)
        and len(title_words) >= 3
    )
    if is_specific:
        score += WEIGHTS["title_is_specific"]
    else:
        issues.append("Title is vague or too short — unclear what needs to be done")
        suggestions.append(
            "Use a specific, action-oriented title (e.g., 'Migrate auth service to OAuth2')"
        )

    # 5. Description has steps
    desc = action.description or ""
    has_steps = any(p.search(desc) for p in _STEP_PATTERNS) or len(desc) > 100
    if has_steps:
        score += WEIGHTS["description_has_steps"]
    else:
        issues.append("Description lacks actionable steps — hard to track progress")
        suggestions.append(
            "Break the action into concrete steps or subtasks in the description"
        )

    return ActionQualityScore(
        action_id=action.id,
        score=score,
        issues=issues,
        suggestions=suggestions,
    )
