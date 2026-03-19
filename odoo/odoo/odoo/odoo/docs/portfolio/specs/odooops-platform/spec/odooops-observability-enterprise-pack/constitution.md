# OdooOps Observability & Enterprise Pack Constitution

**Version**: 1.0.0
**Status**: Draft
**Last Updated**: 2026-02-12
**Owner**: InsightPulse AI Platform Team

---

## Purpose

**OdooOps Observability & Enterprise Pack** provides comprehensive observability guarantees, enterprise governance, and operational intelligence for the OdooOps Platform, ensuring production-grade monitoring, alerting, and compliance for mission-critical Odoo deployments.

### What This Is

- **Observability-first** platform extension with OpenTelemetry instrumentation
- **Real-time alerting** with email/Slack/webhook notifications
- **Enterprise governance** (SSO/RBAC, audit streaming, SLA management)
- **Data export** (logs, traces, analytics) to external systems

### What This Is Not

- ❌ A standalone monitoring solution (extends OdooOps Platform)
- ❌ A tiered product (all observability features included)
- ❌ A replacement for application monitoring (complements Odoo-level monitoring)

---

## Non-Negotiables

### 1. OpenTelemetry-First

**Principle**: All instrumentation must use OpenTelemetry standard, not vendor-specific SDKs.

**Requirements**:
- OTLP protocol for metrics, traces, and logs
- Semantic conventions for naming and attributes
- Vendor-agnostic exporters (Prometheus, Loki, external SIEM)
- No lock-in to proprietary formats

**Rationale**: Ensures interoperability, future-proofs observability stack, and enables data portability.

### 2. 30-Day Standard Retention

**Principle**: All observability data retained for 30 days, consistently across all data types.

**Requirements**:
- Metrics: 30-day retention in Prometheus
- Logs: 30-day retention in Loki
- Traces: 30-day retention in Tempo or equivalent
- Automated cleanup after retention period

**Rationale**: Balances historical analysis needs with storage costs, provides sufficient incident investigation window.

### 3. No UI-Only Features

**Principle**: All observability operations accessible via API and CLI, not just web dashboards.

**Requirements**:
- Alert rule CRUD via API (no UI-only configuration)
- Drain configuration via CLI/API
- Metrics and logs queryable via API (PromQL, LogQL)
- Dashboard definitions as code (Grafana JSON)

**Rationale**: Enables automation, infrastructure-as-code patterns, and third-party integrations.

### 4. Audit Trail Integrity

**Principle**: All control plane operations logged immutably with cryptographic verification.

**Requirements**:
- Append-only audit log (no updates or deletes)
- Cryptographic signatures for log entries (HMAC or digital signatures)
- Tamper detection via hash chains
- Audit log export to external systems (SIEM integration)

**Rationale**: Ensures compliance, enables forensic investigations, and provides non-repudiation.

---

## Success Metrics

### Observability Effectiveness

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Alert Latency** | < 60 seconds | Time from condition trigger to notification sent |
| **Query Performance** | < 2 seconds | p95 latency for metrics/logs queries |
| **Data Completeness** | > 99.5% | % of expected data points received |
| **False Positive Rate** | < 5% | % of alerts that are not actionable |
| **MTTR Improvement** | 40% reduction | Mean time to resolution with observability vs without |

### Enterprise Governance

| Metric | Target | Measurement |
|--------|--------|-------------|
| **SSO Integration** | < 15 minutes | Time to configure SSO for new identity provider |
| **RBAC Coverage** | 100% | % of operations with role-based access control |
| **Audit Log Completeness** | 100% | % of control plane operations logged |
| **SLA Compliance** | > 99.5% | % of time platform meets SLA targets |
| **Audit Export Latency** | < 5 minutes | Time from action to external SIEM receipt |

### Operational Efficiency

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Alert Noise Reduction** | 60% fewer alerts | Compared to naive threshold-based alerts |
| **Dashboard Load Time** | < 3 seconds | p95 Grafana dashboard load time |
| **Storage Efficiency** | > 80% compression | Compressed vs uncompressed data |
| **Query Concurrency** | 50 concurrent queries | Queries supported without degradation |
| **Drain Throughput** | 10K events/sec | Events exported to external systems |

---

## Design Tenets

### 1. Instrumentation is Invisible

**Tenet**: Observability instrumentation must not degrade application performance or require code changes.

**Implications**:
- Automatic instrumentation where possible (FastAPI middleware, Celery hooks)
- Asynchronous data export (no blocking calls in request path)
- Resource limits for observability (< 5% CPU, < 100MB memory overhead)
- Graceful degradation if observability backend unavailable

