"""Retry and rate-limiting utilities for connectors.

Exponential backoff with jitter, token-bucket rate limiting,
and auto-pause logic matching Fivetran's 14-day failure threshold.
"""

from __future__ import annotations

import functools
import logging
import random
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable, TypeVar

from workbench.connectors.types import ConnectorState

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])

# Fivetran auto-pause: consecutive_failures * sync_frequency_hours > 336h (14 days)
AUTO_PAUSE_THRESHOLD_HOURS = 336


@dataclass
class RetryPolicy:
    """Configuration for retry behavior."""

    max_retries: int = 5
    base_delay: float = 1.0
    max_delay: float = 300.0
    exponential_base: float = 2.0
    jitter: bool = True
    retryable_exceptions: tuple[type[Exception], ...] = (Exception,)

    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay with optional jitter for a given attempt."""
        delay = min(
            self.base_delay * (self.exponential_base ** attempt),
            self.max_delay,
        )
        if self.jitter:
            delay = delay * (0.5 + random.random() * 0.5)  # noqa: S311
        return delay


def with_retry(policy: RetryPolicy | None = None) -> Callable[[F], F]:
    """Decorator that retries a function with exponential backoff."""
    if policy is None:
        policy = RetryPolicy()

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception: Exception | None = None
            for attempt in range(policy.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except policy.retryable_exceptions as exc:
                    last_exception = exc
                    if attempt == policy.max_retries:
                        logger.error(
                            "All %d retries exhausted for %s: %s",
                            policy.max_retries,
                            func.__name__,
                            exc,
                        )
                        raise
                    delay = policy.calculate_delay(attempt)
                    logger.warning(
                        "Attempt %d/%d for %s failed (%s), retrying in %.1fs",
                        attempt + 1,
                        policy.max_retries,
                        func.__name__,
                        exc,
                        delay,
                    )
                    time.sleep(delay)
            raise last_exception  # type: ignore[misc]

        return wrapper  # type: ignore[return-value]

    return decorator


class RateLimiter:
    """Token-bucket rate limiter for API calls.

    Thread-safe: uses a lock around token check + decrement (Bug 0e fix).
    """

    def __init__(self, requests_per_second: float = 10.0, burst: int | None = None) -> None:
        self.rate = requests_per_second
        self.burst = burst or max(1, int(requests_per_second * 2))
        self._tokens = float(self.burst)
        self._last_refill = time.monotonic()
        self._lock = threading.Lock()

    def acquire(self) -> None:
        """Block until a token is available. Thread-safe."""
        while True:
            with self._lock:
                self._refill()
                if self._tokens >= 1.0:
                    self._tokens -= 1.0
                    return
                sleep_time = (1.0 - self._tokens) / self.rate
            time.sleep(sleep_time)

    def _refill(self) -> None:
        """Refill tokens based on elapsed time. Must be called under lock."""
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(float(self.burst), self._tokens + elapsed * self.rate)
        self._last_refill = now


def should_auto_pause(
    state: ConnectorState,
    sync_frequency_hours: float = 1.0,
) -> bool:
    """Check if connector should be auto-paused due to sustained failures.

    Mirrors Fivetran: pause after cumulative failure window exceeds 14 days.
    """
    return state.consecutive_failures * sync_frequency_hours >= AUTO_PAUSE_THRESHOLD_HOURS
