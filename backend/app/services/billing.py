"""Stripe billing service for subscription management and feature gating."""

from __future__ import annotations

import hashlib
import hmac
import time
from typing import Any

import httpx
import structlog

from app.core.config import settings

logger = structlog.get_logger()


# Plan Tiers

PLANS = {
    "free": {
        "name": "Free",
        "price_monthly": 0,
        "max_teams": 1,
        "max_ceremonies_per_month": 10,
        "max_participants": 10,
        "features": ["retrospectives", "basic_templates", "action_tracking"],
    },
    "team": {
        "name": "Team",
        "price_monthly": 29,
        "max_teams": 5,
        "max_ceremonies_per_month": -1,
        "max_participants": 50,
        "features": ["retrospectives", "all_templates", "action_tracking", "jira_sync", "analytics", "ai_clustering"],
    },
    "business": {
        "name": "Business",
        "price_monthly": 69,
        "max_teams": 20,
        "max_ceremonies_per_month": -1,
        "max_participants": 200,
        "features": ["retrospectives", "all_templates", "action_tracking", "jira_sync", "analytics", "ai_clustering", "health_checks", "erpnext_sync", "priority_support"],
    },
    "enterprise": {
        "name": "Enterprise",
        "price_monthly": 0,
        "max_teams": -1,
        "max_ceremonies_per_month": -1,
        "max_participants": -1,
        "features": ["all_features"],
    },
}


class StripeService:
    """Stripe Checkout and subscription management."""

    def __init__(self):
        self.api_key = settings.STRIPE_SECRET_KEY
        self.webhook_secret = settings.STRIPE_WEBHOOK_SECRET
        self.base_url = "https://api.stripe.com/v1"

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

    async def create_checkout_session(
        self,
        plan: str,
        customer_email: str,
        success_url: str,
        cancel_url: str,
        metadata: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Create a Stripe Checkout Session for plan upgrade."""
        if plan not in PLANS or plan == "free":
            return {"error": "Invalid plan"}

        price_id = f"price_{plan}"

        params = {
            "mode": "subscription",
            "customer_email": customer_email,
            "line_items[0][price]": price_id,
            "line_items[0][quantity]": "1",
            "success_url": success_url,
            "cancel_url": cancel_url,
            "metadata": metadata or {},
            "subscription_data[0][trial_period_days]": "14" if plan != "free" else "",
        }

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{self.base_url}/checkout/sessions",
                    headers=self.headers,
                    data=params,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return {
                        "session_id": data["id"],
                        "url": data["url"],
                    }
                logger.warning("stripe.checkout_failed", status=resp.status_code)
                return {"error": f"Stripe error: {resp.status_code}"}
        except Exception as exc:
            logger.error("stripe.checkout_error", error=str(exc))
            return {"error": str(exc)}

    async def create_customer_portal_session(
        self, customer_id: str, return_url: str
    ) -> dict[str, Any]:
        """Create a Stripe Customer Portal session."""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{self.base_url}/billing_portal/sessions",
                    headers=self.headers,
                    data={"customer": customer_id, "return_url": return_url},
                )
                if resp.status_code == 200:
                    return {"url": resp.json()["url"]}
                return {"error": f"Stripe error: {resp.status_code}"}
        except Exception as exc:
            return {"error": str(exc)}

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify Stripe webhook signature using HMAC-SHA256."""
        try:
            expected = hmac.new(
                self.webhook_secret.encode(),
                payload,
                hashlib.sha256,
            ).hexdigest()
            return hmac.compare_digest(expected, signature)
        except Exception:
            return False

    async def handle_webhook_event(self, event: dict[str, Any]) -> dict[str, Any]:
        """Process a Stripe webhook event."""
        event_type = event.get("type", "")

        handlers = {
            "checkout.session.completed": self._handle_checkout_completed,
            "customer.subscription.updated": self._handle_subscription_updated,
            "customer.subscription.deleted": self._handle_subscription_deleted,
            "invoice.payment_failed": self._handle_payment_failed,
        }

        handler = handlers.get(event_type, self._handle_unknown)
        return await handler(event)

    async def _handle_checkout_completed(self, event: dict[str, Any]) -> dict[str, Any]:
        session = event["data"]["object"]
        return {
            "type": "checkout.completed",
            "customer_id": session.get("customer"),
            "subscription_id": session.get("subscription"),
            "metadata": session.get("metadata", {}),
        }

    async def _handle_subscription_updated(self, event: dict[str, Any]) -> dict[str, Any]:
        sub = event["data"]["object"]
        return {
            "type": "subscription.updated",
            "customer_id": sub.get("customer"),
            "status": sub.get("status"),
            "current_period_end": sub.get("current_period_end"),
        }

    async def _handle_subscription_deleted(self, event: dict[str, Any]) -> dict[str, Any]:
        sub = event["data"]["object"]
        return {
            "type": "subscription.deleted",
            "customer_id": sub.get("customer"),
        }

    async def _handle_payment_failed(self, event: dict[str, Any]) -> dict[str, Any]:
        invoice = event["data"]["object"]
        return {
            "type": "payment.failed",
            "customer_id": invoice.get("customer"),
            "attempt_count": invoice.get("attempt_count", 1),
        }

    async def _handle_unknown(self, event: dict[str, Any]) -> dict[str, Any]:
        return {"type": "unknown", "event_type": event.get("type")}


class BillingService:
    """Plan management and feature gating."""

    @staticmethod
    def get_plan(plan_id: str) -> dict[str, Any]:
        return PLANS.get(plan_id, PLANS["free"])

    @staticmethod
    def list_plans() -> list[dict[str, Any]]:
        return [{"id": k, **v} for k, v in PLANS.items()]

    @staticmethod
    def can_use_feature(plan_id: str, feature: str) -> bool:
        plan = PLANS.get(plan_id, PLANS["free"])
        features = plan.get("features", [])
        return "all_features" in features or feature in features

    @staticmethod
    def check_limits(plan_id: str, resource: str, current_count: int) -> dict[str, Any]:
        plan = PLANS.get(plan_id, PLANS["free"])
        limit_key = f"max_{resource}"
        limit = plan.get(limit_key, 0)

        if limit == -1:
            return {"allowed": True, "limit": -1, "used": current_count}

        return {
            "allowed": current_count < limit,
            "limit": limit,
            "used": current_count,
            "remaining": max(0, limit - current_count),
        }

    @staticmethod
    def validate_trial(trial_start: str | None, plan: str) -> dict[str, Any]:
        if not trial_start or plan != "free":
            return {"in_trial": False}

        from datetime import datetime
        start = datetime.fromisoformat(trial_start)
        elapsed = (datetime.now().timestamp() - time.mktime(start.timetuple())) / 86400

        return {
            "in_trial": elapsed < 14,
            "days_remaining": max(0, 14 - round(elapsed)),
            "trial_expired": elapsed >= 14,
        }
