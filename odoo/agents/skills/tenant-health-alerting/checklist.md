# Checklist: Tenant Health & Alerting

## Metrics

- [ ] Custom metrics defined with tenant-id dimension
- [ ] Availability metric per tenant (successful requests / total requests)
- [ ] Latency metric per tenant (p50, p95, p99)
- [ ] Error rate metric per tenant (errors / total requests)
- [ ] Throughput metric per tenant (requests per second)
- [ ] Metrics cardinality managed (dimension count controlled)

## SLO Tracking

- [ ] SLO targets defined per tenant tier
- [ ] Error budget calculated per tenant
- [ ] Fast-burn alert configured (e.g., 10% budget consumed in 1 hour)
- [ ] Slow-burn alert configured (e.g., 50% budget consumed in 1 week)
- [ ] SLO dashboard shows current burn rate and remaining budget

## Alert Rules

- [ ] Alert severity levels defined (critical, warning, info)
- [ ] Alert routing respects tenant tier (enterprise: page, standard: email)
- [ ] Alert deduplication prevents alert storms
- [ ] Alert suppression configured for maintenance windows
- [ ] Alert escalation path defined for unacknowledged alerts

## Dashboards

- [ ] Platform overview dashboard shows all-tenant health summary
- [ ] Per-tenant dashboard shows detailed metrics for one tenant
- [ ] Dashboard access controls enforce tenant isolation
- [ ] Dashboard refresh rate appropriate (real-time for critical, 5-min for overview)
- [ ] Key metrics highlighted with RAG (red/amber/green) status

## Anomaly Detection

- [ ] Per-tenant usage baseline established (7-day rolling average)
- [ ] Anomaly detection rules configured (deviation > 3x baseline)
- [ ] Investigation playbook documented for flagged anomalies
- [ ] Auto-remediation actions defined for known anomaly patterns
- [ ] False positive feedback loop to tune detection rules
