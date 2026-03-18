# Prompt: SaaS Observability Design

## Context

You are the SaaS Platform Architect designing multi-tenant observability for a platform on Azure.

## Task

Given the telemetry sources, tenant context method, and SLA definitions, produce an observability design covering:

1. **Tenant context propagation**: How tenant_id flows through the entire request lifecycle — HTTP middleware enrichment, background job context, database query tagging. Every telemetry event must carry tenant_id.
2. **Per-tenant metrics**: Define custom metrics with tenant_id as a dimension — request rate, p50/p95/p99 latency, error rate, active sessions, resource consumption. Aggregation rules for platform-wide and per-tenant views.
3. **Log partitioning**: Log Analytics workspace strategy — single workspace with tenant_id column, workspace per stamp, or workspace per tenant. Query patterns for per-tenant log analysis.
4. **Distributed tracing**: OpenTelemetry configuration to propagate tenant context across service boundaries — Odoo web, background workers, external API calls. Trace sampling strategy per tenant tier.
5. **SLA dashboards**: Azure Dashboard or Grafana definitions tracking per-tenant availability, latency, and throughput against SLA targets. Automated SLA report generation per billing period.
6. **Anomaly detection**: Baseline establishment per tenant, deviation alerting, and automatic correlation with noisy neighbor indicators.

## Constraints

- Tenant A must never see tenant B's telemetry (even in shared Log Analytics workspace)
- Telemetry volume must be manageable — sampling for high-volume tenants
- SLA calculations must use server-side metrics (not client-reported)
- Alert volume must be controlled — aggregate before routing to on-call
- Retention must meet compliance requirements while controlling costs

## Output Format

Produce a structured document with:
- Telemetry pipeline architecture diagram
- Custom metric definitions table
- Log Analytics query examples (KQL)
- Dashboard JSON or Bicep definitions
- Alert rule specifications
