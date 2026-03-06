"""Tests for retry, rate-limiting, and auto-pause logic."""

from __future__ import annotations

import time
from unittest.mock import MagicMock, patch

import pytest

from workbench.connectors.retry import (
    AUTO_PAUSE_THRESHOLD_HOURS,
    RateLimiter,
    RetryPolicy,
    should_auto_pause,
    with_retry,
)
from workbench.connectors.types import ConnectorState


class TestRetryPolicy:
    def test_defaults(self) -> None:
        policy = RetryPolicy()
        assert policy.max_retries == 5
        assert policy.base_delay == 1.0
        assert policy.max_delay == 300.0
        assert policy.jitter is True

    def test_calculate_delay_no_jitter(self) -> None:
        policy = RetryPolicy(base_delay=1.0, exponential_base=2.0, jitter=False)
        assert policy.calculate_delay(0) == 1.0
        assert policy.calculate_delay(1) == 2.0
        assert policy.calculate_delay(2) == 4.0
        assert policy.calculate_delay(3) == 8.0

    def test_calculate_delay_capped(self) -> None:
        policy = RetryPolicy(base_delay=1.0, max_delay=10.0, jitter=False)
        assert policy.calculate_delay(10) == 10.0

    def test_calculate_delay_with_jitter(self) -> None:
        policy = RetryPolicy(base_delay=1.0, jitter=True)
        delay = policy.calculate_delay(0)
        # With jitter: delay * (0.5 to 1.0), so 0.5 <= delay <= 1.0
        assert 0.5 <= delay <= 1.0


class TestWithRetry:
    def test_success_no_retry(self) -> None:
        call_count = 0

        @with_retry(RetryPolicy(max_retries=3))
        def succeed() -> str:
            nonlocal call_count
            call_count += 1
            return "ok"

        result = succeed()
        assert result == "ok"
        assert call_count == 1

    @patch("workbench.connectors.retry.time.sleep")
    def test_retry_then_succeed(self, mock_sleep: MagicMock) -> None:
        call_count = 0

        @with_retry(RetryPolicy(max_retries=3, base_delay=0.01, jitter=False))
        def fail_twice() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("transient")
            return "ok"

        result = fail_twice()
        assert result == "ok"
        assert call_count == 3
        assert mock_sleep.call_count == 2

    @patch("workbench.connectors.retry.time.sleep")
    def test_all_retries_exhausted(self, mock_sleep: MagicMock) -> None:
        @with_retry(RetryPolicy(max_retries=2, base_delay=0.01, jitter=False))
        def always_fail() -> str:
            raise RuntimeError("permanent")

        with pytest.raises(RuntimeError, match="permanent"):
            always_fail()

    def test_non_retryable_exception(self) -> None:
        @with_retry(RetryPolicy(retryable_exceptions=(ValueError,)))
        def raise_type_error() -> str:
            raise TypeError("not retryable")

        with pytest.raises(TypeError, match="not retryable"):
            raise_type_error()


class TestRateLimiter:
    def test_acquire_immediate(self) -> None:
        limiter = RateLimiter(requests_per_second=1000.0)
        start = time.monotonic()
        limiter.acquire()
        elapsed = time.monotonic() - start
        assert elapsed < 0.1  # Should be near-instant

    def test_burst_capacity(self) -> None:
        limiter = RateLimiter(requests_per_second=10.0, burst=5)
        assert limiter.burst == 5


class TestAutoPause:
    def test_no_pause_below_threshold(self) -> None:
        state = ConnectorState(connector_id="test", consecutive_failures=5)
        assert should_auto_pause(state, sync_frequency_hours=1.0) is False

    def test_pause_at_threshold(self) -> None:
        # 336 failures * 1 hour = 336 hours = 14 days
        state = ConnectorState(connector_id="test", consecutive_failures=336)
        assert should_auto_pause(state, sync_frequency_hours=1.0) is True

    def test_pause_with_frequency(self) -> None:
        # 48 failures * 7 hours = 336 hours = 14 days
        state = ConnectorState(connector_id="test", consecutive_failures=48)
        assert should_auto_pause(state, sync_frequency_hours=7.0) is True

    def test_threshold_constant(self) -> None:
        assert AUTO_PAUSE_THRESHOLD_HOURS == 336  # 14 * 24