**Example**:
```python
# Automatic instrumentation (no code changes required)
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

app = FastAPI()
FastAPIInstrumentor.instrument_app(app)  # Automatic trace/metric collection
```

### 2. Alerts are Actionable

**Tenet**: Every alert must have clear remediation steps, not just symptom descriptions.

**Implications**:
- Alerts include runbook links
- Severity levels (critical/warning/info) with response SLAs
- Alert context (current value, threshold, recent trend)
- Automatic incident creation in external systems (PagerDuty, OpsGenie)

**Example Alert**:
```yaml
alert: HighDeploymentFailureRate
severity: critical
condition: "deployment_failure_rate > 0.1"
description: "10%+ of deployments failing in last 10 minutes"
remediation: |
  1. Check recent deployment logs: `odooops logs <env> --since=10m`
  2. Review failed health gates: `odooops deployment get <id>`
  3. Rollback if necessary: `odooops rollback <env>`
runbook: https://docs.odooops.io/runbooks/deployment-failures
```

### 3. Data Ownership is Transparent

**Tenet**: Users control where observability data is stored and who has access.

**Implications**:
- All data stored in user-controlled infrastructure (not SaaS)
- Export to external systems via drains (Datadog, Splunk, S3)
- Data retention policies configurable per environment
- GDPR/compliance-friendly data handling

**Configuration**:
```yaml
# .odooops/observability.yaml
retention:
  metrics: 30d
  logs: 30d
  traces: 30d

drains:
  - type: s3
    bucket: logs-archive-bucket
    region: sgp1
  - type: webhook
    url: https://siem.example.com/ingest
    headers:
      Authorization: Bearer $SIEM_TOKEN
```

### 4. Progressive Disclosure

**Tenet**: Default dashboards show high-level health, drill-down reveals details on demand.

**Implications**:
- Single overview dashboard (platform health at-a-glance)
- Link-based drill-down (click metric → detailed dashboard)
- Contextual links (alert → related logs/traces)
- No information overload (limit to 6-8 key metrics per view)

**Dashboard Hierarchy**:
```
Platform Overview (5 metrics)
  ├─ Deployment Health (drill-down)
  │   ├─ Success Rate by Environment
  │   ├─ Deployment Duration (p50, p95, p99)
  │   └─ Failed Deployment Logs (contextual link)
  ├─ API Health (drill-down)
  │   ├─ Request Rate
  │   ├─ Latency Distribution
  │   └─ Error Rate by Endpoint
  └─ Database Health (drill-down)
      ├─ Connection Pool Utilization
      ├─ Query Performance
      └─ Backup Status
```

### 5. Cost-Conscious by Default

**Tenet**: Observability infrastructure costs should not exceed 10% of platform costs.

**Implications**:
- Aggressive data compression (Loki chunking, Prometheus compression)
- Sampling for traces (100% sample critical paths, 1% sample non-critical)
- Tiered storage (hot: 7 days, warm: 23 days)
- Cardinality limits (prevent metric explosion)

**Cost Optimization**:
```yaml
# Trace sampling configuration
sampling:
  critical_paths:
    - /api/v1/deployments  # 100% sample
    - /api/v1/environments  # 100% sample
  non_critical:
    - /api/v1/health  # 1% sample (high volume, low value)

# Cardinality limits
cardinality:
  max_labels_per_metric: 10
  max_unique_values: 1000
```

---

## Architectural Principles

### Separation of Concerns

**Control Plane** (orchestration):
- Alert rule engine
- Drain configuration
- SSO/RBAC management
- Audit log export

**Data Plane** (collection):
- OpenTelemetry Collector (metrics/traces/logs)
- Prometheus (metrics storage)
- Loki (log aggregation)
- Tempo (trace storage - optional)

**Presentation Layer** (visualization):
- Grafana (dashboards and queries)
- AlertManager (notification routing)
- API endpoints (programmatic access)

### Data Flow Architecture

```
[Odoo Workers] → [OTEL Collector] → [Prometheus] → [Grafana]
                        ↓              ↓
                     [Loki]        [Drains]
                        ↓              ↓
                   [Grafana]      [External SIEM]
```

