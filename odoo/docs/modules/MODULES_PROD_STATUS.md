# Module Production Readiness Status

**Generated:** 2026-01-06 07:13:51
**Odoo Version:** 18
**Addons Path:** `addons/ipai`

## Summary

| Stage | Count | Percentage |
|-------|-------|------------|
| Stable ✅ | 31 | 54.4% |
| Beta ⚠️ | 26 | 45.6% |
| Experimental 🧪 | 0 | 0.0% |
| Deprecated ☠️ | 0 | 0.0% |

**Blocked Modules:** 0

---

## High-Risk Modules

Modules with risk score ≥ 40:

| Module | Stage | Score | Blocked | Issues |
|--------|-------|-------|---------|--------|
| `ipai_equipment` | beta | 60 | ✓ | Unmet dependencies: maintenance; Module may contain 'tree' view patterns; ipai_v |
| `ipai_marketing_journey` | beta | 55 | ✓ | Unmet dependencies: mass_mailing, utm; Module may contain 'tree' view patterns;  |
| `ipai_project_profitability_bridge` | beta | 55 | ✓ | Unmet dependencies: analytic; Module may contain 'tree' view patterns; ipai_v18_ |

---

## V18 Compatibility Required

These modules may need `ipai_v18_compat` for tree→list view fixes:

- `ipai_agent_core`
- `ipai_ai_audit`
- `ipai_ai_core`
- `ipai_ai_prompts`
- `ipai_ai_provider_pulser`
- `ipai_ai_studio`
- `ipai_clarity_ppm_parity`
- `ipai_equipment`
- `ipai_expense`
- `ipai_finance_bir_compliance`
- `ipai_finance_month_end`
- `ipai_marketing_journey`
- `ipai_project_profitability_bridge`
- `ipai_project_suite`
- `ipai_studio_ai`
- `ipai_superset_connector`
- `ipai_workspace_core`

---

## All Modules

