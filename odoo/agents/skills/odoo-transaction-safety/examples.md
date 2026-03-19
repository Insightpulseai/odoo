# Examples — odoo-transaction-safety

## Example 1: Clean code — PASS

**Input**: `ipai_finance_ppm/models/portfolio.py` — standard business logic module.

**Review**:
```
Transaction Safety Report

Critical violations: none
High violations: none
Medium violations: none
Low violations: none

Details:
- No cr.commit() found — PASS
- No raw SQL found — PASS
- ORM usage: mapped() at line 45, filtered() at line 52, sorted() at line 58 — PASS
- Context: with_context(lang='en_US') at line 30 — PASS
- sudo(): line 72 — justified: "sudo: bypass ACL for system-level portfolio rebalance" — PASS
- ensure_one() at line 80 before action_confirm — PASS

Risk assessment: low
```

## Example 2: Code with cr.commit() — FAIL

**Input**: `ipai_bulk_import/models/import_wizard.py` — bulk import wizard.

**Review**:
```
Transaction Safety Report

Critical violations:
- [CRITICAL] models/import_wizard.py:89 — cr.commit() without justification
  Code: `self.env.cr.commit()  # save progress`
  The comment "save progress" is not a valid justification. It does not explain why
  ORM transaction boundaries are insufficient or document rollback implications.

- [CRITICAL] models/import_wizard.py:120 — cr.commit() without justification
  Code: `self.env.cr.commit()`
  No comment at all.

High violations:
- [HIGH] models/import_wizard.py:65 — context mutation
  Code: `self.env.context['importing'] = True`
  Must use: `self.with_context(importing=True)`

Medium violations:
- [MEDIUM] models/import_wizard.py:40 — sudo() without documentation
  Code: `records = self.sudo().search([('active', '=', False)])`
  No comment explaining why sudo is needed.

Remediation:
1. Remove cr.commit() at line 89 — restructure to process in ORM-managed batches.
   If memory management truly requires intermediate commits (e.g., 100k+ records),
   add explicit justification: "cr.commit(): required for memory management in
   batch of N records. Rollback granularity is per-batch, not per-record."
2. Remove cr.commit() at line 120 — same as above.
3. Replace context mutation at line 65 with with_context().
4. Add justification comment for sudo() at line 40.

Risk assessment: critical
```

## Example 3: Code with raw SQL — conditional PASS

**Input**: `ipai_data_migration/models/migrate_partners.py` — data migration script.

**Review**:
```
Transaction Safety Report

Critical violations: none

High violations:
- [HIGH] models/migrate_partners.py:35 — raw SQL for bulk update
  Code: `self.env.cr.execute("UPDATE res_partner SET active = %s WHERE ...", [True])`
  Context: migration script for activating 50k partner records.

  Assessment: ACCEPTABLE with conditions.
  - Parameterized query (no SQL injection risk) — PASS
  - Performance justification present in docstring: "ORM write() on 50k records
    causes N+1 recompute; raw SQL completes in 2s vs 45min" — PASS
  - Wrapped in try/except with specific IntegrityError catch — PASS

  Recommendation: Add `# raw SQL: performance — ORM recompute prohibitive at 50k records`
  inline comment for future reviewers.

Medium violations:
- [MEDIUM] models/migrate_partners.py:22 — sudo() without documentation
  Code: `self.sudo().env.cr.execute(...)`
  Add justification: "sudo: migration runs as system, bypassing per-user ACL"

Remediation:
1. Add inline comment for raw SQL at line 35
2. Add sudo() justification at line 22

Risk assessment: medium (acceptable for migration context with fixes)
```
