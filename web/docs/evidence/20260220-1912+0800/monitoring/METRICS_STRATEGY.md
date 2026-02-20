# Odoo.sh Platform Metrics Strategy

**Timestamp**: 2026-02-20 19:30+0800
**Project**: Odoo.sh CI/CD Platform Observability
**Supabase**: spdtwktxdalcfigzeqrz

---

## Overview

Supabase Metrics API provides 200+ Prometheus-compatible PostgreSQL metrics for monitoring the ops.* CI/CD state tables (builds, deployments, build_logs).

**Metrics Endpoint**: `https://spdtwktxdalcfigzeqrz.supabase.co/customer/v1/privileged/metrics`

**Authentication**:
- Username: `service_role`
- Password: `SUPABASE_SERVICE_ROLE_KEY` (from Vault/env)

---

## Key Metrics for Odoo.sh Platform

### Build Performance Metrics

**Query Performance**:
- `pg_stat_statements` - Track slow queries on ops.builds table
- Build lookup latency (by git_sha, branch_name indexes)
- Test result JSON parsing performance

**Table Statistics**:
- ops.builds row count growth rate
- ops.deployments table size and bloat
- ops.build_logs write throughput (high insert rate)

**Connection Pool**:
- Active connections during build spikes
- Connection pool saturation alerts
- Idle connections cleanup

### Database Health Metrics

**Resource Utilization**:
- CPU usage during build creation/update operations
- IO patterns for ops.* table inserts/updates
- WAL (Write-Ahead Log) generation rate

**Index Performance**:
- Index hit ratio for ops.builds (project_branch, status, pr, created indexes)
- Sequential scan detection on filtered queries
- Index regression alerts

**RLS Policy Overhead**:
- RLS policy evaluation time for service_role vs authenticated user access
- Policy cache hit rates

---

## Integration with Agent Skills

### odoo-sh-github-integration Skill

**Monitored Operations**:
- Step 1: Build record creation latency → `ops.builds INSERT` metric
- Step 9: Build status update performance → `ops.builds UPDATE` metric
- Step 10: Deployment record creation → `ops.deployments INSERT` metric

**Alert Thresholds**:
- Build creation >500ms → Investigate connection pool
- Build log writes >1000/sec → Check WAL performance
- Deployment query >200ms → Index regression alert

### odoo-sh-environment-manager Skill

**Monitored Operations**:
- CREATE: ops.environments table performance
- PROMOTE: Bulk deployment record creation during blue-green swap
- CLONE_DATA: Database copy operation metrics (not Supabase-specific)
- DELETE: Cleanup operation efficiency

**Alert Thresholds**:
- Environment creation >1s → Connection pool saturation
- Promotion deployment creation >2s → Bulk insert optimization needed

### platform-engineer Persona

**Dashboard Requirements**:
- Real-time build pipeline health (success/failure rates)
- Average build duration trends
- Deployment frequency by environment
- Database resource utilization during peak CI/CD activity

---

## Observability Stack Options

### Option A: Grafana Cloud (Recommended for MVP)

**Pros**:
- Pre-built Supabase dashboards (200+ charts)
- Free tier: 10K metrics, 50GB logs, 14-day retention
- Managed service, no infrastructure

**Setup**:
1. Create Grafana Cloud account
2. Add Prometheus data source with Supabase metrics endpoint
3. Import Supabase Grafana repository dashboards
4. Customize for ops.* table-specific metrics

**Cost**: Free tier → $8/month after limits

### Option B: Self-Hosted Prometheus + Grafana

**Pros**:
- Full control over data retention
- No vendor lock-in
- Cost-effective for long-term storage

**Cons**:
- Requires infrastructure management (DigitalOcean droplet)
- Maintenance overhead

**Setup**:
1. Deploy Prometheus + Grafana on DigitalOcean droplet
2. Configure Prometheus scrape for Supabase metrics endpoint
3. Build custom Grafana dashboards for Odoo.sh platform

**Cost**: $6/month droplet + storage

### Option C: Datadog (Enterprise Option)

**Pros**:
- APM integration with Next.js frontend
- Log aggregation + metrics + tracing
- Advanced alerting and anomaly detection

**Cons**:
- Expensive ($15/host/month + usage)
- Overkill for current scale

---

## Metrics Collection Workflow

### 1. Enable Metrics Access

```bash
# Test metrics endpoint (requires service_role key)
curl -u "service_role:${SUPABASE_SERVICE_ROLE_KEY}" \
  "https://spdtwktxdalcfigzeqrz.supabase.co/customer/v1/privileged/metrics" \
  | head -20
```

