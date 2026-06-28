"""Template governance API — org-level publishing and team customization."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.core.security import CurrentUser, require_role
from app.services.template_governance import TemplateGovernanceService

router = APIRouter()


@router.post("/templates/publish", summary="Publish org template")
async def publish_template(
    user: Annotated[CurrentUser, Depends(require_role("org_admin", "workspace_admin"))],
    template: dict,
) -> dict:
    """Publish a template at org level (locked, all teams can use)."""
    service = TemplateGovernanceService()
    return await service.publish_org_template(
        org_id=user.org_id or "",
        template_data=template,
    )


@router.get("/templates/org", summary="Get org templates")
async def get_org_templates(user: CurrentUser) -> dict:
    """Get all org-level published templates."""
    service = TemplateGovernanceService()
    templates = await service.get_org_templates(user.org_id or "")
    return {"templates": templates}


@router.post("/templates/{template_id}/customize", summary="Customize template")
async def customize_template(
    template_id: str,
    user: CurrentUser,
    customizations: dict,
) -> dict:
    """Create a team-level customization of a locked template."""
    service = TemplateGovernanceService()
    return await service.customize_template(
        template_id=template_id,
        team_id="",
        customizations=customizations,
    )


@router.post("/templates/{template_id}/lock", summary="Lock template")
async def lock_template(
    template_id: str,
    user: Annotated[CurrentUser, Depends(require_role("org_admin"))],
) -> dict:
    """Lock a template to prevent modifications."""
    service = TemplateGovernanceService()
    return await service.lock_template(template_id)


@router.post("/templates/{template_id}/unlock", summary="Unlock template")
async def unlock_template(
    template_id: str,
    user: Annotated[CurrentUser, Depends(require_role("org_admin"))],
) -> dict:
    """Unlock a template to allow modifications."""
    service = TemplateGovernanceService()
    return await service.unlock_template(template_id)
