"""Base integration connector with circuit breaker and idempotency."""

from __future__ import annotations

import hashlib
import time
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitOpenError(Exception):
    """Raised when the circuit breaker is open."""
    pass


class CircuitBreaker:
    """Circuit breaker pattern for external API calls."""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time: float | None = None

    @property
    def state(self) -> CircuitState:
        if self._state == CircuitState.OPEN:
            if self._last_failure_time and (time.time() - self._last_failure_time) > self.recovery_timeout:
                self._state = CircuitState.HALF_OPEN
        return self._state

    def allow_request(self) -> bool:
        state = self.state
        if state == CircuitState.CLOSED:
            return True
        if state == CircuitState.HALF_OPEN:
            return True
        return False

    def record_success(self):
        self._failure_count = 0
        self._state = CircuitState.CLOSED

    def record_failure(self):
        self._failure_count += 1
        self._last_failure_time = time.time()
        if self._failure_count >= self.failure_threshold:
            self._state = CircuitState.OPEN

    def reset(self):
        self._failure_count = 0
        self._state = CircuitState.CLOSED
        self._last_failure_time = None


class IdempotencyMixin:
    """Generates and tracks idempotency keys for sync operations."""

    def __init__(self):
        self._completed: dict[str, Any] = {}

    def generate_idempotency_key(self, operation: str, entity_id: str) -> str:
        hour_period = int(time.time() / 3600)
        raw = f"{operation}:{entity_id}:{hour_period}"
        return hashlib.sha256(raw.encode()).hexdigest()[:32]

    def check_duplicate(self, key: str) -> bool:
        return key in self._completed

    def store_result(self, key: str, result: Any):
        self._completed[key] = result


class BaseIntegrationConnector(ABC):
    """Abstract base for external system connectors."""

    def __init__(self):
        self.circuit_breaker = CircuitBreaker()
        self.idempotency = IdempotencyMixin()

    def _guard_circuit(self):
        if not self.circuit_breaker.allow_request():
            raise CircuitOpenError("Circuit breaker is open — too many failures")

    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the external system."""
        ...

    @abstractmethod
    async def push_action(self, action: dict[str, Any]) -> dict[str, Any]:
        """Push an action to the external system."""
        ...

    @abstractmethod
    async def pull_status(self, external_id: str) -> dict[str, Any]:
        """Pull status from the external system."""
        ...

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """Check connectivity to the external system."""
        ...
