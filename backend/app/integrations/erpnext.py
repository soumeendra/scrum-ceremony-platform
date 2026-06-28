"""ERPNext integration connector for CRM and finance sync."""

from __future__ import annotations

import json
from typing import Any

import httpx
import structlog

from app.core.config import settings

logger = structlog.get_logger()


# ── Custom Doctype Schemas ────────────────────────────────────────────────────

SCP_TEAM_DOCTYPE = {
    "doctype": "SCP Team",
    "fields": {
        "team_id": "",
        "team_name": "",
        "workspace": "",
        "member_count": 0,
        "plan": "free",
        "created_at": "",
    },
}

SCP_SUBSCRIPTION_DOCTYPE = {
    "doctype": "SCP Subscription",
    "fields": {
        "organization": "",
        "plan": "free",
        "status": "active",
        "stripe_customer_id": "",
        "stripe_subscription_id": "",
        "trial_end": "",
        "current_period_start": "",
        "current_period_end": "",
    },
}

SCP_PLAN_DOCTYPE = {
    "doctype": "SCP Plan",
    "fields": {
        "plan_name": "Team",
        "price_monthly": 29,
        "max_teams": 5,
        "max_ceremonies_per_month": -1,
        "features": "[]",
    },
}

SCP_USAGE_DOCTYPE = {
    "doctype": "SCP Usage Metric",
    "fields": {
        "team": "",
        "period": "",
        "ceremony_count": 0,
        "action_count": 0,
        "participant_count": 0,
    },
}


class ERPNextClient:
    """Async client for ERPNext REST API."""

    def __init__(self, url: str | None = None, api_key: str | None = None, api_secret: str | None = None):
        self.base_url = (url or settings.ERPNEXT_URL).rstrip("/")
        self.api_key = api_key or settings.ERPNEXT_API_KEY
        self.api_secret = api_secret or settings.ERPNEXT_API_SECRET

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"token {self.api_key}:{self.api_secret}",
            "Content-Type": "application/json",
        }

    async def create_doctype(self, doctype: str, fields: dict[str, Any]) -> dict[str, Any]:
        """Create a new document in ERPNext."""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{self.base_url}/api/resource/{doctype}",
                    headers=self.headers,
                    json=fields,
                )
                if resp.status_code in (200, 201):
                    return resp.json().get("data", {})
                logger.warning("erpnext.create_failed", doctype=doctype, status=resp.status_code)
                return {}
        except Exception as exc:
            logger.error("erpnext.create_error", error=str(exc))
            return {}

    async def get_doctype(self, doctype: str, name: str) -> dict[str, Any]:
        """Get a document by doctype and name."""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    f"{self.base_url}/api/resource/{doctype}/{name}",
                    headers=self.headers,
                )
                if resp.status_code == 200:
                    return resp.json().get("data", {})
                return {}
        except Exception as exc:
            logger.error("erpnext.get_error", error=str(exc))
            return {}

    async def update_doctype(self, doctype: str, name: str, fields: dict[str, Any]) -> dict[str, Any]:
        """Update an existing document."""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.put(
                    f"{self.base_url}/api/resource/{doctype}/{name}",
                    headers=self.headers,
                    json=fields,
                )
                if resp.status_code == 200:
                    return resp.json().get("data", {})
                return {}
        except Exception as exc:
            logger.error("erpnext.update_error", error=str(exc))
            return {}

    async def health_check(self) -> bool:
        """Check ERPNext connectivity."""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(
                    f"{self.base_url}/api/method/ping",
                    headers=self.headers,
                )
                return resp.status_code == 200
        except Exception:
            return False


class ERPNextSyncService:
    """Orchestrate sync flows between SCP and ERPNext."""

    def __init__(self):
        self.client = ERPNextClient()

    async def sync_trial_signup(self, org_id: str, org_name: str, email: str) -> dict[str, Any]:
        """Sync a trial signup to ERPNext CRM as a Lead."""
        return await self.client.create_doctype("Lead", {
            "email": email,
            "company_name": org_name,
            "lead_source": "Scrum Ceremony Platform",
            "status": "Lead",
            "custom_scp_org_id": org_id,
        })

    async def sync_paid_conversion(self, org_id: str, plan: str, stripe_customer_id: str) -> dict[str, Any]:
        """Convert a trial lead to a customer."""
        return await self.client.create_doctype("Customer", {
            "customer_name": org_id,
            "customer_type": "Company",
            "custom_scp_plan": plan,
            "custom_stripe_customer_id": stripe_customer_id,
        })

    async def sync_subscription(self, org_id: str, plan: str, status: str, stripe_sub_id: str) -> dict[str, Any]:
        """Sync subscription state to ERPNext."""
        return await self.client.create_doctype("SCP Subscription", {
            "organization": org_id,
            "plan": plan,
            "status": status,
            "stripe_subscription_id": stripe_sub_id,
        })

    async def sync_usage_metrics(self, team_id: str, period: str, ceremonies: int, actions: int, participants: int) -> dict[str, Any]:
        """Sync usage metrics to ERPNext."""
        return await self.client.create_doctype("SCP Usage Metric", {
            "team": team_id,
            "period": period,
            "ceremony_count": ceremonies,
            "action_count": actions,
            "participant_count": participants,
        })
