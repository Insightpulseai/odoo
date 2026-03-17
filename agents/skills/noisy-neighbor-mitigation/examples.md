# Examples: Noisy Neighbor Mitigation

## Example 1: Rate Limiting Matrix

| Tier | API calls/min | Burst (30s) | Concurrent requests | Response on exceed |
|------|--------------|-------------|--------------------|--------------------|
| Free | 60 | 120 | 5 | 429 + Retry-After: 60 |
| Standard | 600 | 1200 | 25 | 429 + Retry-After: 30 |
| Enterprise | 6000 | 12000 | 100 | 429 + Retry-After: 10 |

**Implementation**: Azure API Management (APIM) rate-limit-by-key policy with tenant-id as key.

```xml
<rate-limit-by-key calls="600" renewal-period="60"
  counter-key="@(context.Request.Headers.GetValueOrDefault("X-Tenant-Id"))" />
```

---

## Example 2: Database Connection Pool Isolation

**Pool configuration**:

| Tier | Max connections | Idle timeout | Queue wait |
|------|----------------|-------------|------------|
| Free | 2 | 30s | 5s |
| Standard | 10 | 60s | 10s |
| Enterprise | 50 | 120s | 30s |

**Implementation**: Application-level connection pool per tenant using pgBouncer with tenant-scoped pools, or application code with tenant-keyed pool map.

```python
class TenantConnectionPool:
    def __init__(self):
        self._pools = {}

    def get_connection(self, tenant_id, tier):
        if tenant_id not in self._pools:
            max_conn = {"free": 2, "standard": 10, "enterprise": 50}[tier]
            self._pools[tenant_id] = create_pool(max_size=max_conn)
        return self._pools[tenant_id].acquire()
```

---

## Example 3: Anomaly Detection Rules

| Metric | Baseline (p95) | Warning threshold | Throttle threshold | Action |
|--------|----------------|-------------------|-------------------|--------|
| API calls/min | 100 | 3x baseline (300) | 5x baseline (500) | Warning: alert. Throttle: rate limit to baseline. |
| DB queries/min | 200 | 3x baseline (600) | 5x baseline (1000) | Warning: alert. Throttle: connection limit reduced. |
| Storage writes/hr | 50MB | 3x baseline (150MB) | 5x baseline (250MB) | Warning: alert. Throttle: write rate limited. |

**Implementation**: Azure Monitor alert rules with dynamic thresholds, feeding into an Azure Function that adjusts APIM rate limits via management API.
