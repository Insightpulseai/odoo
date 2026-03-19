# Examples — odoo-monitoring-posture

## Example 1: Healthy monitoring posture

**Input**: Pre-deployment monitoring readiness check

**Output**:
- Monitor workspace: configured, collecting data — PASS
- Application Insights: connected to all 3 Container Apps — PASS
- Health probes: web (200), worker (200), cron (200) — PASS
- Alert rules:
  - Error rate > 5%: configured, action group `ag-ipai-ops` — PASS
  - p95 latency > 2000ms: configured, action group `ag-ipai-ops` — PASS
  - Availability < 99.5%: configured, action group `ag-ipai-ops` — PASS
  - Container restarts > 3/hour: configured — PASS
- Notifications: email to ops team + Slack webhook — PASS
- Log retention: 90 days (policy minimum: 30) — PASS
- Dashboard: `Odoo Platform KPIs` workbook exists — PASS
- Blockers: none
- Evidence: `az monitor metrics list --resource <app-id> --metric HttpResponseCode`

## Example 2: Missing alert rules

**Input**: New Container App `ipai-shelf-dev` provisioned without monitoring setup

**Output**:
- Application Insights: NOT connected to `ipai-shelf-dev` — FAIL
- Health probes: not configured — FAIL
- Alert rules: none for `ipai-shelf-dev` — FAIL
- Blockers: [App Insights not connected, health probe missing, no alert rules]
- Recommendation: Connect App Insights, configure `/health` probe, add to alert action group
