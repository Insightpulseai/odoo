# Examples: Tenant Health & Alerting

## Example 1: Metrics Definition Table

| Metric | Type | Dimensions | Unit | Source |
|--------|------|-----------|------|--------|
| `tenant.request.count` | Counter | tenant_id, method, status_code | count | API Gateway |
| `tenant.request.duration` | Histogram | tenant_id, method, endpoint | ms | API Gateway |
| `tenant.error.count` | Counter | tenant_id, error_type | count | Application |
| `tenant.db.query.duration` | Histogram | tenant_id, query_type | ms | Database |
| `tenant.storage.usage` | Gauge | tenant_id | bytes | Storage |
| `tenant.active.users` | Gauge | tenant_id | count | Auth service |

---

## Example 2: SLO Burn Rate Alert

**SLO**: 99.9% availability (43.2 min downtime budget per 30-day window).

**Fast burn alert** (14.4x burn rate):
```
# Consumes 10% of budget in 1 hour
# Threshold: error_rate > 1.44% over 5-minute window
alert: TenantSLOFastBurn
expr: tenant_error_rate{tier="enterprise"} > 0.0144
for: 5m
labels:
  severity: critical
annotations:
  summary: "Tenant {{ $labels.tenant_id }} fast-burning SLO budget"
```

**Slow burn alert** (3x burn rate):
```
# Consumes 50% of budget in 1 week
# Threshold: error_rate > 0.3% over 1-hour window
alert: TenantSLOSlowBurn
expr: tenant_error_rate{tier="enterprise"} > 0.003
for: 1h
labels:
  severity: warning
```

---

## Example 3: Alert Routing by Tier

| Tier | Critical | Warning | Info |
|------|----------|---------|------|
| Free | Email (batch, daily) | No alert | No alert |
| Standard | Email (immediate) | Email (batch) | Dashboard only |
| Enterprise | PagerDuty + Slack + Email | Email (immediate) | Dashboard + email |

**Deduplication**: Group alerts by tenant_id + alert_name. Suppress duplicate alerts for 15 minutes.

---

## Example 4: Per-Tenant Dashboard Layout

**Sections**:
1. **Health summary**: RAG status for availability, latency, error rate
2. **SLO status**: Current error budget remaining, burn rate trend
3. **Traffic overview**: Request count, throughput, top endpoints
4. **Error breakdown**: Error types, top failing endpoints, error timeline
5. **Resource usage**: Storage, compute, database connections
6. **Active users**: Current active users, login history