**Expected Output**:
```
# HELP pg_stat_database_blks_hit Number of times disk blocks were found in buffer cache
# TYPE pg_stat_database_blks_hit counter
pg_stat_database_blks_hit{datname="postgres"} 1234567
...
```

### 2. Configure Prometheus (if self-hosted)

**prometheus.yml**:
```yaml
scrape_configs:
  - job_name: 'supabase-odoosh'
    metrics_path: '/customer/v1/privileged/metrics'
    scheme: https
    basic_auth:
      username: 'service_role'
      password: '${SUPABASE_SERVICE_ROLE_KEY}'
    static_configs:
      - targets: ['spdtwktxdalcfigzeqrz.supabase.co']
    scrape_interval: 30s
```

### 3. Create Custom Metrics (Application-Level)

**Supabase Edge Function**: `ops-metrics-aggregator`

```typescript
// Example: Calculate build success rate over last 24h
const buildMetrics = await supabase
  .from('ops.builds')
  .select('status, created_at')
  .gte('created_at', new Date(Date.now() - 24*60*60*1000).toISOString());

const successRate = buildMetrics.data.filter(b => b.status === 'success').length
  / buildMetrics.data.length;

// Export as Prometheus metric
return new Response(`# HELP odoosh_build_success_rate Build success rate (24h)
# TYPE odoosh_build_success_rate gauge
odoosh_build_success_rate ${successRate}
`, { headers: { 'Content-Type': 'text/plain' } });
```

**Scrape**: Add to Prometheus config for application-level metrics

---

## Alert Configuration

### Critical Alerts

**Build Pipeline Failures** (PagerDuty/Slack):
- Build failure rate >10% over 1 hour
- No successful builds in 2 hours
- Database connection pool exhaustion

**Database Health** (Email):
- CPU >80% for 5 minutes
- Disk I/O saturation
- Index hit ratio <95%

**Performance Degradation** (Slack):
- Build creation latency >1s (P95)
- Deployment query time >500ms (P95)
- RLS policy evaluation >100ms

### Warning Alerts

**Capacity Planning**:
- ops.builds table >100K rows (consider partitioning)
- ops.build_logs table size >1GB (archive old logs)
- Connection count >50% of pool limit

**Query Optimization**:
- Sequential scans detected on ops.builds
- Missing index usage on filtered queries
- Slow query log threshold exceeded

---

## Grafana Dashboard Panels

### Panel 1: Build Pipeline Health

**Metric**: `odoosh_build_success_rate`
**Visualization**: Single Stat + Sparkline
**Threshold**: <90% = Warning, <80% = Critical

### Panel 2: Build Duration Trends

**Query**:
```sql
SELECT
  DATE_TRUNC('hour', created_at) as time,
  AVG(EXTRACT(epoch FROM (completed_at - created_at))) as avg_duration_sec
FROM ops.builds
WHERE completed_at IS NOT NULL
  AND created_at > NOW() - INTERVAL '7 days'
GROUP BY time
ORDER BY time;
```

**Visualization**: Time Series Line Chart

### Panel 3: Deployment Frequency

**Query**:
```sql
SELECT
  DATE_TRUNC('day', deployed_at) as time,
  environment_id,
  COUNT(*) as deployment_count
FROM ops.deployments
WHERE deployed_at > NOW() - INTERVAL '30 days'
GROUP BY time, environment_id
ORDER BY time;
```

**Visualization**: Stacked Bar Chart (by environment)

### Panel 4: Database Resource Utilization

**Metrics**:
- `pg_stat_database_blks_hit` (buffer cache hits)
- `pg_stat_database_tup_inserted` (ops.* insert rate)
- `pg_stat_activity{state="active"}` (active queries)

**Visualization**: Multi-axis Time Series

### Panel 5: Top Slow Queries

**Query** (via pg_stat_statements extension):
```sql
SELECT
  query,
  mean_exec_time,
  calls
FROM pg_stat_statements
WHERE query LIKE '%ops.builds%' OR query LIKE '%ops.deployments%'
ORDER BY mean_exec_time DESC
LIMIT 10;
```

**Visualization**: Table with conditional formatting

---

## Implementation Roadmap

### Phase 1: MVP Monitoring (Week 1)

**Goal**: Basic visibility into build pipeline health

