# IPAI Module Installation Order

This document defines the **correct installation order** for IPAI custom modules based on their dependency hierarchy. Installing modules in the wrong order will cause errors.

## Quick Reference

```bash
# Install in this order (or let Odoo resolve dependencies automatically)
# Phase 1 → Phase 2 → Phase 3
```

## Dependency Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         PHASE 1: Foundation                             │
│                    (No IPAI dependencies - install first)               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ipai_dev_studio_base     ipai_finance_ppm      ipai_project_program    │
│  ipai_ppm_monthly_close   ipai_expense          ipai_finance_close_seed │
│  ipai_close_orchestration ipai_bir_compliance   ipai_ppm_a1             │
│  + 20 other foundation modules                                          │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                         PHASE 2: Level 1 Dependents                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ipai_workspace_core        ← ipai_dev_studio_base                      │
│  ipai_ask_ai                ← ipai_finance_ppm                          │
│  ipai_finance_close_automation ← ipai_finance_close_seed                │
│  ipai_finance_bir_compliance ← ipai_project_program                     │
│  ipai_finance_month_end     ← ipai_project_program                      │
│  ipai_finance_ppm_closing   ← ipai_finance_ppm + ipai_ppm_monthly_close │
│  ipai_ocr_expense           ← ipai_expense                              │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                         PHASE 3: Level 2+ Dependents                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ipai_ask_ai_chatter        ← ipai_ask_ai ← ipai_finance_ppm            │
│  ipai_industry_accounting_firm ← ipai_workspace_core ← ipai_dev_studio  │
│  ipai_industry_marketing_agency ← ipai_workspace_core ← ipai_dev_studio │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Foundation Modules

These modules have **no IPAI dependencies** and can be installed in any order (or in parallel):

| Module | Depends On (Odoo Core) | Category |
|--------|------------------------|----------|
| `ipai_dev_studio_base` | base, web, mail, contacts, project | **INSTALL FIRST** |
| `ipai_finance_ppm` | base, mail, project | Finance |
| `ipai_finance_close_seed` | project, resource | Finance |
| `ipai_project_program` | project, mail | Project |
| `ipai_ppm_monthly_close` | base, project, mail, resource | Project |
| `ipai_expense` | hr, hr_expense, account, project | HR/Expenses |
| `ipai_close_orchestration` | base, mail | Accounting |
| `ipai_bir_compliance` | account | Accounting |
| `ipai_ppm_a1` | base, mail, project | Project |
| `ipai_advisor` | base, mail | Operations |
| `ipai_agent_core` | base, web | AI |
| `ipai_ai_studio` | base, web | Productivity |
| `ipai_assets` | base, mail, hr, stock | Equipment |
| `ipai_ce_branding` | web, base | Theme |
| `ipai_ce_cleaner` | base, web | Tools |
| `ipai_clarity_ppm_parity` | project | Project |
| `ipai_custom_routes` | base, web, mail, calendar, project, hr_expense | Tools |
| `ipai_default_home` | base, web, mail | Tools |
| `ipai_equipment` | stock, maintenance, project | Inventory |
| `ipai_finance_monthly_closing` | project | Finance |
| `ipai_finance_ppm_dashboard` | base, web | Reporting |
| `ipai_finance_ppm_tdi` | base, project, hr, account | Finance |
| `ipai_finance_project_hybrid` | project, mail | Project |
| `ipai_master_control` | base, hr, hr_expense, purchase | Productivity |
| `ipai_portal_fix` | portal | Technical |
| `ipai_ppm` | project, hr, mail | Project |
| `ipai_srm` | base, mail, purchase, contacts | Inventory |
| `ipai_studio_ai` | base, mail | Customization |
| `ipai_test_fixtures` | base, hr, project | Testing |

---

## Phase 2: Level 1 Dependents

These modules depend on **one IPAI module** from Phase 1:

| Module | IPAI Dependency | Must Install After |
|--------|-----------------|-------------------|
| `ipai_workspace_core` | ipai_dev_studio_base | Phase 1 |
| `ipai_ask_ai` | ipai_finance_ppm | Phase 1 |
| `ipai_finance_close_automation` | ipai_finance_close_seed | Phase 1 |
| `ipai_finance_bir_compliance` | ipai_project_program | Phase 1 |
| `ipai_finance_month_end` | ipai_project_program | Phase 1 |
| `ipai_finance_ppm_closing` | ipai_finance_ppm, ipai_ppm_monthly_close | Phase 1 |
| `ipai_ocr_expense` | ipai_expense | Phase 1 |

