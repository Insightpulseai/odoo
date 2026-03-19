# Checklist: SaaS Observability Design

## Pre-flight

- [ ] Telemetry sources inventoried (app logs, metrics, traces, infra)
- [ ] Tenant context propagation method selected
- [ ] SLA targets defined per tier
- [ ] Retention and compliance requirements documented
- [ ] Budget for observability infrastructure estimated

## Tenant Context Propagation

- [ ] HTTP middleware enriches all requests with tenant_id
- [ ] Background jobs carry tenant context from triggering request
- [ ] Database queries tagged with tenant_id for slow query attribution
- [ ] External API calls propagate tenant context via headers
- [ ] Tenant_id present in every log entry, metric, and trace span

## Metrics

- [ ] Custom metrics defined: request_rate, latency (p50/p95/p99), error_rate per tenant
- [ ] Resource metrics collected: CPU, memory, connections per tenant (where possible)
- [ ] Aggregation rules: per-tenant, per-stamp, platform-wide views
- [ ] Metric cardinality managed (tenant_id dimension bounded by tenant count)
- [ ] Application Insights or Azure Monitor configured with custom dimensions

## Logs

- [ ] Log Analytics workspace strategy decided (single with filtering, per-stamp)
- [ ] All log entries include tenant_id, request_id, and timestamp
- [ ] Structured logging format (JSON) enforced
- [ ] Log retention configured per compliance requirements
- [ ] KQL queries created for common per-tenant investigations

## Distributed Tracing

- [ ] OpenTelemetry SDK integrated into application
- [ ] Trace context propagated across service boundaries
- [ ] Tenant_id added as span attribute
- [ ] Sampling strategy defined (higher sampling for enterprise tier)
- [ ] Trace retention appropriate for debugging needs

## SLA Dashboards

- [ ] Per-tenant availability dashboard (uptime percentage)
- [ ] Per-tenant latency dashboard (p50, p95, p99)
- [ ] SLA compliance indicator (green/yellow/red per tenant)
- [ ] Automated SLA report generation per billing period
- [ ] Dashboard access restricted to appropriate roles

## Alerting

- [ ] Per-tenant alert rules for SLA breach
- [ ] Platform-wide alert rules for systemic issues
- [ ] Alert aggregation to prevent alert fatigue
- [ ] Escalation paths defined (PagerDuty, email, Slack)
- [ ] Alert suppression during planned maintenance

## Post-flight

- [ ] Per-tenant log query returns correct tenant data only
- [ ] SLA dashboard shows accurate metrics for test tenant
- [ ] Alert fires correctly when SLA threshold breached
- [ ] Trace spans include tenant_id across all services
- [ ] Cross-tenant telemetry isolation verified
