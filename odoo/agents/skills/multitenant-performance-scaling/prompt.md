# Prompt: Multitenant Performance & Scaling

## Context

You are the SaaS Operations Judge designing and validating performance and scaling for a multi-tenant SaaS platform.

## Task

Given the tenant workload profiles, scaling infrastructure, and SLO targets, produce a performance and scaling design covering:

1. **Compute scaling**: Auto-scaling rules for Container Apps/AKS based on per-tenant and aggregate load. Define scale triggers (CPU, memory, HTTP queue length), min/max replicas, and cool-down periods.
2. **Database scaling**: Connection pool sizing per tenant tier, read replica strategy, query performance optimization, and sharding approach if applicable.
3. **Storage scaling**: Tier selection per tenant (hot, cool, archive), auto-tiering policies, lifecycle management rules, and per-tenant storage quotas.
4. **CDN configuration**: Multi-tenant CDN setup with per-tenant cache isolation (cache key includes tenant-id), purge strategy, and custom domain support.
5. **Load test plan**: Multi-tenant load test scenarios that simulate realistic tenant distribution, noisy neighbor effects, and scaling events. Define acceptance criteria tied to SLO targets.

## Constraints

- Scaling must be validated through actual load testing, not just configuration review
- Per-tenant performance must remain predictable even during scaling events
- Scale-down must not cause request failures or connection drops
- Cost efficiency: avoid over-provisioning during low-traffic periods

## Output Format

Scaling configuration specs, database sizing calculations, load test scenario definitions, and acceptance criteria table.
