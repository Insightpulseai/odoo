# Examples: Multitenant Performance & Scaling

## Example 1: Container Apps Auto-Scaling Configuration

```yaml
# Azure Container Apps scaling rules
scale:
  minReplicas: 2
  maxReplicas: 20
  rules:
    - name: http-scaling
      http:
        metadata:
          concurrentRequests: "50"  # Scale when > 50 concurrent requests per replica
    - name: cpu-scaling
      custom:
        metadata:
          type: Utilization
          value: "70"  # Scale when CPU > 70%
    - name: queue-scaling
      azure-queue:
        metadata:
          queueName: tenant-tasks
          queueLength: "10"  # Scale when > 10 messages per replica
```

**Cool-down**: 300 seconds (5 min) to prevent flapping during traffic spikes.

---

## Example 2: Database Connection Pool Sizing

**Calculation for shared PostgreSQL** (max_connections = 200):

| Tier | Tenants | Conn/Tenant | Total | % of Pool |
|------|---------|-------------|-------|-----------|
| Free | 100 | 1 | 100 | 50% |
| Standard | 40 | 3 | 120 | 60% |
| Enterprise | 5 | 10 | 50 | 25% |
| Platform | 1 | 10 | 10 | 5% |
| **Reserve** | - | - | **20** | **10%** |

**Issue**: Total (280) exceeds pool (200). **Solution**: Use pgBouncer with transaction-level pooling. Each tenant gets a virtual pool; pgBouncer multiplexes actual connections.

```
Actual PG connections: 50 (pgBouncer pool)
Virtual connections:   280 (application-level per-tenant pools)
Multiplexing ratio:    5.6x
```

---

## Example 3: Load Test Scenarios

**Scenario 1: Steady state**
- 100 free tenants (1 req/sec each)
- 40 standard tenants (10 req/sec each)
- 5 enterprise tenants (50 req/sec each)
- Total: 750 req/sec sustained for 30 minutes
- Acceptance: p95 latency < 200ms, error rate < 0.1%

**Scenario 2: Noisy neighbor**
- Same as Scenario 1, plus one standard tenant bursting to 100 req/sec
- Acceptance: Other tenants' p95 latency increases < 20%, noisy tenant rate-limited

**Scenario 3: Scale event**
- Start at 200 req/sec, ramp to 1500 req/sec over 5 minutes
- Acceptance: No requests dropped during scale-up, p95 latency < 500ms during scaling, stabilizes to < 200ms after scaling

**Scenario 4: Scale down**
- Start at 1500 req/sec, drop to 200 req/sec instantly
- Acceptance: No connection drops, scale-down within 10 minutes, no orphaned replicas

---

## Example 4: CDN Cache Key Strategy

**Cache key pattern**: `{tenant-id}:{asset-path}:{content-hash}`

```
# Tenant A requesting logo.png
Cache key: tenant-abc:assets/logo.png:sha256-xyz

# Tenant B requesting logo.png (different file)
Cache key: tenant-def:assets/logo.png:sha256-uvw
```

**Result**: Tenant A never receives Tenant B's cached assets, even for same path.
