"""OTel tracing setup stub."""

from __future__ import annotations

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider

_tracer: trace.Tracer | None = None


def configure_tracing(service_name: str = "agent-platform", otlp_endpoint: str | None = None) -> None:
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    if otlp_endpoint:
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint)))
    trace.set_tracer_provider(provider)
    global _tracer
    _tracer = trace.get_tracer(service_name)


def get_tracer() -> trace.Tracer:
    return _tracer or trace.get_tracer("agent-platform")