| Module | Category | Stage | Score | Version |
|--------|----------|-------|-------|---------|
| `ipai_advisor` | Operations | stable ✅ | 5 | 18.0.1.0.0 |
| `ipai_agent_core` | Productivity/AI | beta ⚠️ | 25 | 18.0.1.0.0 |
| `ipai_ai_audit` | Productivity/AI | beta ⚠️ | 25 | 18.0.1.0.0 |
| `ipai_ai_core` | Productivity | beta ⚠️ | 25 | 18.0.1.0.0 |
| `ipai_ai_prompts` | Productivity/AI | beta ⚠️ | 25 | 18.0.1.0.0 |
| `ipai_ai_provider_kapa` | Productivity | stable ✅ | 0 | 18.0.1.0.0 |
| `ipai_ai_provider_pulser` | Productivity/AI | beta ⚠️ | 25 | 18.0.1.0.0 |
| `ipai_ai_studio` | Productivity | beta ⚠️ | 25 | 18.0.1.0.0 |
| `ipai_ask_ai` | Productivity/AI | stable ✅ | 0 | 18.0.1.0.0 |
| `ipai_ask_ai_chatter` | Productivity/AI | stable ✅ | 0 | 18.0.1.0.0 |
| `ipai_assets` | Operations/Equipment | stable ✅ | 5 | 18.0.1.1.0 |
| `ipai_auth_oauth_internal` | Technical | beta ⚠️ | 30 | 18.0.1.0.0 |
| `ipai_bir_compliance` | Accounting/Localizations | stable ✅ | 0 | 18.0.1.0.0 |
| `ipai_ce_branding` | Customization | beta ⚠️ | 30 | 18.0.1.2.0 |
| `ipai_ce_cleaner` | Tools | beta ⚠️ | 30 | 18.0.1.0.0 |
| `ipai_chatgpt_sdk_theme` | Themes | stable ✅ | 0 | 18.0.1.0.0 |
| `ipai_clarity_ppm_parity` | Project Management | beta ⚠️ | 25 | 18.0.1.1.0 |
| `ipai_close_orchestration` | Accounting/Close | stable ✅ | 0 | 18.0.1.0.0 |
| `ipai_custom_routes` | Extra Tools | beta ⚠️ | 30 | 18.0.1.0.0 |
| `ipai_default_home` | Extra Tools | stable ✅ | 0 | 18.0.3.0.0 |
| `ipai_dev_studio_base` | Tools | stable ✅ | 0 | 18.0.1.1.0 |
| `ipai_equipment` | Inventory | beta ⚠️ | 60 | 18.0.1.0.0 |
| `ipai_expense` | Human Resources/Expenses | beta ⚠️ | 30 | 18.0.1.0.0 |
| `ipai_finance_bir_compliance` | Accounting/Project | beta ⚠️ | 25 | 18.0.1.0.0 |
| `ipai_finance_close_automation` | Accounting/Project | beta ⚠️ | 30 | 18.0.1.0.0 |
| `ipai_finance_close_seed` | Accounting/Project | beta ⚠️ | 30 | 18.0.1.0.0 |
| `ipai_finance_month_end` | Accounting/Project | beta ⚠️ | 25 | 18.0.1.0.0 |
| `ipai_finance_monthly_closing` | Accounting/Finance | stable ✅ | 0 | 18.0.1.0.0 |
| `ipai_finance_ppm` | Accounting/Finance | stable ✅ | 0 | 18.0.1.0.0 |
| `ipai_finance_ppm_closing` | Accounting/Finance | stable ✅ | 0 | 18.0.1.1.0 |
| `ipai_finance_ppm_dashboard` | Accounting/Reporting | stable ✅ | 0 | 18.0.1.0.0 |
| `ipai_finance_ppm_tdi` | Finance | stable ✅ | 0 | 18.0.1.0.0 |
| `ipai_finance_project_hybrid` | Project | stable ✅ | 0 | 18.0.1.0.0 |
| `ipai_industry_accounting_firm` | InsightPulse/Vertical | stable ✅ | 0 | 18.0.1.0.0 |
| `ipai_industry_marketing_agency` | InsightPulse/Vertical | stable ✅ | 0 | 18.0.1.0.0 |
| `ipai_marketing_ai` | Marketing | beta ⚠️ | 30 | 18.0.1.0.0 |
| `ipai_marketing_journey` | Marketing | beta ⚠️ | 55 | 18.0.1.0.0 |
| `ipai_master_control` | Productivity | stable ✅ | 0 | 18.0.1.0.0 |
| `ipai_module_gating` | Technical | stable ✅ | 0 | 18.0.1.0.0 |
| `ipai_ocr_expense` | Human Resources/Expenses | stable ✅ | 0 | 18.0.1.0.0 |
| `ipai_platform_theme` | Themes | stable ✅ | 0 | 18.0.1.0.0 |
| `ipai_portal_fix` | Technical | beta ⚠️ | 30 | 18.0.1.0.1 |
| `ipai_ppm` | Project Management | stable ✅ | 5 | 18.0.1.0.0 |
| `ipai_ppm_a1` | Project/Portfolio | stable ✅ | 0 | 18.0.1.0.0 |
| `ipai_ppm_monthly_close` | Project Management | beta ⚠️ | 30 | 18.0.1.0.0 |
| `ipai_project_gantt` | Project | stable ✅ | 0 | 18.0.1.0.0 |
| `ipai_project_profitability_bridge` | Project | beta ⚠️ | 55 | 18.0.1.0.0 |
| `ipai_project_program` | Project | stable ✅ | 0 | 18.0.1.0.0 |
| `ipai_project_suite` | Project | beta ⚠️ | 25 | 18.0.1.0.0 |
| `ipai_srm` | Inventory/Purchase | stable ✅ | 5 | 18.0.1.0.0 |
| `ipai_studio_ai` | Customization/Studio | beta ⚠️ | 25 | 18.0.1.1.0 |
| `ipai_superset_connector` | Reporting/BI | beta ⚠️ | 25 | 18.0.1.0.0 |
| `ipai_test_fixtures` | Hidden/Tools | stable ✅ | 0 | 18.0.1.0.0 |
| `ipai_theme_fluent2` | Themes | stable ✅ | 0 | 18.0.1.0.0 |
| `ipai_v18_compat` | Technical | stable ✅ | 0 | 18.0.1.0.0 |
| `ipai_web_fluent2` | Themes/Backend | stable ✅ | 5 | 18.0.1.0.0 |
| `ipai_workspace_core` | InsightPulse/Core | beta ⚠️ | 25 | 18.0.1.0.0 |

---

_Generated by `scripts/generate_module_health_report.py`_