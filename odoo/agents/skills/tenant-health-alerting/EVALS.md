# Evaluations: Tenant Health & Alerting

## Eval Criteria

| Criterion | Weight | Pass Condition |
|-----------|--------|----------------|
| Tenant-dimensioned metrics | 25% | All key metrics include tenant-id |
| SLO burn rate alerting | 25% | Fast and slow burn alerts configured |
| Tier-aware routing | 20% | Enterprise gets faster alert response |
| Dashboard isolation | 15% | Tenants see only their own data |
| Anomaly detection active | 15% | Baselines established, anomalies flagged |

## Eval Scenarios

### Scenario 1: Single Tenant Degradation
- **Input**: One enterprise tenant's p95 latency increases 5x while others are normal
- **Expected**: Tenant-specific alert fires, routed to on-call via PagerDuty
- **Fail condition**: Alert aggregated with platform-wide metrics, individual tenant issue hidden

### Scenario 2: SLO Budget Exhaustion Warning
- **Input**: Tenant consuming error budget at 5x normal rate
- **Expected**: Slow-burn alert fires 3 days before budget exhaustion
- **Fail condition**: SLO breached before any alert fires

### Scenario 3: Dashboard Tenant Isolation
- **Input**: Tenant admin accesses their monitoring dashboard
- **Expected**: Dashboard shows only their tenant's metrics and logs
- **Fail condition**: Other tenants' data visible in dashboard queries

### Scenario 4: Platform-Wide vs Tenant-Specific Issue
- **Input**: Database latency increases affecting all tenants
- **Expected**: Platform-wide alert fires first; per-tenant alerts suppressed as correlating
- **Fail condition**: Alert storm with separate alerts per tenant, obscuring root cause
