# Prompt: Tenant Health & Alerting

## Context

You are the Tenant Lifecycle Operator designing per-tenant monitoring and alerting for a multi-tenant SaaS platform.

## Task

Given the observability stack, SLO definitions, and alert routing requirements, produce a monitoring design covering:

1. **Metrics design**: Define custom metrics with tenant-id as a required dimension. Include availability, latency, error rate, and throughput per tenant.
2. **SLO tracking**: Per-tenant SLO calculation using error budgets and burn rate. Define alert thresholds for fast-burn (immediate) and slow-burn (trending) scenarios.
3. **Alert rules**: Alert definitions with severity levels, tenant-aware routing (enterprise tenants get paged, free tenants get email), and deduplication rules.
4. **Dashboard design**: Platform-wide overview dashboard and per-tenant detail dashboard. Define access controls (tenant admins see only their own data).
5. **Anomaly detection**: Per-tenant baseline establishment, anomaly detection rules, and investigation playbooks.

## Constraints

- Metrics cardinality must be managed (tenant-id dimension + limited additional dimensions)
- SLO burn rate alerts must fire before the SLO budget is exhausted
- Enterprise tenant alerts must have faster response SLA than standard
- Per-tenant dashboards must enforce tenant isolation in data access

## Output Format

Metric definitions table, SLO burn rate calculations, alert rule YAML, dashboard wireframes, and anomaly detection playbook.
