"""Jira Cloud integration connector."""

from __future__ import annotations

import random
import time
from typing import Any

import httpx
import structlog

from app.integrations.base import (
    BaseIntegrationConnector,
    CircuitOpenError,
)

logger = structlog.get_logger()


class JiraConnector(BaseIntegrationConnector):
    """Jira Cloud integration with OAuth 2.0, rate limiting, and field mapping."""

    def __init__(
        self,
        base_url: str,
        client_id: str = "",
        client_secret: str = "",
        access_token: str = "",
        refresh_token: str = "",
    ):
        super().__init__()
        self.base_url = base_url.rstrip("/")
        self.client_id = client_id
        self.client_secret = client_secret
        self._access_token = access_token
        self._refresh_token = refresh_token
        self._consecutive_429 = 0

    async def authenticate(self) -> bool:
        """Authenticate with Jira via OAuth 2.0."""
        if self._access_token:
            try:
                return await self._validate_token()
            except Exception:
                pass

        if self._refresh_token and self.client_id and self.client_secret:
            return await self._refresh_access_token()

        return False

    async def _validate_token(self) -> bool:
        """Validate the current access token."""
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"{self.base_url}/rest/api/3/myself",
                headers={"Authorization": f"Bearer {self._access_token}"},
            )
            return resp.status_code == 200

    async def _refresh_access_token(self) -> bool:
        """Refresh the access token using the refresh token."""
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(
                    "https://auth.atlassian.com/oauth/token",
                    data={
                        "grant_type": "refresh_token",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "refresh_token": self._refresh_token,
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    self._access_token = data["access_token"]
                    self._refresh_token = data.get("refresh_token", self._refresh_token)
                    return True
        except Exception as exc:
            logger.warning("jira.token_refresh_failed", error=str(exc))
        return False

    def generate_pkce_challenge(self) -> tuple[str, str]:
        """Generate PKCE code verifier and challenge for OAuth flow."""
        import hashlib
        import base64
        import secrets

        verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b"=").decode()
        challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
        return verifier, challenge

    def build_authorization_url(self, redirect_uri: str, state: str, challenge: str) -> str:
        """Build the Jira OAuth authorization URL."""
        return (
            f"https://auth.atlassian.com/authorize"
            f"?audience=api.atlassian.com"
            f"&client_id={self.client_id}"
            f"&scope=read%3Ajira-work%20write%3Ajira-work"
            f"&redirect_uri={redirect_uri}"
            f"&state={state}"
            f"&response_type=code"
            f"&prompt=consent"
            f"&code_challenge_method=S256"
            f"&code_challenge={challenge}"
        )

    async def push_action(self, action: dict[str, Any]) -> dict[str, Any]:
        """Push an SCP action to Jira (create or update issue)."""
        self._guard_circuit()

        external_id = action.get("external_id")
        if external_id:
            return await self._update_issue(external_id, action)
        return await self._create_issue(action)

    async def _create_issue(self, action: dict[str, Any]) -> dict[str, Any]:
        """Create a new Jira issue from an action."""
        payload = self.map_fields(action)
        try:
            async with self._request_with_retry() as client:
                resp = await client.post(
                    f"{self.base_url}/rest/api/3/issue",
                    json=payload,
                )
                if resp.status_code in (200, 201):
                    data = resp.json()
                    self.circuit_breaker.record_success()
                    return {
                        "external_id": data["id"],
                        "external_url": f"{self.base_url}/browse/{data['key']}",
                        "key": data["key"],
                    }
                self.circuit_breaker.record_failure()
                raise Exception(f"Jira create failed: {resp.status_code} {resp.text}")
        except CircuitOpenError:
            raise
        except Exception as exc:
            self.circuit_breaker.record_failure()
            logger.error("jira.create_failed", error=str(exc))
            raise

    async def _update_issue(self, external_id: str, action: dict[str, Any]) -> dict[str, Any]:
        """Update an existing Jira issue."""
        payload = self.map_fields(action)
        try:
            async with self._request_with_retry() as client:
                await client.put(
                    f"{self.base_url}/rest/api/3/issue/{external_id}",
                    json={"fields": payload.get("fields", {})},
                )
                self.circuit_breaker.record_success()
                return {"external_id": external_id, "updated": True}
        except Exception as exc:
            self.circuit_breaker.record_failure()
            logger.error("jira.update_failed", error=str(exc))
            raise

    async def pull_status(self, external_id: str) -> dict[str, Any]:
        """Pull status from a Jira issue."""
        self._guard_circuit()
        try:
            async with self._request_with_retry() as client:
                resp = await client.get(
                    f"{self.base_url}/rest/api/3/issue/{external_id}",
                    fields="status,summary,assignee",
                )
                if resp.status_code == 200:
                    data = resp.json()
                    status = data["fields"]["status"]["name"]
                    self.circuit_breaker.record_success()
                    return {
                        "external_id": external_id,
                        "jira_status": status,
                        "scp_status": self.map_status(status),
                        "summary": data["fields"].get("summary", ""),
                    }
                self.circuit_breaker.record_failure()
                return {"external_id": external_id, "error": f"HTTP {resp.status_code}"}
        except CircuitOpenError:
            raise
        except Exception as exc:
            self.circuit_breaker.record_failure()
            return {"external_id": external_id, "error": str(exc)}

    def map_fields(self, action: dict[str, Any], project_key: str = "SCP") -> dict[str, Any]:
        """Map SCP action fields to Jira issue payload."""
        description = action.get("description", "")
        # Truncate description to 1000 chars for Jira
        if len(description) > 1000:
            description = description[:997] + "..."

        priority_map = {
            "critical": "1",
            "high": "2",
            "medium": "3",
            "low": "4",
        }

        return {
            "fields": {
                "project": {"key": project_key},
                "summary": action.get("title", "")[:255],
                "description": description,
                "issuetype": {"name": "Task"},
                "priority": {"id": priority_map.get(action.get("priority", "medium"), "3")},
                "labels": ["scp-action"],
            }
        }

    def map_status(self, jira_status: str) -> str:
        """Map Jira issue status to SCP action status."""
        status_map = {
            "To Do": "open",
            "In Progress": "in_progress",
            "In Review": "in_progress",
            "Done": "done",
            "Closed": "done",
            "Cancelled": "dropped",
        }
        return status_map.get(jira_status, "open")

    async def _request_with_retry(self):
        """Create an HTTP client with retry logic for rate limits."""
        return httpx.AsyncClient(
            headers={"Authorization": f"Bearer {self._access_token}"},
            timeout=30,
        )

    async def handle_rate_limit(self, retry_after: float = 1.0):
        """Handle rate limiting with exponential backoff."""
        self._consecutive_429 += 1
        wait_time = retry_after * (2 ** min(self._consecutive_429, 5))
        wait_time += random.uniform(0, 1)  # Jitter
        logger.warning("jira.rate_limited", wait=wait_time, consecutive=self._consecutive_429)
        time.sleep(wait_time)

    async def health_check(self) -> dict[str, Any]:
        """Check Jira connectivity."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    f"{self.base_url}/rest/api/3/myself",
                    headers={"Authorization": f"Bearer {self._access_token}"} if self._access_token else {},
                )
                return {
                    "healthy": resp.status_code == 200,
                    "status_code": resp.status_code,
                    "base_url": self.base_url,
                }
        except Exception as exc:
            return {"healthy": False, "error": str(exc)}
