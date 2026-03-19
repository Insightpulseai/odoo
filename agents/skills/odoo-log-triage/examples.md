# Examples — odoo-log-triage

## Example 1: Post-deployment error spike

**Input**: Error rate increased after revision `ipai-odoo-dev-web--abc123` deployed 30 minutes ago

**Output**:
- Time range: 2026-03-17T10:00:00Z to 2026-03-17T10:30:00Z
- Total errors: 47 ERROR, 12 WARNING
- Top errors:
  1. `odoo.modules.loading: Module ipai_helpdesk: ImportError` (23 occurrences) — Module: dependency conflict
  2. `odoo.http: 500 Internal Server Error /web/dataset/call_kw` (15 occurrences) — HTTP: caused by module load failure
  3. `odoo.sql_db: Connection pool exhausted` (9 occurrences) — Database: connection leak
- Correlation: revision `abc123` deployed at 10:02:00Z, errors started at 10:03:15Z
- Root cause: `ipai_helpdesk` module has unmet dependency — rollback to previous revision recommended
- Evidence: `az containerapp logs show --name ipai-odoo-dev-web --resource-group rg-ipai-dev --type system`

## Example 2: Intermittent timeout pattern

**Input**: Users reporting sporadic slow page loads over past 24 hours

**Output**:
- Time range: 2026-03-16T10:00:00Z to 2026-03-17T10:00:00Z
- Total errors: 8 ERROR, 34 WARNING
- Top errors:
  1. `odoo.http: 504 Gateway Timeout /web/action/load` (8 occurrences) — Timeout: long-running queries
- Pattern: all timeouts occur between 14:00-16:00 UTC, correlated with batch cron execution
- Root cause: cron job `ir_cron_sale_order_sync` holding database locks during peak usage
- Evidence: Log Analytics KQL query with timestamp distribution
