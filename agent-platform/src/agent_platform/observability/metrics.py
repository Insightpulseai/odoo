"""OTel metrics stub."""

from __future__ import annotations

from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider

_meter: metrics.Meter | None = None


def configure_metrics(service_name: str = "agent-platform") -> None:
    provider = MeterProvider()
    metrics.set_meter_provider(provider)
    global _meter
    _meter = metrics.get_meter(service_name)


def get_meter() -> metrics.Meter:
    return _meter or metrics.get_meter("agent-platform")
