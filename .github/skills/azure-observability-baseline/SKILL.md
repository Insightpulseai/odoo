# azure-observability-baseline

**Impact tier**: P1 -- Operational Readiness

## Purpose

Close the observability gap where the Odoo runtime lacks Azure-native monitoring.
The benchmark audit found: no Application Insights instrumentation, no Log
Analytics workspace, no Azure Monitor alert rules, and residual Docker/Prometheus
assumptions in documentation that do not apply to the ACA runtime.

## When to Use

- Instrumenting Odoo on Azure Container Apps for the first time.
- Replacing Docker-centric monitoring (Prometheus, cAdvisor) with Azure-native stack.
- Setting up alert rules for Odoo health, PG health, and ACA scaling events.
- Preparing for go-live observability readiness.

## Required Evidence (inspect these repo paths first)

| Path | What to look for |
|------|-----------------|
| `infra/azure/modules/app-insights.bicep` | App Insights resource, connection string output |
| `infra/azure/odoo-runtime.bicep` | ACA env diagnostic settings, App Insights binding |
| `infra/azure/main.bicep` | Log Analytics workspace, module wiring |
| `infra/ssot/azure/resources.yaml` | Log Analytics, App Insights entries |
| `docs/runbooks/ODOO18_GO_LIVE_CHECKLIST.md` | Monitoring/alerting line items |
| `docs/audits/ODOO_AZURE_ENTERPRISE_BENCHMARK.md` | Observability gap row |

## Microsoft Learn MCP Usage

Run at least these three queries:

1. `microsoft_docs_search("Azure Container Apps Application Insights monitoring")`
   -- retrieves how to bind App Insights to ACA environment.
2. `microsoft_docs_search("Azure Monitor alert rules container apps CPU memory")`
   -- retrieves alert rule configuration for ACA metrics.
3. `microsoft_docs_search("Azure Log Analytics workspace diagnostic settings PostgreSQL")`
   -- retrieves how to route PG Flexible Server logs to Log Analytics.

Optional:

4. `microsoft_code_sample_search("bicep application insights log analytics workspace", language="bicep")`
5. `microsoft_docs_fetch("https://learn.microsoft.com/en-us/azure/container-apps/observability")`

## Workflow

1. **Inspect repo** -- Read Bicep modules for existing App Insights and Log
   Analytics resources. Check if ACA environment has `appInsightsConfiguration`.
   Search for any Prometheus/Docker monitoring references to remove.
2. **Query MCP** -- Run the three searches. Capture App Insights connection
   string binding for ACA, alert rule metric names, PG diagnostic categories.
3. **Compare** -- Identify: (a) Does a Log Analytics workspace exist in Bicep?
   (b) Is App Insights connected to ACA? (c) Are alert rules defined? (d) Are
   there stale Prometheus references?
4. **Patch** -- Update Bicep:
   - Create Log Analytics workspace if missing.
   - Create App Insights connected to that workspace.
   - Bind App Insights to ACA environment via `appInsightsConfiguration`.
   - Add diagnostic settings for PG Flexible Server.
   - Add alert rules: ACA CPU > 80%, ACA memory > 80%, PG connections > 80%,
     Odoo health check failure.
   - Remove Docker/Prometheus monitoring references from docs.
5. **Verify** -- Bicep lints clean. SSOT updated. Go-live checklist has
   monitoring items. No Prometheus/Docker monitoring references remain.

## Outputs

| File | Change |
|------|--------|
| `infra/azure/modules/app-insights.bicep` | App Insights + Log Analytics |
| `infra/azure/odoo-runtime.bicep` | ACA App Insights binding |
| `infra/azure/modules/postgres-flexible.bicep` | Diagnostic settings |
| `infra/azure/modules/alerts.bicep` | Alert rules (new file) |
| `infra/ssot/azure/resources.yaml` | Log Analytics, App Insights entries |
| `docs/runbooks/ODOO18_GO_LIVE_CHECKLIST.md` | Monitoring verification steps |
| `docs/evidence/<stamp>/azure-observability-baseline/` | Bicep diffs, MCP excerpts |

## Completion Criteria

- [ ] Log Analytics workspace exists in Bicep with 30-day retention minimum.
- [ ] Application Insights is created and connected to Log Analytics.
- [ ] ACA environment has `appInsightsConfiguration.connectionString` set.
- [ ] PG Flexible Server has diagnostic settings routing to Log Analytics.
- [ ] At least 4 alert rules defined (CPU, memory, PG connections, health check).
- [ ] No Prometheus, Grafana, or cAdvisor references remain in `docs/runbooks/`.
- [ ] Evidence directory contains Bicep diffs and MCP query excerpts.
