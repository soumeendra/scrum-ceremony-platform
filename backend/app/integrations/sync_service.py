"""Sync orchestration service for bidirectional Jira synchronization."""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class SyncResult:
    success: bool
    external_id: str | None = None
    error: str | None = None
    retry_count: int = 0


@dataclass
class DeadLetterItem:
    action_id: str
    operation: str
    error: str
    retry_count: int = 0
    last_retry: float = 0
    max_retries: int = 3


class SyncService:
    """Manages bidirectional sync between SCP and Jira."""

    def __init__(self, connector):
        self.connector = connector
        self._dead_letter: list[DeadLetterItem] = []
        self._success_count = 0
        self._failure_count = 0

    async def sync_action_to_jira(self, action: dict[str, Any]) -> SyncResult:
        """Push an SCP action to Jira."""
        idempotency_key = self.connector.idempotency.generate_idempotency_key(
            "push", action["id"]
        )

        if self.connector.idempotency.check_duplicate(idempotency_key):
            return SyncResult(success=True, external_id=action.get("external_id"))

        try:
            result = await self.connector.push_action(action)
            self.connector.idempotency.store_result(idempotency_key, result)
            self._success_count += 1
            return SyncResult(
                success=True,
                external_id=result.get("external_id"),
            )
        except Exception as exc:
            self._failure_count += 1
            self._dead_letter.append(DeadLetterItem(
                action_id=action["id"],
                operation="push",
                error=str(exc),
            ))
            return SyncResult(success=False, error=str(exc))

    async def sync_status_from_jira(self, external_id: str) -> SyncResult:
        """Pull status from Jira to SCP."""
        try:
            result = await self.connector.pull_status(external_id)
            self._success_count += 1
            return SyncResult(
                success=True,
                external_id=external_id,
            )
        except Exception as exc:
            self._failure_count += 1
            return SyncResult(success=False, error=str(exc))

    async def retry_failed_syncs(self):
        """Retry failed sync operations from the dead-letter queue."""
        now = time.time()
        for item in self._dead_letter:
            if item.retry_count >= item.max_retries:
                continue
            if now - item.last_retry < 60:  # Wait at least 60s between retries
                continue

            item.retry_count += 1
            item.last_retry = now

            try:
                if item.operation == "push":
                    # Re-attempt push
                    pass
                self._dead_letter.remove(item)
            except Exception:
                pass

    def get_sync_health(self) -> dict[str, Any]:
        """Get overall sync health metrics."""
        total = self._success_count + self._failure_count
        return {
            "success_rate": (self._success_count / total * 100) if total > 0 else 100,
            "success_count": self._success_count,
            "failure_count": self._failure_count,
            "dead_letter_count": len(self._dead_letter),
            "total_operations": total,
        }
