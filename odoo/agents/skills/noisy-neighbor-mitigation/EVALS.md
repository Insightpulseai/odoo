# Evaluations: Noisy Neighbor Mitigation

## Eval Criteria

| Criterion | Weight | Pass Condition |
|-----------|--------|----------------|
| Rate limits per tenant | 25% | Per-tenant rate limiting active at API gateway |
| Graceful throttling | 20% | 429 response with Retry-After, not 503 |
| Resource quotas enforced | 25% | CPU, memory, connections capped per tenant |
| Anomaly detection active | 20% | Baseline established, anomalies detected and actioned |
| Well-behaved tenants unaffected | 10% | No performance degradation for compliant tenants |

## Eval Scenarios

### Scenario 1: Burst Traffic from Single Tenant
- **Input**: Free tier tenant sends 1000 API calls in 1 minute (limit: 60)
- **Expected**: First 60 succeed, remaining get 429 with Retry-After: 60
- **Fail condition**: All 1000 succeed, or other tenants' requests fail

### Scenario 2: Database Connection Exhaustion
- **Input**: Standard tenant opens 50 concurrent database connections (limit: 10)
- **Expected**: First 10 succeed, remaining queue for 10s then timeout
- **Fail condition**: Tenant gets 50 connections, shared pool exhausted for others

### Scenario 3: Anomaly vs Legitimate Spike
- **Input**: Enterprise tenant runs end-of-month report generating 5x normal API calls
- **Expected**: Warning alert raised, no throttling (enterprise tier has high limits)
- **Fail condition**: Enterprise tenant throttled during legitimate business operation

### Scenario 4: Cascading Failure Prevention
- **Input**: One tenant's runaway process saturates shared compute
- **Expected**: CPU quota enforcement isolates impact to that tenant
- **Fail condition**: Other tenants experience latency increase > 10%
