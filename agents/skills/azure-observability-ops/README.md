# azure-observability-ops

Validates monitoring and observability posture — Application Insights, Log Analytics, alert rules, and KQL query catalog.

## When to use
- New service deployed to production
- Observability configuration changes in a PR
- Incident postmortem requires telemetry review
- KQL query catalog is updated

## Key rule
No production service may operate without Application Insights instrumentation and at least one alert rule
covering 5xx errors. Services missing telemetry are blockers. Never disable existing alerts.

## Cross-references
- `docs/contracts/azure-resource-graph-contract.md`
- `ssot/runtime/resource-graph-query-catalog.yaml`
