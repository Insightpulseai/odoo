# Checklist: Multitenant Performance & Scaling

## Compute Scaling

- [ ] Auto-scaling rules defined (triggers, min/max replicas, cool-down)
- [ ] Scale triggers include per-tenant metrics (not just aggregate)
- [ ] Scale-up time meets SLO requirements (requests not dropped during scaling)
- [ ] Scale-down tested (graceful connection draining, no request failures)
- [ ] Minimum replica count covers baseline load
- [ ] Maximum replica count capped to control cost

## Database Scaling

- [ ] Connection pool sized per tenant tier
- [ ] Read replicas configured for read-heavy workloads
- [ ] Query performance optimized (indexes, query plans reviewed)
- [ ] Connection exhaustion prevention in place (per-tenant limits)
- [ ] Database scaling (vertical or horizontal) tested under load
- [ ] Backup/restore performance validated

## Storage Scaling

- [ ] Storage tier selected per tenant tier (hot, cool, archive)
- [ ] Auto-tiering policies configured based on access patterns
- [ ] Lifecycle management rules defined (move to cool after N days)
- [ ] Per-tenant storage quotas enforced
- [ ] Storage performance (IOPS, throughput) meets SLO

## CDN Configuration

- [ ] CDN cache key includes tenant-id (prevents cross-tenant cache hits)
- [ ] Cache purge strategy defined (per-tenant, per-asset, global)
- [ ] Custom domain support via CDN
- [ ] CDN origin failover configured
- [ ] CDN performance validated (cache hit ratio, latency)

## Load Testing

- [ ] Multi-tenant load test scenarios defined
- [ ] Realistic tenant distribution simulated (80/20 rule)
- [ ] Noisy neighbor scenario included
- [ ] Scaling event scenario included (scale-up and scale-down)
- [ ] Acceptance criteria tied to SLO targets
- [ ] Load test results documented and reviewed
