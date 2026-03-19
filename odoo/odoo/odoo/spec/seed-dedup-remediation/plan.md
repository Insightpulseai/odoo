# Seed Data Deduplication — Remediation Plan

> Evidence: `docs/architecture/SEED_DATA_INVENTORY.md`
> Branch: TBD (dedicated remediation branch, not `fix/foundry-endpoint-audit`)
> Status: Planned — not yet started

---

## Workstream 1: Finance Task Seed Canonicalization

### Canonical Source

**Module**: `ipai_finance_workflow`
**Files** (keep):
- `data/finance_task_stages.xml` — 5 stages with `finance_stage_code`
- `data/finance_projects.xml` — 2 projects (Month-End Close + BIR Returns)
- `data/finance_ppm_tasks.xml` — 20 tasks with preparer/reviewer/approver

### Deprecated Sources (remove seed data)

| File | Records | Action |
|------|---------|--------|
| `ipai_finance_close_seed/data/01_stages.xml` | 6 stages | Remove — superseded by workflow stages |
| `ipai_finance_close_seed/data/04_projects.xml` | 2 projects | Remove — superseded by workflow projects |
| `ipai_finance_close_seed/data/06_tasks_month_end.xml` | 39 tasks | Remove — superseded by workflow tasks |
| `ipai_finance_close_seed/data/tasks_month_end.xml` | 36 tasks | Remove — older format, same domain |

### ID Migration Notes

- Old XML IDs: `task_me_01`, `task_close_01_*`, `stage_todo`, `project_month_end_template`
- New XML IDs: `fin_ppm_me_*`, `fin_stage_*`, `fin_project_*`
- If old IDs are referenced by `ir.model.data` in production, need migration script to remap
- Check: `SELECT * FROM ir_model_data WHERE module = 'ipai_finance_close_seed'`

### Install/Update Risk

- **If only `ipai_finance_workflow` is installed**: Safe — no migration needed
- **If both modules installed**: Must run `odoo -u ipai_finance_close_seed` after removing data files, then uninstall the module
- **Rollback**: Restore removed XML files from git history

---

## Workstream 2: Mail Server Seed Canonicalization

### Canonical Source

**Module**: `ipai_zoho_mail`
**File**: `data/mail_server.xml` — Zoho SMTP (`smtppro.zoho.com:587`)

### Deprecated Sources (remove/disable)

| Module | File | Server | Action |
|--------|------|--------|--------|
| `ipai_mailgun_smtp` | `data/ir_mail_server.xml` | Mailgun (deprecated) | **Delete entire module** |
| `ipai_enterprise_bridge` | `data/mail_server.xml` | Zoho (active=False) | Remove mail server record from this file |
| `ipai_zoho_mail_api` | `data/ir_mail_server.xml` | Zoho API variant | Evaluate — may serve different purpose (API vs SMTP) |
| `ipai_system_config` | `hooks.py` (post_init) | SSOT SMTP (env-driven) | Evaluate — hooks.py creates server from env vars at install time |

### Sequence Ownership

After cleanup, exactly **one** `ir.mail_server` record should have `sequence=1`:
- `ipai_zoho_mail.zoho_smtp_server` (canonical)
- All others removed or set to `sequence=99`

### Install/Update Risk

- **Mailgun module removal**: If installed in production, must uninstall first (`odoo -u ipai_mailgun_smtp` then remove from addons path)
- **Rollback**: Restore module from git history + reinstall

---

## Workstream 3: BIR Task Consolidation

### Canonical Source

**File**: `ipai_finance_close_seed/data/07_tasks_bir_tax.xml` (33 tasks — most complete)

### Deprecated Source

| File | Records | Action |
|------|---------|--------|
| `ipai_finance_close_seed/data/tasks_bir.xml` | 27 tasks | Remove — subset of 07_tasks_bir_tax.xml |

### ID Migration Notes

- Both files are in the same module — lower risk
- Check for XML ID overlap: some task IDs may be shared
- `__manifest__.py` data list must be updated to remove the deprecated file

### Install/Update Risk

- Low — same module, just removing a data file
- **Rollback**: Restore file from git history + add back to manifest

---

## Workstream 4: Exact-Copy Mirror Cleanup

### ops-platform/supabase/ mirrors

| File to Delete | Original |
|----------------|----------|
| `ops-platform/supabase/seeds/001_hr_seed.sql` | `supabase/seeds/001_hr_seed.sql` |
| `ops-platform/supabase/seeds/002_finance_seed.sql` | `supabase/seeds/002_finance_seed.sql` |
| `ops-platform/supabase/seeds/003_odoo_dict_seed.sql` | `supabase/seeds/003_odoo_dict_seed.sql` |
| `ops-platform/supabase/seed/` (all subdirs) | `supabase/seed/` |

### Nested odoo/ stale copies

| File to Delete | Original |
|----------------|----------|
| `odoo/ipai_finance_closing_seed.json` | `ipai_finance_closing_seed.json` |
| `odoo/supabase/seeds/002_finance_seed.sql` | `supabase/seeds/002_finance_seed.sql` |
| `odoo/addons/ipai/ipai_agent/data/tools_seed.xml` | `addons/ipai/ipai_agent/data/tools_seed.xml` |
| `odoo/docs/kb/graph_seed.json` | `docs/kb/graph_seed.json` |

### Pre-deletion Verification

Before deleting:
1. `diff` each pair to confirm they are truly identical (or the copy is staler)
2. `grep -r "ops-platform/supabase/seeds"` to find any references
3. `grep -r "odoo/addons/ipai"` to find any references
4. Check CI workflows for paths referencing these copies

### Install/Update Risk

- Low — these are standalone copies, not referenced by Odoo module loaders
- **Rollback**: Restore from git history

---

## Execution Order

1. **Workstream 4** (mirror cleanup) — lowest risk, immediate hygiene
2. **Workstream 3** (BIR consolidation) — same-module cleanup, low risk
3. **Workstream 2** (mail server) — requires install state check
4. **Workstream 1** (finance tasks) — highest impact, requires migration check

---

## Verification Checklist

- [ ] `python3 scripts/ci/validate_platform_strategy.py` passes
- [ ] No broken `ir.model.data` references in production DB
- [ ] `odoo -d test_remediation -i <affected_modules> --stop-after-init` succeeds
- [ ] Exactly one `ir.mail_server` at sequence=1 after mail cleanup
- [ ] No CI workflows reference deleted paths
- [ ] `diff` confirms all deleted copies were true mirrors
