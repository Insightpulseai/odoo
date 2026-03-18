# Checklist: Noisy Neighbor Mitigation

## Rate Limiting

- [ ] Per-tenant rate limits defined at API gateway
- [ ] Limits tiered by tenant tier (free < standard < enterprise)
- [ ] Burst allowance defined (e.g., 2x sustained rate for 30 seconds)
- [ ] 429 response includes Retry-After header
- [ ] Rate limit counters are per-tenant, not per-IP or per-user
- [ ] Rate limit dashboard available for monitoring

## Resource Quotas

- [ ] CPU quota per tenant defined and enforced
- [ ] Memory quota per tenant defined and enforced
- [ ] Storage quota per tenant defined and enforced
- [ ] Quota enforcement mechanism documented (hard cap vs soft cap)
- [ ] Quota alerts configured before hard limits are reached
- [ ] Quota increase process documented for tier upgrades

## Queue Isolation

- [ ] Queue partitioning strategy defined (per-tenant, per-tier, or priority)
- [ ] Dead letter queue configured for failed messages
- [ ] Queue depth monitoring per tenant
- [ ] Backpressure mechanism prevents queue overflow
- [ ] Priority processing for higher-tier tenants

## Connection Pooling

- [ ] Database connection pool sized per tenant tier
- [ ] Maximum connections per tenant enforced
- [ ] Connection timeout configured to prevent pool exhaustion
- [ ] Pool health monitoring enabled
- [ ] Failover behavior documented when pool is exhausted

## Anomaly Detection

- [ ] Baseline usage profile established per tenant
- [ ] Anomaly detection rules defined with thresholds
- [ ] Automatic throttling triggered on confirmed anomaly
- [ ] Manual escalation path for ambiguous anomalies
- [ ] False positive rate monitored and tuned
