# Examples — azure-observability-ops

## Example 1: Fully instrumented Odoo service

**Input**: Validate observability for `ipai-odoo-dev-web`

**Output**:
- Service: `ipai-odoo-dev-web` (Microsoft.App/containerApps)
- App Insights: connected — `applicationinsights-ipai-dev` — PASS
- Log Analytics: receiving data — last ingestion 12 minutes ago — PASS
- Alert rules:
  - HTTP 5xx rate > 5%: active — PASS
  - P95 latency > 2s: active — PASS
  - Container restart > 3: active — PASS
- KQL validation: q01 (container logs) — PASS, q14 (request latency) — PASS
- Retention: 90 days configured (minimum 30) — PASS
- Blockers: none
- Evidence: `az monitor app-insights component show --app applicationinsights-ipai-dev`

## Example 2: Service missing alert rules

**Input**: Validate observability for `ipai-shelf-dev`

**Output**:
- Service: `ipai-shelf-dev` (Microsoft.App/containerApps)
- App Insights: connected — PASS
- Log Analytics: receiving data — PASS
- Alert rules:
  - HTTP 5xx rate > 5%: MISSING — FAIL
  - P95 latency > 2s: MISSING — FAIL
  - Container restart > 3: active — PASS
- Blockers: [2 alert rules missing for 5xx and latency]
- Recommendation: Create alert rules for HTTP 5xx rate and P95 latency using platform template

## Example 3: Service without App Insights

**Input**: Validate observability for newly deployed `ipai-docs-dev`

**Output**:
- Service: `ipai-docs-dev` (Microsoft.App/containerApps)
- App Insights: NOT CONNECTED — FAIL (BLOCKER)
- Log Analytics: no data — FAIL
- Alert rules: none — FAIL
- Blockers: [App Insights not connected — hard blocker for production readiness]
- Recommendation: Connect App Insights via Bicep `Microsoft.Insights/components` and inject connection string via Key Vault
