# odoo-monitoring-posture

Validates monitoring and observability posture on Azure — Azure Monitor, Application Insights, health probes, alerting, and KPI dashboards.

## When to use
- Pre-deployment monitoring readiness check
- Periodic monitoring posture audit
- Incident response monitoring verification
- New Container App provisioned

## Key rule
Never disable monitoring or alerting. Never reduce log retention. All Container Apps must have health probes and alert rules.

## Cross-references
- `agents/knowledge/benchmarks/odoo-sh-persona-model.md`
- `agents/personas/odoo-platform-admin.md`
- `.claude/rules/infrastructure.md`
