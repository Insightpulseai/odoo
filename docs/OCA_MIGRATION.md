# IPAI Module Deprecation Plan

> **Principle**: Extend OCA modules, minimize custom delta code.

## OCA Modules Added (external-src/)

| OCA Repository | Key Modules | Replaces |
|----------------|-------------|----------|
| `reporting-engine` | `bi_sql_editor` | `ipai_finance_ppm_dashboard` |
| `account-closing` | `account_fiscal_year_closing`, `account_cutoff_base` | `ipai_finance_monthly_closing` |
| `project` | `project_milestone_status`, `project_stage_last_update_date` | Parts of `ipai_ppm_monthly_close` |

## Deprecation Schedule

### Phase 1: Immediate Removal (No Data Migration Needed)

| Module | Status | Replacement |
|--------|--------|-------------|
| `ipai_finance_ppm_dashboard` | **DEPRECATED** | Use `bi_sql_editor` from OCA |
| `ipai_docs` | **DEPRECATED** | Use native Odoo 18 Knowledge app |
| `ipai_docs_project` | **DEPRECATED** | Native Knowledge has project integration |

### Phase 2: Consolidate (Data Migration Required)

| Module | Status | Action |
|--------|--------|--------|
| `ipai_ppm_monthly_close` | **CONSOLIDATE** | Keep task templates, extend `account_fiscal_year_closing` |
| `ipai_finance_monthly_closing` | **MERGE** | Merge into `ipai_ppm_monthly_close` |
| `ipai_finance_ppm` | **REDUCE** | Keep only BIR-specific logic, extend OCA project modules |

### Phase 3: Keep (Legitimate Deltas)

| Module | Status | Reason |
|--------|--------|--------|
| `ipai_ce_cleaner` | **KEEP** | No OCA equivalent for hiding Enterprise upsells |
| `tbwa_spectra_integration` | **KEEP** | Company-specific Spectra export format |

## Migration Steps

### For ipai_docs Users:
```bash
# Install native Knowledge
./odoo-bin -d your_db -i knowledge --stop-after-init

# Data export (if needed)
./odoo-bin shell -d your_db << 'EOF'
docs = env['ipai.doc'].search([])
for doc in docs:
    env['knowledge.article'].create({
        'name': doc.name,
        'body': doc.body_html,
        'sequence': doc.sequence,
    })
env.cr.commit()
EOF
```

### For ipai_finance_ppm_dashboard Users:
```sql
-- Create equivalent view in bi_sql_editor
-- See external-src/reporting-engine/bi_sql_editor/README.rst
```

## Updated addons_path

After migration, update `odoo.conf`:
```ini
addons_path = /mnt/extra-addons,/mnt/external-src/reporting-engine,/mnt/external-src/account-closing,/mnt/external-src/project
```

## Final Target State

```
addons/
├── ipai_ce_cleaner/           # KEEP - unique delta
├── ipai_bir_compliance/       # NEW - thin delta extending OCA account-closing
└── tbwa_spectra_integration/  # KEEP - company-specific export

external-src/
├── reporting-engine/          # OCA - dashboards, BI
├── account-closing/           # OCA - fiscal close, cutoffs
└── project/                   # OCA - project extensions
```

---
**Last Updated**: 2025-11-25
