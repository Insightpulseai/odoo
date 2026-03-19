# odoo-log-triage

Filters, classifies, and triages Odoo server logs from Azure Container Apps using Azure Log Analytics.

## When to use
- Error rate spike detected in monitoring
- Post-deployment health check requires log review
- User-reported issue needs log-based root cause analysis
- Recurring error pattern investigation

## Key rule
Every error must be classified by category (ORM, HTTP, module, database, timeout, memory). Never dismiss recurring errors without classification. Secrets found in logs must be redacted.

## Cross-references
- `agents/knowledge/benchmarks/odoo-sh-persona-model.md`
- `agents/personas/odoo-developer.md`
- `.claude/rules/infrastructure.md`