**Key Characteristics**:
- Centralized collection (single OTEL Collector per cluster)
- Push-based metrics (workers push to collector)
- Pull-based scraping (Prometheus pulls from collector)
- Asynchronous export (drains don't block data collection)

### State Management

**Ephemeral State**:
- In-memory metrics buffer (OTEL Collector)
- Active trace contexts
- Alert evaluation state (AlertManager)

**Persistent State**:
- Metrics: Prometheus TSDB (30-day retention)
- Logs: Loki chunks (30-day retention)
- Traces: Tempo blocks (30-day retention)
- Audit Logs: PostgreSQL (90-day retention)

**Configuration State**:
- Alert rules: Git-tracked YAML (`monitoring/alerts/`)
- Dashboard definitions: Git-tracked JSON (`monitoring/dashboards/`)
- Drain configuration: Control plane database

---

## Adoption Criteria

### Minimum Viable Observability (MVO)

Before declaring "observability v1.0 ready":

- [ ] **Metrics Collection**: Prometheus scrapes OTEL Collector
- [ ] **Log Aggregation**: Loki receives logs from all services
- [ ] **Dashboards**: 5 core dashboards (platform, deployment, API, database, infrastructure)
- [ ] **Alerting**: 10 critical alerts configured (deployment failures, API errors, DB issues)
- [ ] **Retention**: 30-day retention enforced for all data types

### Production Readiness

Before deploying observability in production:

- [ ] **Alert Latency**: < 60 seconds (p95)
- [ ] **Query Performance**: < 2 seconds (p95)
- [ ] **Data Completeness**: > 99.5% (no dropped metrics/logs)
- [ ] **Drain Reliability**: Export to external systems without data loss
- [ ] **SSO Integration**: SAML/OIDC working for Grafana access

### Feature Completeness

Before considering feature-complete:

- [ ] **Advanced Alerting**: Anomaly detection, multi-condition alerts, alert grouping
- [ ] **Custom Dashboards**: User-created dashboards via API
- [ ] **SLA Tracking**: Automated SLA compliance reporting
- [ ] **Audit Streaming**: Real-time audit log export to SIEM
- [ ] **Cost Attribution**: Per-environment resource usage tracking

---

## Constraints and Limitations

### Technical Constraints

**Retention**:
- Maximum 30 days (hard limit due to storage costs)
- No historical data beyond 30 days
- Export to external systems for longer retention

**Cardinality**:
- Maximum 10 labels per metric
- Maximum 1000 unique values per label
- Alert on cardinality explosion

**Query Performance**:
- Maximum 100 concurrent queries
- Query timeout: 30 seconds
- Rate limiting: 60 queries/min per user

### Operational Constraints

**Storage**:
- 100GB allocated for metrics/logs/traces (combined)
- Automatic cleanup at 80% capacity
- No support for user-provided storage backends

**Drains**:
- Maximum 5 drains per platform
- Export rate limited to 10K events/sec
- Webhook timeout: 5 seconds

**Alerts**:
- Maximum 50 alert rules per platform
- Notification rate limiting (max 10/min to prevent alert storms)
- Alert de-duplication (5-minute window)

---

## Evolution and Governance

### Version Strategy

**Semantic Versioning**: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes to metrics/logs schema
- **MINOR**: New features (new data sources, drains, alert types)
- **PATCH**: Bug fixes, performance improvements

**Deprecation Policy**:
- 2 minor versions notice before removing metrics/logs
- Migration guides for schema changes
- Backward compatibility for 1 year minimum

### Specification Ownership

**Primary Owner**: InsightPulse AI Observability Team
**Reviewers**: Platform team, DevOps team, Security team
**Approval Process**: RFC for major changes, PR review for minor updates

---

## References

### Related Specifications

- **`spec/odooops-platform/`**: Core platform spec (this observability pack extends it)
- **`spec/platform-kit/`**: Generic observability patterns
- **`infra/monitoring/docker-compose.monitoring.yml`**: Existing Prometheus/Grafana setup

### External Standards

- **OpenTelemetry**: Instrumentation and data collection standard
- **Prometheus**: Metrics storage and querying
- **Loki**: Log aggregation and querying
- **OWASP Logging Cheat Sheet**: Secure logging practices
- **GDPR**: Data retention and privacy compliance

### Documentation

- **Architecture**: `docs/arch/PROD_RUNTIME_SNAPSHOT.md`
- **Monitoring**: `infra/monitoring/` (existing Prometheus/Grafana configs)
- **Supabase**: `docs/ai/SUPABASE.md` (audit log integration)

---

**Document Status**: ✅ Constitution finalized
**Next Steps**: Create PRD, Plan, and Tasks documents
**Review Cadence**: Quarterly (or on major observability changes)
