# Examples: SaaS Observability Design

## Example 1: Tenant-Enriched Application Insights

**Scenario**: Odoo CE multi-tenant platform with Application Insights.

**Tenant context middleware** (Python):
```python
class TenantTelemetryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tenant_id = request.tenant_id  # resolved from token or session
        # Enrich all telemetry with tenant context
        from opencensus.ext.azure.trace_exporter import AzureExporter
        tracer = get_tracer()
        tracer.span.add_attribute("tenant_id", tenant_id)
        tracer.span.add_attribute("tenant_tier", request.tenant_tier)

        response = self.get_response(request)
        return response
```

**Custom metrics**:
| Metric | Type | Dimensions | Description |
|--------|------|-----------|-------------|
| `odoo.request.duration` | Histogram | tenant_id, endpoint, method | Request latency |
| `odoo.request.count` | Counter | tenant_id, endpoint, status_code | Request count |
| `odoo.active_sessions` | Gauge | tenant_id | Active user sessions |
| `odoo.db.query_duration` | Histogram | tenant_id, query_type | Database query latency |

---

## Example 2: KQL Queries for Per-Tenant Analysis

**Scenario**: Investigating slow performance for a specific tenant.

**Per-tenant latency**:
```kql
requests
| where customDimensions.tenant_id == "acme-corp"
| where timestamp > ago(1h)
| summarize
    p50 = percentile(duration, 50),
    p95 = percentile(duration, 95),
    p99 = percentile(duration, 99),
    count = count()
  by bin(timestamp, 5m)
| render timechart
```

**Tenant comparison (noisy neighbor detection)**:
```kql
requests
| where timestamp > ago(1h)
| summarize
    avg_duration = avg(duration),
    request_count = count(),
    error_rate = countif(success == false) * 100.0 / count()
  by tenant_id = tostring(customDimensions.tenant_id)
| order by request_count desc
| take 20
```

**SLA compliance report**:
```kql
let sla_target = 99.9;
requests
| where timestamp > ago(30d)
| summarize
    total = count(),
    successful = countif(resultCode startswith "2" or resultCode startswith "3"),
    availability = round(countif(resultCode startswith "2" or resultCode startswith "3") * 100.0 / count(), 2)
  by tenant_id = tostring(customDimensions.tenant_id)
| extend sla_met = availability >= sla_target
| order by availability asc
```

---

## Example 3: SLA Dashboard Definition

**Scenario**: Azure Dashboard for per-tenant SLA tracking.

**Dashboard tiles**:
1. **Platform Overview**: Total tenants, active/suspended, overall availability
2. **SLA Heatmap**: Tenant grid colored by SLA compliance (green >= 99.9%, yellow >= 99%, red < 99%)
3. **Top 10 Slowest Tenants**: p95 latency ranked
4. **Error Rate by Tenant**: Error rate trend per tenant over 24h
5. **Resource Consumption**: CPU/memory per stamp with tenant breakdown

**Alert rules**:
```yaml
alerts:
  - name: "Tenant SLA Breach"
    condition: "availability < 99.9% over 1h window"
    severity: 2
    action_group: "platform-oncall"
    suppress_window: "15m"

  - name: "Tenant Latency Spike"
    condition: "p95_latency > 5s for 5 consecutive minutes"
    severity: 3
    action_group: "platform-oncall"

  - name: "Tenant Error Rate Spike"
    condition: "error_rate > 5% over 10m window"
    severity: 2
    action_group: "platform-oncall"
```
