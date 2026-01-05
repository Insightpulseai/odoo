# IPAI Module Inventory

Generated: 2026-01-05 10:40:33

## Summary

| Metric | Count |
|--------|-------|
| Total Modules | 43 |
| OK Status | 43 |
| Enterprise Deps | 0 |
| Applications | 9 |
| Installable | 43 |

## Recommendations Summary

| Recommendation | Count |
|----------------|-------|
| KEEP | 37 |
| DEMOTE | 6 |
| REVIEW | 0 |
| REFACTOR | 0 |

## Module Details

| Module | Version | App | Rec | Type | Reason |
|--------|---------|-----|-----|------|--------|
| ipai | 18.0.1.0.0 | No | KEEP | namespace | Namespace/container module |
| ipai_advisor | 18.0.1.0.0 | No | KEEP | integration | AI/Integration functionality |
| ipai_agent_core | 18.0.1.0.0 | No | KEEP | integration | AI/Integration functionality |
| ipai_ai_studio | 18.0.1.0.0 | Yes | KEEP | integration | AI/Integration functionality |
| ipai_ask_ai | 18.0.1.0.0 | Yes | KEEP | integration | AI/Integration functionality |
| ipai_ask_ai_chatter | 18.0.1.0.0 | No | KEEP | integration | AI/Integration functionality |
| ipai_assets | 18.0.1.1.0 | Yes | KEEP | integration | AI/Integration functionality |
| ipai_bir_compliance | 18.0.1.0.0 | No | KEEP | core_business | Core business logic for finance/tax compliance |
| ipai_ce_branding | 18.0.1.2.0 | No | DEMOTE | branding | Branding/UI customization - should be application=... |
| ipai_ce_cleaner | 18.0.1.0.0 | No | DEMOTE | branding | Branding/UI customization - should be application=... |
| ipai_clarity_ppm_parity | 18.0.1.1.0 | No | KEEP | core_business | Core business logic for finance/tax compliance |
| ipai_close_orchestration | 18.0.1.0.0 | Yes | KEEP | core_business | Core business logic for finance/tax compliance |
| ipai_custom_routes | 18.0.1.0.0 | No | DEMOTE | patch | Technical patch - should be application=False |
| ipai_default_home | 18.0.3.0.0 | No | KEEP | integration | AI/Integration functionality |
| ipai_dev_studio_base | 18.0.1.1.0 | No | KEEP | integration | AI/Integration functionality |
| ipai_equipment | 18.0.1.0.0 | No | KEEP | integration | AI/Integration functionality |
| ipai_expense | 18.0.1.0.0 | Yes | KEEP | integration | AI/Integration functionality |
| ipai_finance_bir_compliance | 18.0.1.0.0 | No | KEEP | core_business | Core business logic for finance/tax compliance |
| ipai_finance_close_automation | 18.0.1.0.0 | No | KEEP | core_business | Core business logic for finance/tax compliance |
| ipai_finance_close_seed | 18.0.1.0.0 | No | DEMOTE | seed | Data seeding module - should be application=False |
| ipai_finance_month_end | 18.0.1.0.0 | No | KEEP | core_business | Core business logic for finance/tax compliance |
| ipai_finance_monthly_closing | 18.0.1.0.0 | No | KEEP | core_business | Core business logic for finance/tax compliance |
| ipai_finance_ppm | 18.0.1.0.0 | Yes | KEEP | core_business | Core business logic for finance/tax compliance |
| ipai_finance_ppm_closing | 18.0.1.1.0 | No | KEEP | core_business | Core business logic for finance/tax compliance |
| ipai_finance_ppm_dashboard | 18.0.1.0.0 | No | KEEP | core_business | Core business logic for finance/tax compliance |
| ipai_finance_ppm_tdi | 18.0.1.0.0 | No | KEEP | core_business | Core business logic for finance/tax compliance |
| ipai_finance_project_hybrid | 18.0.1.0.0 | No | KEEP | core_business | Core business logic for finance/tax compliance |
| ipai_industry_accounting_firm | 18.0.1.0.0 | No | KEEP | integration | AI/Integration functionality |
| ipai_industry_marketing_agency | 18.0.1.0.0 | No | KEEP | integration | AI/Integration functionality |
| ipai_marketing_ai | 18.0.1.0.0 | Yes | KEEP | integration | AI/Integration functionality |
| ipai_master_control | 18.0.1.0.0 | No | KEEP | integration | AI/Integration functionality |
| ipai_ocr_expense | 18.0.1.0.0 | No | KEEP | integration | AI/Integration functionality |
| ipai_portal_fix | 18.0.1.0.1 | No | DEMOTE | patch | Technical patch - should be application=False |
| ipai_ppm | 18.0.1.0.0 | No | KEEP | core_business | Core business logic for finance/tax compliance |
| ipai_ppm_a1 | 18.0.1.0.0 | No | KEEP | core_business | Core business logic for finance/tax compliance |
| ipai_ppm_monthly_close | 18.0.1.0.0 | No | KEEP | core_business | Core business logic for finance/tax compliance |
| ipai_project_program | 18.0.1.0.0 | No | KEEP | integration | AI/Integration functionality |
| ipai_project_suite | 18.0.1.0.0 | No | KEEP | integration | AI/Integration functionality |
| ipai_srm | 18.0.1.0.0 | Yes | KEEP | integration | AI/Integration functionality |
| ipai_studio_ai | 18.0.1.1.0 | No | KEEP | integration | AI/Integration functionality |
| ipai_superset_connector | 18.0.1.0.0 | Yes | KEEP | integration | AI/Integration functionality |
| ipai_test_fixtures | 18.0.1.0.0 | No | DEMOTE | test | Test support module - should be application=False |
| ipai_workspace_core | 18.0.1.0.0 | No | KEEP | integration | AI/Integration functionality |

## Potential Duplicates

These module groups may have overlapping functionality:

- **ipai_finance_ppm**: ipai_finance_ppm_closing, ipai_finance_ppm_tdi, ipai_finance_ppm_dashboard
- **ipai_finance_close**: ipai_finance_close_automation, ipai_finance_close_seed
- **ipai**: ipai_ppm, ipai