---

## Phase 3: Level 2+ Dependents

These modules have **transitive IPAI dependencies** (depend on Phase 2 modules):

| Module | Dependency Chain | Max Depth |
|--------|-----------------|-----------|
| `ipai_ask_ai_chatter` | ipai_ask_ai → ipai_finance_ppm | 2 |
| `ipai_industry_accounting_firm` | ipai_workspace_core → ipai_dev_studio_base | 2 |
| `ipai_industry_marketing_agency` | ipai_workspace_core → ipai_dev_studio_base | 2 |

---

## Key Dependency Chains

### Workspace Stack
```
ipai_dev_studio_base          # Foundation (install first)
    └── ipai_workspace_core   # Core workspace
        ├── ipai_industry_accounting_firm
        └── ipai_industry_marketing_agency
```

### Finance PPM Stack
```
ipai_finance_ppm              # Foundation
    ├── ipai_ask_ai           # AI assistant
    │   └── ipai_ask_ai_chatter
    └── ipai_finance_ppm_closing (+ ipai_ppm_monthly_close)
```

### Project Program Stack
```
ipai_project_program          # Foundation
    ├── ipai_finance_bir_compliance
    └── ipai_finance_month_end
```

### Finance Close Stack
```
ipai_finance_close_seed       # Foundation (seed data)
    └── ipai_finance_close_automation
```

### Expense Stack
```
ipai_expense                  # Foundation
    └── ipai_ocr_expense      # OCR digitization
```

---

## Installation Commands

### Option 1: Install All (Let Odoo Resolve Dependencies)
```bash
# Odoo will automatically install dependencies in correct order
docker exec -t odoo-core odoo -d odoo_core \
  -i ipai_dev_studio_base,ipai_workspace_core,ipai_industry_marketing_agency,ipai_industry_accounting_firm,ipai_finance_ppm,ipai_ask_ai,ipai_ask_ai_chatter \
  --db_host=postgres --stop-after-init
```

### Option 2: Install by Phase (Explicit Order)
```bash
# Phase 1: Foundation
docker exec -t odoo-core odoo -d odoo_core \
  -i ipai_dev_studio_base,ipai_finance_ppm,ipai_project_program,ipai_expense,ipai_ppm_monthly_close,ipai_finance_close_seed,ipai_close_orchestration \
  --db_host=postgres --stop-after-init

# Phase 2: Level 1
docker exec -t odoo-core odoo -d odoo_core \
  -i ipai_workspace_core,ipai_ask_ai,ipai_finance_close_automation,ipai_finance_bir_compliance,ipai_finance_month_end,ipai_finance_ppm_closing,ipai_ocr_expense \
  --db_host=postgres --stop-after-init

# Phase 3: Level 2+
docker exec -t odoo-core odoo -d odoo_core \
  -i ipai_ask_ai_chatter,ipai_industry_accounting_firm,ipai_industry_marketing_agency \
  --db_host=postgres --stop-after-init
```

---

## Verification

After installation, verify module states:
```bash
docker exec -t odoo-core odoo shell -d odoo_core --db_host=postgres --stop-after-init <<'PY'
modules = env['ir.module.module'].search([('name', 'like', 'ipai_%')])
for m in modules.sorted(lambda x: x.name):
    print(f"{m.name:40} {m.state:12} {m.latest_version or '-'}")
PY
```

---

## Notes

1. **Odoo handles dependencies**: If you install a module with dependencies, Odoo will automatically install the dependencies first
2. **No circular dependencies**: The IPAI module graph has no cycles
3. **Maximum depth**: 3 levels (Foundation → Level 1 → Level 2)
4. **Safe to re-run**: Installing already-installed modules is a no-op

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total IPAI modules | 40 |
| Foundation (Phase 1) | 28 |
| Level 1 (Phase 2) | 8 |
| Level 2+ (Phase 3) | 3 |
| Max dependency depth | 3 |
| Circular dependencies | None |

---

*Last updated: 2026-01-05*
*Generated from manifest analysis*
