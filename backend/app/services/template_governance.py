"""Template governance service for org-level ceremony standards."""

from __future__ import annotations

from typing import Any

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.models.template import Template

logger = structlog.get_logger()


class TemplateGovernanceService:
    """Manage org-level template publishing and team-level customization."""

    async def publish_org_template(
        self,
        org_id: str,
        template_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Publish a template at org level (locked, all teams can use)."""
        async with async_session_factory() as session:
            template = Template(
                name=template_data["name"],
                ceremony_type=template_data.get("ceremony_type", "retrospective"),
                scope="org",
                owner_id=org_id,
                tenant_id=org_id,
                phases=template_data.get("phases", ["collect", "cluster", "vote", "action"]),
                columns=template_data.get("columns", {"column1": "Default"}),
                is_locked=True,
                is_default=template_data.get("is_default", False),
            )
            session.add(template)
            await session.commit()

        return {
            "id": template.id,
            "name": template.name,
            "scope": "org",
            "is_locked": True,
            "status": "published",
        }

    async def get_org_templates(self, org_id: str) -> list[dict[str, Any]]:
        """Get all org-level published templates."""
        async with async_session_factory() as session:
            result = await session.execute(
                select(Template).where(
                    Template.scope == "org",
                    Template.tenant_id == org_id,
                )
            )
            templates = result.scalars().all()

        return [
            {
                "id": t.id,
                "name": t.name,
                "ceremony_type": t.ceremony_type,
                "is_locked": t.is_locked,
                "is_default": t.is_default,
            }
            for t in templates
        ]

    async def customize_template(
        self,
        template_id: str,
        team_id: str,
        customizations: dict[str, Any],
    ) -> dict[str, Any]:
        """Create a team-level customization of a locked template.

        Teams can customize non-structural settings (colors, labels)
        but cannot change the template structure (columns, phases).
        """
        async with async_session_factory() as session:
            # Get the original template
            result = await session.execute(
                select(Template).where(Template.id == template_id)
            )
            original = result.scalar_one_or_none()

            if not original:
                return {"error": "Template not found"}

            if not original.is_locked:
                return {"error": "Template is not locked — edit directly"}

            # Create team-scoped copy with customizations
            custom = Template(
                name=customizations.get("name", original.name),
                ceremony_type=original.ceremony_type,
                scope="team",
                owner_id=team_id,
                tenant_id=original.tenant_id,
                phases=original.phases,  # Cannot change structure
                columns=customizations.get("columns", original.columns),  # Can customize labels
                is_locked=False,
                is_default=False,
            )
            session.add(custom)
            await session.commit()

        return {
            "id": custom.id,
            "name": custom.name,
            "scope": "team",
            "parent_template_id": template_id,
            "status": "customized",
        }

    async def lock_template(self, template_id: str) -> dict[str, Any]:
        """Lock a template to prevent modifications."""
        async with async_session_factory() as session:
            result = await session.execute(
                select(Template).where(Template.id == template_id)
            )
            template = result.scalar_one_or_none()
            if template:
                template.is_locked = True
                await session.commit()

        return {"id": template_id, "locked": True}

    async def unlock_template(self, template_id: str) -> dict[str, Any]:
        """Unlock a template to allow modifications."""
        async with async_session_factory() as session:
            result = await session.execute(
                select(Template).where(Template.id == template_id)
            )
            template = result.scalar_one_or_none()
            if template:
                template.is_locked = False
                await session.commit()

        return {"id": template_id, "locked": False}
