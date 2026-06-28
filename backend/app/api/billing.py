"""Billing API — plans, checkout, webhooks, and subscription management."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from app.core.security import CurrentUser
from app.services.billing import BillingService, StripeService

router = APIRouter()


@router.get("/plans", summary="List available plans")
async def list_plans(user: CurrentUser) -> dict:
    """List all available subscription plans."""
    return {"plans": BillingService.list_plans()}


@router.get("/plans/{plan_id}", summary="Get plan details")
async def get_plan(plan_id: str, user: CurrentUser) -> dict:
    """Get details for a specific plan."""
    plan = BillingService.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


@router.get("/subscription", summary="Get current subscription")
async def get_subscription(user: CurrentUser) -> dict:
    """Get the current tenant's subscription status."""
    return {
        "plan": "free",
        "status": "active",
        "features": BillingService.get_plan("free")["features"],
    }


@router.post("/checkout", summary="Create checkout session")
async def create_checkout(
    user: CurrentUser,
    plan: str = "team",
    success_url: str = "https://scp.com/success",
    cancel_url: str = "https://scp.com/pricing",
) -> dict:
    """Create a Stripe Checkout session for plan upgrade."""
    stripe = StripeService()
    result = await stripe.create_checkout_session(
        plan=plan,
        customer_email=user.email,
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={"user_id": user.id, "org_id": user.org_id or ""},
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/portal", summary="Customer portal")
async def customer_portal(
    user: CurrentUser,
    return_url: str = "https://scp.com/dashboard",
) -> dict:
    """Create a Stripe Customer Portal session."""
    stripe = StripeService()
    result = await stripe.create_customer_portal_session(
        customer_id="",  # TODO: look up from subscription
        return_url=return_url,
    )
    return result


@router.post("/webhooks", summary="Stripe webhook handler")
async def stripe_webhook(request: Request) -> JSONResponse:
    """Handle incoming Stripe webhook events."""
    payload = await request.body()
    signature = request.headers.get("stripe-signature", "")

    stripe = StripeService()
    if not stripe.verify_webhook_signature(payload, signature):
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    import json
    event = json.loads(payload)
    result = await stripe.handle_webhook_event(event)
    return JSONResponse(content=result)


@router.get("/feature-check/{feature}", summary="Check feature access")
async def check_feature(feature: str, user: CurrentUser) -> dict:
    """Check if the current plan includes a specific feature."""
    return {
        "feature": feature,
        "allowed": BillingService.can_use_feature("free", feature),
    }


@router.get("/limits/{resource}", summary="Check plan limits")
async def check_limits(resource: str, user: CurrentUser, current_count: int = 0) -> dict:
    """Check if the team is within plan limits for a resource."""
    return BillingService.check_limits("free", resource, current_count)
