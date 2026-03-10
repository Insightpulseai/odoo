# DB Reorg Migration Plan

This plan describes how to move from the current layout to the target architecture, starting with a canonical example:

> `public.expense_reports` → `expense.expense_reports`

All changes are designed to be **reviewed** and **explicitly executed**; nothing is auto-run.

---

## 1. Principles

- **Non-destructive** steps: No `DROP` or `TRUNCATE` in initial migrations
- **Backward compatibility**: `public.*` remains viable via views + INSTEAD OF triggers
- **Small, testable slices**: Start with one high-value table, then expand

---

## 2. Generic Migration Pattern

```sql
-- Step 1: Create schema
CREATE SCHEMA IF NOT EXISTS <domain>;

-- Step 2: Create table
CREATE TABLE IF NOT EXISTS <domain>.<table> (LIKE public.<table> INCLUDING ALL);

-- Step 3: Copy data
INSERT INTO <domain>.<table>
SELECT * FROM public.<table>
ON CONFLICT DO NOTHING;

-- Step 4: Optional - rename legacy
ALTER TABLE public.<table> RENAME TO <table>_legacy;

-- Step 5: Create compatibility view
CREATE OR REPLACE VIEW public.<table> AS
SELECT * FROM <domain>.<table>;

-- Step 6: Optional - INSTEAD OF triggers for write compatibility
```

---

## 3. Top 10 Priority Tables

| Priority | Table | Target | Notes |
|----------|-------|--------|-------|
| 1 | public.expense_reports | expense.expense_reports | Example migration complete |
| 2 | public.expenses | expense.expenses | |
| 3 | public.cash_advances | expense.cash_advances | |
| 4 | public.projects | projects.projects | |
| 5 | public.project_budget_lines | projects.project_budget_lines | |
| 6 | public.vendor_profile | rates.vendor_profile | |
| 7 | public.rate_card_items | rates.rate_card_items | |
| 8 | public.bir_chunks | finance.bir_chunks | |
| 9 | gold.docs | gold.docs | Already canonical |
| 10 | public.agent_runs | mcp.agent_runs | Or keep public as read-surface |

---

## 4. Validation Queries

### Row Count Comparison
```sql
SELECT
  (SELECT count(*) FROM public.expense_reports) AS public_count,
  (SELECT count(*) FROM expense.expense_reports) AS expense_count;
```

### Missing Rows
```sql
SELECT id FROM public.expense_reports
EXCEPT
SELECT id FROM expense.expense_reports
LIMIT 50;
```

### Recent Writes
```sql
SELECT * FROM expense.expense_reports
WHERE created_at > now() - interval '5 minutes'
ORDER BY created_at DESC
LIMIT 10;
```

---

## 5. Maintenance Runbook

### Pre-Checks
- [ ] Backups/snapshots available and tested
- [ ] Staging run completed and validated
- [ ] Stakeholders notified (app teams, DBAs)
- [ ] No long-running transactions against target tables

### Migration Order
1. Run: `202512071200_REORG_CREATE_DOMAIN_TABLES.sql`
2. Run: `202512071205_REORG_COPY_DATA.sql`
3. Validate (row counts, samples)
4. Run: `202512071210_REORG_CREATE_COMPAT_VIEWS.sql` (maintenance window)
5. Optional: `202512071215_REORG_VIEW_WRITE_FORWARDING.sql`

### Post-Cutover
- [ ] Application can read/write via chosen path
- [ ] Row count checks pass
- [ ] FK integrity verified
- [ ] RLS policies applied

---

## 6. Rollback Steps

If cutover introduces errors:

1. Drop view/trigger:
```sql
DROP TRIGGER IF EXISTS tr_expense_reports_insert ON public.expense_reports;
DROP VIEW IF EXISTS public.expense_reports;
```

2. Rename legacy table back:
```sql
ALTER TABLE public.expense_reports_legacy RENAME TO expense_reports;
```

3. Re-deploy previous app version pointing at `public.expense_reports`

---

## 7. Hygiene SQL (Optional)

### Add Canonical Comments
```sql
COMMENT ON TABLE expense.expense_reports IS
  'Domain: T&E. Canonical home for expense reports (migrated from public.expense_reports). Owner: finance-ssc@insightpulseai.com.';
```

### Add Source Metadata to Gold Tables
```sql
ALTER TABLE gold.docs
  ADD COLUMN IF NOT EXISTS source_schema text,
  ADD COLUMN IF NOT EXISTS source_table text,
  ADD COLUMN IF NOT EXISTS source_pk text;
```

---

## 8. Contacts

- **Data Owner**: business@insightpulseai.com
- **Technical Owner**: jgtolentino_rn@yahoo.com
