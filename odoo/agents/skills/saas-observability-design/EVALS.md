# Evaluations: SaaS Observability Design

## Eval Criteria

| Criterion | Weight | Pass Condition |
|-----------|--------|----------------|
| Tenant context completeness | 25% | Every telemetry event includes tenant_id |
| Per-tenant query capability | 20% | Logs and metrics filterable by tenant_id |
| SLA measurement accuracy | 25% | SLA calculations match actual tenant experience |
| Cross-tenant isolation | 15% | Tenant cannot see other tenants' telemetry |
| Alert effectiveness | 15% | Alerts fire for real issues, no false positives |

## Eval Scenarios

### Scenario 1: Per-Tenant Log Query

- **Input**: Query logs for tenant "acme-corp" over the last hour
- **Expected**: Only acme-corp log entries returned, complete coverage
- **Fail condition**: Logs from other tenants included, or acme-corp logs missing

### Scenario 2: SLA Breach Detection

- **Input**: Tenant availability drops below 99.9% for 1 hour
- **Expected**: Alert fires within 5 minutes, dashboard shows breach
- **Fail condition**: No alert, or alert delayed beyond 15 minutes

### Scenario 3: Noisy Neighbor Identification

- **Input**: One tenant's request volume spikes 10x, degrading other tenants
- **Expected**: Tenant comparison query identifies the spike, correlated with other tenants' latency increase
- **Fail condition**: Cannot correlate high-usage tenant with performance degradation

### Scenario 4: Tenant Telemetry Isolation

- **Input**: Tenant admin accesses their observability dashboard
- **Expected**: Only their tenant's metrics, logs, and traces visible
- **Fail condition**: Any data from other tenants visible

## Grading Rubric

| Grade | Criteria |
|-------|----------|
| A | All 5 criteria pass, all 4 scenarios handled |
| B | 4/5 criteria pass, scenarios 1-3 handled |
| C | 3/5 criteria pass, basic per-tenant queries work |
| F | Tenant context missing from telemetry or cross-tenant leakage |

## Pass Criteria

Minimum grade B for production. Grade A required for platforms with tenant-facing SLA dashboards.
