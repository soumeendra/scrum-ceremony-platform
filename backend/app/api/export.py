"""Export API — PDF retro summaries and CSV action registers."""

from __future__ import annotations

import csv
import io
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import PlainTextResponse

from app.core.security import CurrentUser

router = APIRouter()


@router.get("/export/summary/{ceremony_id}", summary="Export retro summary as PDF")
async def export_summary_pdf(
    ceremony_id: str,
    user: CurrentUser,
) -> PlainTextResponse:
    """Export a retrospective summary as a PDF-like text document.

    In production: use a PDF library (weasyprint/reportlab) to generate real PDFs.
    For now: returns a formatted text document.
    """
    # In production: fetch ceremony data, generate PDF
    content = f"""
RETROSPECTIVE SUMMARY
Ceremony: {ceremony_id}
Generated: 2026-06-27

TOP THEMES
-----------
1. Communication gaps between frontend and backend
2. Sprint estimation accuracy needs improvement
3. Technical debt in the authentication module

TOP VOTED ITEMS
---------------
- Improve sprint planning (12 votes)
- Add more code reviews (8 votes)
- Reduce meeting overhead (6 votes)

PROPOSED ACTIONS
----------------
- Implement estimation poker (Owner: TBD, Due: Next sprint)
- Add PR review checklist (Owner: TBD, Due: Next sprint)

CARRY FORWARD
-------------
- CI pipeline optimization (carried from 3 previous retros)
- Documentation updates (carried from 2 previous retros)
"""
    return PlainTextResponse(
        content=content.strip(),
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename=retro-{ceremony_id}.txt"},
    )


@router.get("/export/actions/{team_id}", summary="Export action register as CSV")
async def export_actions_csv(
    team_id: str,
    user: CurrentUser,
    status: str | None = Query(None, description="Filter by status"),
) -> PlainTextResponse:
    """Export the action register as CSV."""
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "ID", "Title", "Status", "Priority", "Assignee",
        "Due Date", "Created At", "Ceremony ID",
    ])

    # In production: fetch from database
    # Placeholder data for structure
    writer.writerow([
        "action-001", "Implement estimation poker", "open", "high",
        "user@example.com", "2026-07-04", "2026-06-27", "ceremony-001",
    ])
    writer.writerow([
        "action-002", "Add PR review checklist", "in_progress", "medium",
        "user@example.com", "2026-07-11", "2026-06-27", "ceremony-001",
    ])

    return PlainTextResponse(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=actions-{team_id}.csv"},
    )


@router.get("/export/analytics/{team_id}", summary="Export analytics as CSV")
async def export_analytics_csv(
    team_id: str,
    user: CurrentUser,
) -> PlainTextResponse:
    """Export full analytics as CSV."""
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["Metric", "Value"])
    writer.writerow(["Team ID", team_id])
    writer.writerow(["Total Ceremonies", "0"])
    writer.writerow(["Total Actions", "0"])
    writer.writerow(["Completion Rate", "0%"])
    writer.writerow(["Participation Balance", "N/A"])

    return PlainTextResponse(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=analytics-{team_id}.csv"},
    )
