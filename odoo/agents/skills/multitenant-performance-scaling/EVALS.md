# Evaluations: Multitenant Performance & Scaling

## Eval Criteria

| Criterion | Weight | Pass Condition |
|-----------|--------|----------------|
| Scaling validated by test | 30% | Load test evidence shows scaling works under multi-tenant load |
| Per-tenant predictability | 25% | Individual tenant SLOs met during shared infrastructure scaling |
| Scale-down graceful | 20% | No request failures or connection drops during scale-down |
| Cost efficiency | 15% | No over-provisioning during low-traffic periods |
| CDN isolation | 10% | Cache key includes tenant-id, no cross-tenant cache hits |

## Eval Scenarios

### Scenario 1: Scaling Under Multi-Tenant Load
- **Input**: 100 tenants generating 750 req/sec total
- **Expected**: Platform scales to handle load, all tenants meet SLO
- **Fail condition**: SLO breach for any tenant during scaling

### Scenario 2: Connection Pool Exhaustion
- **Input**: Spike in database connections from multiple tenants simultaneously
- **Expected**: Per-tenant connection limits enforced, pgBouncer multiplexes effectively
- **Fail condition**: Shared pool exhausted, all tenants get connection errors

### Scenario 3: CDN Cross-Tenant Cache
- **Input**: Tenant A and Tenant B request asset at same URL path
- **Expected**: Different cached responses (cache key includes tenant-id)
- **Fail condition**: Tenant A receives Tenant B's cached content

### Scenario 4: Scale-Down Without Impact
- **Input**: Traffic drops from 1500 to 200 req/sec
- **Expected**: Replicas scale down gracefully within 10 minutes, no dropped requests
- **Fail condition**: Requests fail during scale-down, or replicas remain over-provisioned
