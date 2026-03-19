# Examples — caf-operations-management

## Example 1: Management baseline establishment

**Input**: Establish operations management baseline for ACA-based platform.

**Output**:
- Maturity: Below baseline (monitoring exists but incomplete)
- Inventory:
  - 11 Container Apps: all discovered via Resource Graph
  - 2 PostgreSQL servers: `ipai-odoo-dev-pg`, `pg-ipai-dev`
  - 3 Container Registries: `cripaidev`, `ipaiodoodevacr`, `ipaiwebacr`
  - 1 Front Door: `ipai-fd-dev`
  - 3 Key Vaults: `kv-ipai-dev`, `kv-ipai-staging`, `kv-ipai-prod`
- Visibility gaps:
  - Application Insights enabled on 6/11 Container Apps — 5 missing
  - No structured logging on n8n, Keycloak, Plane
  - No distributed tracing configured
  - Alert rules: 2 configured (ACA health), 8 recommended missing
- Compliance:
  - PostgreSQL backup: enabled (7-day retention) — PASS
  - ACA image updates: manual — needs automation
  - Key Vault key rotation: no policy — FAIL
- Roadmap:
  1. (Week 1) Enable Application Insights on remaining 5 Container Apps
  2. (Week 1) Create alert rules for availability and error rate per service
  3. (Week 2) Configure Slack notification for critical alerts
  4. (Week 3) Define SLA/SLO targets per workload
  5. (Week 4) Set up automated backup restore testing

## Example 2: SLA/SLO definition

**Input**: Define SLA/SLO targets for platform services.

**Output**:
- SLO definitions:
  - Odoo ERP (`ipai-odoo-dev-web`): 99.9% availability, p95 latency < 2s, error rate < 1%
  - n8n automation: 99.5% availability (non-user-facing), workflow success rate > 95%
  - Front Door edge: 99.99% availability (Azure SLA)
  - PostgreSQL: 99.99% availability (Azure Flex Server SLA)
- Measurement:
  - Availability: health probe success rate over 30-day window
  - Latency: Application Insights request duration percentiles
  - Error rate: 5xx responses / total responses
- Error budget: Odoo 99.9% = 43.2 minutes/month downtime budget
- Alerting:
  - Burn rate alert at 2x (consuming error budget twice as fast as sustainable)
  - Exhaustion alert at 80% budget consumed
- Review cadence: Monthly operational fitness review

## Example 3: Incident postmortem operations improvement

**Input**: PostgreSQL connection pool exhaustion caused 15-minute Odoo outage.

**Output**:
- Incident: Odoo 503 errors for 15 minutes due to PG connection pool exhaustion
- Root cause: n8n workflow triggered 200 concurrent queries, exhausting PgBouncer pool
- Operations gaps identified:
  - No connection pool monitoring alert — FAIL
  - No query rate limiting on n8n database access — FAIL
  - No runbook for connection pool exhaustion — FAIL
- Improvements:
  1. Add alert: PgBouncer active connections > 80% capacity
  2. Add alert: n8n workflow query rate > 50/second
  3. Create runbook: connection pool exhaustion (identify source, kill idle connections, restart if needed)
  4. Implement: n8n database connection limit (max 20 concurrent)
- SLO impact: 15 minutes consumed from 43.2 minute monthly error budget (35%)
- Status: 3 action items created in Azure DevOps backlog
