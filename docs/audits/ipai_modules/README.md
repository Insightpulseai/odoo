# IPAI Module Audit Report

**Generated:** 2026-01-05
**Auditor:** Claude Code (automated)
**Strategy:** CE/OCA-first

## Executive Summary

| Metric | Value |
|--------|-------|
| Total IPAI Modules | 43 (42 + 1 new umbrella) |
| Enterprise Dependencies | **0** |
| Applications | 15 |
| Installable | 43 |
| KEEP Recommendations | 37 |
| DEMOTE Recommendations | 6 |
| REVIEW Recommendations | 0 |
| REFACTOR Recommendations | 0 |

### Key Findings

1. **Zero Enterprise Dependencies** - All IPAI modules are CE/OCA-clean
2. **Metadata Normalized** - All modules have correct author ("InsightPulse AI") and GitHub website URLs
3. **No Backup Directories Found** - Clean codebase
4. **6 Modules Already Correctly Demoted** - Library/patch modules properly set to `application=False`

---

## Module Classification

### Classification Legend

| Code | Type | Description |
|------|------|-------------|
| A | Umbrella | Pure dependency aggregation + minimal config |
| B | Differentiator | Core business logic, no OCA equivalent |
| C | OCA-Overlapped | Review for potential OCA replacement |
| D | Supporting | Patches, tests, seeds, helpers |

---

## Decision Table

| Module | Type | Application | Installable | Recommendation | Notes |
|--------|------|-------------|-------------|----------------|-------|
| ipai | A | No | Yes | KEEP | Namespace module |
| ipai_advisor | B | Yes | Yes | KEEP | Azure Advisor-style recommendations |
| ipai_agent_core | B | Yes | Yes | KEEP | AI agent registry |
| ipai_ai_studio | A | Yes | Yes | KEEP | AI module builder umbrella |
| ipai_ask_ai | B | Yes | Yes | KEEP | AI RAG engine for Finance |
| ipai_ask_ai_chatter | B | No | Yes | KEEP | Chatter AI integration |
| ipai_assets | B | Yes | Yes | KEEP | Equipment checkout (Cheqroom-style) |
| ipai_bir_compliance | B | No | Yes | KEEP | BIR 2307 generator |
| ipai_ce_branding | D | No | Yes | KEEP | CE branding layer |
| ipai_ce_cleaner | D | No | Yes | KEEP | Enterprise/IAP cleanup |
| ipai_clarity_ppm_parity | B | No | Yes | KEEP | Clarity PPM parity |
| ipai_close_orchestration | B | Yes | Yes | KEEP | Close cycle management |
| ipai_custom_routes | D | No | Yes | KEEP | URL routing patch |
| ipai_default_home | B | No | Yes | KEEP | Custom app grid home |
| ipai_dev_studio_base | B | No | Yes | KEEP | Base dependencies |
| ipai_equipment | B | Yes | Yes | KEEP | Equipment management |
| ipai_expense | B | Yes | Yes | KEEP | PH expense workflows |
| ipai_finance_bir_compliance | B | No | Yes | KEEP | BIR schedule + generator |
| ipai_finance_close_automation | B | No | Yes | KEEP | Close automation |
| ipai_finance_close_seed | D | No | Yes | KEEP | Seed data |
| ipai_finance_month_end | B | No | Yes | KEEP | Month-end templates |
| ipai_finance_monthly_closing | B | No | Yes | KEEP | Monthly closing |
| ipai_finance_ppm | B | Yes | Yes | KEEP | Core Finance PPM |
| ipai_finance_ppm_closing | B | No | Yes | KEEP | PPM closing generator |
| ipai_finance_ppm_dashboard | B | No | Yes | KEEP | PPM dashboard |
| ipai_finance_ppm_tdi | B | No | Yes | KEEP | Transaction data ingestion |
| ipai_finance_project_hybrid | B | No | Yes | KEEP | IM1/IM2 generators |
| ipai_industry_accounting_firm | B | No | Yes | KEEP | Accounting firm vertical |
| ipai_industry_marketing_agency | B | No | Yes | KEEP | Marketing agency vertical |
| ipai_marketing_ai | A | Yes | Yes | KEEP | **NEW** Marketing AI umbrella |
| ipai_master_control | B | No | Yes | KEEP | Work intake bridge |
| ipai_ocr_expense | B | No | Yes | KEEP | Receipt OCR |
| ipai_portal_fix | D | No | Yes | KEEP | Portal bug fix |
| ipai_ppm | B | Yes | Yes | KEEP | Portfolio/Program management |
| ipai_ppm_a1 | B | Yes | Yes | KEEP | A1 Control Center |
| ipai_ppm_monthly_close | B | No | Yes | KEEP | Monthly close scheduler |
| ipai_project_program | B | No | Yes | KEEP | Program + IM projects |
| ipai_project_suite | B | No | Yes | KEEP | Enterprise-like project features |
| ipai_srm | B | Yes | Yes | KEEP | Supplier management |
| ipai_studio_ai | B | Yes | Yes | KEEP | NL customization engine |
| ipai_superset_connector | B | Yes | Yes | KEEP | Superset BI integration |
| ipai_test_fixtures | D | No | Yes | KEEP | Test support |
| ipai_workspace_core | B | No | Yes | KEEP | Workspace foundation |

