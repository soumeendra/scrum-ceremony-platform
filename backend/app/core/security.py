"""JWT verification via Clerk JWKS and FastAPI auth dependencies."""

from __future__ import annotations

import time
from dataclasses import dataclass
from functools import lru_cache
from typing import Annotated

import httpx
import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from app.core.config import settings

logger = structlog.get_logger()

_bearer_scheme = HTTPBearer(auto_error=False)


# ── Data models ────────────────────────────────────────────────────────────────

class ClerkUser(BaseModel):
    """Decoded Clerk JWT payload (minimal fields we care about)."""

    id: str
    email: str
    org_id: str | None = None
    role: str = "member"


# ── JWKS helpers ──────────────────────────────────────────────────────────────

_JWKS_CACHE_MAX_AGE = 3600  # seconds


class ClerkJWKS:
    """Fetch and cache the Clerk JSON Web Key Set."""

    _jwks: dict | None = None
    _fetched_at: float = 0

    @classmethod
    async def fetch(cls) -> dict:
        """Return the cached JWKS, refreshing if stale."""
        now = time.monotonic()
        if cls._jwks is None or (now - cls._fetched_at) > _JWKS_CACHE_MAX_AGE:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(settings.CLERK_JWKS_URL)
                resp.raise_for_status()
                cls._jwks = resp.json()
                cls._fetched_at = now
                logger.info("jwks.refreshed")
        return cls._jwks  # type: ignore[return-value]


def _find_key(kid: str, jwks: dict) -> dict:
    """Locate the JWK whose ``kid`` matches the token header."""
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return key
    raise KeyError(f"No matching key for kid={kid!r}")


# ── Token verification ─────────────────────────────────────────────────────────

async def verify_token(token: str) -> ClerkUser:
    """Validate a Clerk JWT and return a ``ClerkUser``."""
    try:
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        if kid is None:
            raise JWTError("Missing kid in token header")

        jwks = await ClerkJWKS.fetch()
        key_data = _find_key(kid, jwks)
        public_key = jwt.construct_key(key_data)  # type: ignore[attr-defined]

        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            options={"verify_aud": False},
        )

        return ClerkUser(
            id=payload.get("sub", ""),
            email=payload.get("email", ""),
            org_id=payload.get("org_id") or payload.get("org_id", None),
            role=payload.get("role", "member"),
        )
    except JWTError as exc:
        logger.warning("jwt.invalid", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc
    except KeyError as exc:
        logger.warning("jwks.key_not_found", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token signing key not found",
        ) from exc


# ── FastAPI dependencies ───────────────────────────────────────────────────────

async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)],
) -> ClerkUser:
    """Return the authenticated ``ClerkUser`` or raise 401."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return await verify_token(credentials.credentials)


CurrentUser = Annotated[ClerkUser, Depends(get_current_user)]


def require_role(*allowed_roles: str):
    """Dependency factory that enforces the user's role is in *allowed_roles*."""

    async def _check(user: Annotated[ClerkUser, Depends(get_current_user)]) -> ClerkUser:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user

    return _check
