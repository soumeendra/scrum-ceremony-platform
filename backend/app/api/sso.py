"""SSO and SCIM provisioning API endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.core.security import CurrentUser, require_role
from app.services.sso import SCIMService, SSOService

router = APIRouter()


# ── SSO Configuration ────────────────────────────────────────────────────────

@router.get("/sso/status", summary="Get SSO status")
async def get_sso_status(
    user: Annotated[CurrentUser, Depends(require_role("org_admin"))],
) -> dict:
    """Get SSO configuration status for the tenant."""
    return SSOService.get_sso_status(user.org_id or "")


@router.post("/sso/saml/configure", summary="Configure SAML SSO")
async def configure_saml(
    user: Annotated[CurrentUser, Depends(require_role("org_admin"))],
    idp_metadata_url: str,
    idp_entity_id: str,
    idp_sso_url: str,
) -> dict:
    """Configure SAML SSO for the tenant."""
    return SSOService.configure_saml(
        tenant_id=user.org_id or "",
        idp_metadata_url=idp_metadata_url,
        idp_entity_id=idp_entity_id,
        idp_sso_url=idp_sso_url,
    )


@router.get("/sso/saml/metadata", summary="Get SP metadata")
async def get_sp_metadata(
    user: Annotated[CurrentUser, Depends(require_role("org_admin"))],
) -> str:
    """Generate SAML Service Provider metadata XML."""
    return SSOService.generate_sp_metadata(user.org_id or "")


# ── SCIM Provisioning ────────────────────────────────────────────────────────

@router.get("/scim/status", summary="Get SCIM status")
async def get_scim_status(
    user: Annotated[CurrentUser, Depends(require_role("org_admin"))],
) -> dict:
    """Get SCIM provisioning status."""
    service = SCIMService(user.org_id or "")
    return await service.get_provisioning_status()


@router.post("/scim/token", summary="Generate SCIM bearer token")
async def generate_scim_token(
    user: Annotated[CurrentUser, Depends(require_role("org_admin"))],
) -> dict:
    """Generate a new SCIM bearer token."""
    service = SCIMService(user.org_id or "")
    token = service.generate_bearer_token()
    return {
        "token": token,
        "base_url": service.base_url,
        "expires_in": "never",
        "message": "Store this token securely. It will not be shown again.",
    }


@router.post("/scim/Users", summary="Provision user (SCIM)")
async def provision_user(
    user: Annotated[CurrentUser, Depends(require_role("org_admin"))],
    scim_user: dict,
) -> dict:
    """Provision a new user via SCIM."""
    service = SCIMService(user.org_id or "")
    return await service.provision_user(scim_user)


@router.delete("/scim/users/{user_id}", summary="Deprovision user (SCIM)")
async def deprovision_user(
    user_id: str,
    user: Annotated[CurrentUser, Depends(require_role("org_admin"))],
) -> dict:
    """Deprovision a user via SCIM."""
    service = SCIMService(user.org_id or "")
    return await service.deprovision_user(user_id)


@router.put("/scim/groups", summary="Sync groups (SCIM)")
async def sync_groups(
    user: Annotated[CurrentUser, Depends(require_role("org_admin"))],
    groups: list[dict],
) -> dict:
    """Sync group memberships from IdP."""
    service = SCIMService(user.org_id or "")
    return await service.sync_groups(groups)