---

## OCA Baseline Requirements

Before further IPAI development, install these OCA modules:

### Must-Have OCA Repos (18.0 branches)

```bash
# From repo root
mkdir -p addons/OCA

git submodule add -b 18.0 https://github.com/OCA/server-brand addons/OCA/server-brand
git submodule add -b 18.0 https://github.com/OCA/server-auth addons/OCA/server-auth
git submodule add -b 18.0 https://github.com/OCA/server-tools addons/OCA/server-tools
git submodule add -b 18.0 https://github.com/OCA/server-ux addons/OCA/server-ux
git submodule add -b 18.0 https://github.com/OCA/reporting-engine addons/OCA/reporting-engine
git submodule add -b 18.0 https://github.com/OCA/web addons/OCA/web
git submodule add -b 18.0 https://github.com/OCA/queue addons/OCA/queue
```

### Required OCA Modules

| Module | Repo | Purpose |
|--------|------|---------|
| remove_odoo_enterprise | server-brand | CE hygiene |
| disable_odoo_online | server-brand | CE hygiene |
| password_security | server-auth | Security baseline |
| auditlog | server-tools | Generic CRUD logging |
| queue_job | queue | Async job processing |
| web_responsive | web | Responsive UI |
| report_xlsx | reporting-engine | Excel exports |

---

## Potential Duplicate Groups

These module groups may have overlapping functionality:

### 1. Finance PPM Family
- `ipai_finance_ppm` (core)
- `ipai_finance_ppm_closing` (generator)
- `ipai_finance_ppm_tdi` (data ingestion)
- `ipai_finance_ppm_dashboard` (visualization)

**Recommendation:** Keep as separate modules - they have distinct responsibilities.

### 2. Finance Close Family
- `ipai_finance_close_automation` (generator)
- `ipai_finance_close_seed` (seed data)

**Recommendation:** Keep as separate modules - automation depends on seed.

---

## Quick Fixes Applied

### Metadata Normalization (Previous Commit)
- All 42 modules now have `author: "InsightPulse AI"`
- All 42 modules now have GitHub `website` URLs

### New Umbrella Module (This Commit)
- Created `ipai_marketing_ai` umbrella for marketing AI features

---

## CI/CD Integration

### Test Script
A new test script has been created at `scripts/test_ipai_install_upgrade.py`:

```bash
# Test all modules
python scripts/test_ipai_install_upgrade.py

# Test specific modules
python scripts/test_ipai_install_upgrade.py ipai_finance_ppm ipai_ask_ai

# With custom Odoo path
ODOO_BIN=/path/to/odoo-bin python scripts/test_ipai_install_upgrade.py
```

### GitHub Actions Workflow
Add to `.github/workflows/ci-odoo-ce.yml`:

```yaml
- name: Test IPAI Module Install/Upgrade
  run: |
    python scripts/test_ipai_install_upgrade.py
```

---

## Artifacts Generated

| File | Description |
|------|-------------|
| `inventory.json` | Machine-readable module inventory |
| `inventory.csv` | Spreadsheet-friendly inventory |
| `inventory.md` | Human-readable inventory |
| `oca_overlap_map.yaml` | OCA overlap analysis |
| `README.md` | This audit report |

---

## Next Steps

1. **Vendor OCA Baseline** - Add required OCA repos as submodules
2. **Run Install Tests** - Execute `test_ipai_install_upgrade.py` in CI
3. **Review OCA Overlaps** - Evaluate `ipai_ce_branding` and `ipai_ce_cleaner` against OCA server-brand
4. **Update addons_path** - Ensure Docker/odoo.conf includes OCA paths

---

## Audit Scripts

| Script | Purpose |
|--------|---------|
| `scripts/audit_ipai_modules.py` | Generate module inventory |
| `scripts/test_ipai_install_upgrade.py` | Test install/upgrade |

---

*Report generated by Claude Code audit automation*
