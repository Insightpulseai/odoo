# Prompt: Noisy Neighbor Mitigation

## Context

You are the Multitenancy Architect designing noisy neighbor mitigation for shared infrastructure in a multi-tenant SaaS platform.

## Task

Given the shared resources, tenant tiers, and SLO targets, produce a mitigation design covering:

1. **Rate limiting**: Per-tenant rate limits at the API gateway. Define limits per tier, burst allowance, and response when limits are exceeded (429 with Retry-After header).
2. **Resource quotas**: Per-tenant CPU, memory, and storage quotas. How quotas are enforced (hard cap vs soft cap with alerting).
3. **Queue isolation**: How message queues prevent one tenant's backlog from blocking others. Partitioning, priority queues, or dedicated queues per tier.
4. **Connection pooling**: Database connection pool sizing per tenant. How to prevent one tenant from exhausting the shared connection pool.
5. **Anomaly detection**: Baseline usage profiles per tenant, anomaly detection rules, automatic throttling triggers, and manual escalation thresholds.

## Constraints

- Mitigation must be transparent to well-behaved tenants
- Throttling response must include Retry-After header and clear error message
- Quotas must scale with tenant tier (enterprise gets more than free)
- False positive rate for anomaly detection must be below 1%

## Output Format

Resource-by-resource mitigation matrix with per-tier limits, plus anomaly detection rule definitions.