**Tasks**:
1. ✅ Enable Supabase Metrics API access
2. Set up Grafana Cloud free tier
3. Import Supabase pre-built dashboards
4. Create 3 custom panels: Build success rate, duration trends, deployment frequency
5. Configure Slack alerts for critical failures

**Deliverables**:
- Grafana Cloud workspace URL
- 5-panel Odoo.sh platform dashboard
- Slack webhook integration

### Phase 2: Advanced Metrics (Week 2-3)

**Goal**: Application-level metrics and query performance tracking

**Tasks**:
1. Deploy `ops-metrics-aggregator` Edge Function
2. Enable pg_stat_statements extension in Supabase
3. Create slow query dashboard panel
4. Add capacity planning alerts (table size, connection pool)
5. Document runbook for common alerts

**Deliverables**:
- Application metrics endpoint
- Slow query monitoring
- Alert runbook in `docs/ops/`

### Phase 3: Cost Optimization (Month 2)

**Goal**: Right-size infrastructure based on metrics

**Tasks**:
1. Analyze database resource utilization patterns
2. Identify index optimization opportunities
3. Archive old build logs (>90 days)
4. Implement table partitioning for ops.builds if needed
5. Evaluate self-hosted Prometheus migration

**Deliverables**:
- Infrastructure sizing recommendations
- Query optimization report
- Cost comparison: Grafana Cloud vs self-hosted

---

## Integration with Agent Teams

### Backend Engineer + Platform Engineer Collaboration

**Workflow**:
1. **Backend Engineer**: Creates RLS policies, indexes for ops.* tables
2. **Platform Engineer**: Monitors query performance via Grafana
3. **Feedback Loop**: Platform engineer identifies slow queries → Backend engineer optimizes

**Shared Dashboard**: Both agents access same Grafana workspace

### DevOps Engineer Role

**Responsibilities**:
- Maintain Prometheus/Grafana infrastructure (if self-hosted)
- Configure alert routing (Slack, PagerDuty)
- Manage metrics retention policies
- Cost monitoring and optimization

---

## Security Considerations

**Service Role Key Protection**:
- Never commit `SUPABASE_SERVICE_ROLE_KEY` to Git
- Store in Supabase Vault for CI/CD access
- Rotate quarterly or after suspected compromise

**Metrics Endpoint Access**:
- HTTP Basic Auth required (service_role user)
- No anonymous access
- Monitor failed auth attempts in Supabase logs

**Data Exposure**:
- Metrics endpoint exposes database statistics (not user data)
- Safe to aggregate in third-party observability platforms
- No PII or sensitive business logic in metrics

---

## Verification Commands

```bash
# Test metrics endpoint
curl -u "service_role:${SUPABASE_SERVICE_ROLE_KEY}" \
  "https://spdtwktxdalcfigzeqrz.supabase.co/customer/v1/privileged/metrics" \
  | grep "pg_stat_database"

# Query build success rate (via psql)
psql "$POSTGRES_URL" -c "
  SELECT
    status,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
  FROM ops.builds
  WHERE created_at > NOW() - INTERVAL '24 hours'
  GROUP BY status;
"

# Check ops.builds table size
psql "$POSTGRES_URL" -c "
  SELECT
    pg_size_pretty(pg_total_relation_size('ops.builds')) as total_size,
    pg_size_pretty(pg_relation_size('ops.builds')) as table_size,
    pg_size_pretty(pg_indexes_size('ops.builds')) as indexes_size;
"
```

---

## Next Steps

### Immediate (After Vercel Integration)

1. **Enable Metrics Access**: Test `curl` command above with service_role key
2. **Create Grafana Cloud Account**: Sign up at grafana.com
3. **Import Pre-Built Dashboard**: Use Supabase Grafana repository
4. **Add Custom Panel**: Build success rate over 24h

### Short-Term (Week 1-2)

1. **Configure Slack Alerts**: Critical build failures + database health
2. **Deploy Metrics Aggregator**: Edge Function for application-level metrics
3. **Document Alert Runbook**: Common failure scenarios and remediation

### Long-Term (Month 1-2)

1. **Evaluate Self-Hosted**: Cost comparison with Grafana Cloud
2. **Optimize Queries**: Use slow query dashboard to identify bottlenecks
3. **Capacity Planning**: Analyze growth trends and scale proactively

---

**Status**: READY FOR IMPLEMENTATION
**Dependencies**: Vercel integration complete, ops.* tables deployed
**Owner**: Platform Engineer (persona) + DevOps Engineer (infrastructure)
