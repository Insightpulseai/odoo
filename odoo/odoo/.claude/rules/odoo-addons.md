---
paths:
  - "addons/**"
---

# Odoo Addons & Module Architecture

> Module philosophy, IPAI naming, module hierarchy, test coverage, addon paths.

---

## Module Philosophy

```
Config -> OCA -> Delta (ipai_*)
```

1. **Config**: Use Odoo's built-in configuration first
2. **OCA**: Use vetted OCA community modules second
3. **Delta**: Only create `ipai_*` modules for truly custom needs

## IPAI Module Naming Convention

All custom modules use the `ipai_` prefix organized by domain:

| Domain | Prefix Pattern | Examples |
|--------|---------------|----------|
| AI/Agents | `ipai_ai_*`, `ipai_agent_*` | `ipai_ai_core`, `ipai_ai_copilot`, `ipai_agent`, `ipai_ai_widget` |
| Finance | `ipai_finance_*` | `ipai_finance_ppm`, `ipai_finance_close_seed`, `ipai_finance_tax_return`, `ipai_finance_workflow` |
| Platform | `ipai_platform_*` | `ipai_platform_workflow`, `ipai_platform_audit`, `ipai_platform_approvals` |
| Workspace | `ipai_workspace_*` | `ipai_workspace_core` |
| Studio | `ipai_dev_studio_*`, `ipai_studio_*` | `ipai_dev_studio_base`, `ipai_studio_ai` |
| Industry | `ipai_industry_*` | `ipai_industry_marketing_agency`, `ipai_industry_accounting_firm` |
| WorkOS | `ipai_workos_*` | `ipai_workos_core`, `ipai_workos_blocks`, `ipai_workos_canvas` |
| Theme/UI | `ipai_theme_*`, `ipai_web_*`, `ipai_ui_*` | `ipai_theme_tbwa_backend`, `ipai_ui_brand_tokens` |
| Integrations | `ipai_*_connector` | `ipai_slack_connector`, `ipai_superset_connector`, `ipai_ops_connector`, `ipai_pulser_connector` |
| HR | `ipai_hr_*` | `ipai_hr_payroll_ph`, `ipai_hr_expense_liquidation` |
| BIR Compliance | `ipai_bir_*` | `ipai_bir_tax_compliance`, `ipai_bir_notifications`, `ipai_bir_plane_sync` |
| Mail | `ipai_mail_*`, `ipai_mailgun_*`, `ipai_zoho_*` | `ipai_mailgun_smtp`, `ipai_zoho_mail`, `ipai_mail_bridge_zoho` |
| Design | `ipai_design_*` | `ipai_design_system`, `ipai_design_system_apps_sdk` |
| LLM | `ipai_llm_*` | `ipai_llm_supabase_bridge` |

## Key Module Hierarchy (Verified 2026-03-08)

Based on actual `__manifest__.py` dependency analysis:

```
Layer 0 -- Independent (no IPAI deps, depend only on base Odoo):
  ipai_foundation              # Foundation layer (Live)
  ipai_ai_core                 # AI core framework (Live, has tests)
  ipai_ai_widget               # AI widget (Live, has tests)
  ipai_enterprise_bridge       # EE parity bridge (Live, has tests)
  ipai_finance_ppm             # Finance PPM (Live)
  ipai_helpdesk                # Helpdesk (Live)
  ipai_hr_expense_liquidation  # HR expense liquidation (Live, has tests)
  ipai_llm_supabase_bridge     # LLM Supabase bridge (Live, has tests)

Layer 1 -- Single IPAI dependency:
  ipai_ai_copilot              # -> ipai_ai_widget (Live)
  ipai_agent                   # -> ipai_hr_expense_liquidation (Live, has tests)

Layer 2 -- Multiple IPAI dependencies:
  ipai_workspace_core          # -> ipai_foundation + ipai_ai_copilot (Live, has tests, app=True)

Deprecated (installable: False):
  ipai_ai_agent_builder        # Migrated to ipai_enterprise_bridge
  ipai_ai_tools                # Migrated to ipai_enterprise_bridge
  ipai_ai_agents_ui            # Not installable (has tests)
```

## Test Coverage (8 of 69 modules have tests)

| Module | Test Files |
|--------|-----------|
| `ipai_ai_core` | `test_ai_core.py` |
| `ipai_ai_widget` | `test_ai_widget.py` |
| `ipai_agent` | `test_agent.py` |
| `ipai_enterprise_bridge` | `test_enterprise_bridge.py` |
| `ipai_hr_expense_liquidation` | `test_form_no.py`, `test_qweb.py` |
| `ipai_llm_supabase_bridge` | `test_install_smoke.py` |
| `ipai_workspace_core` | `test_workspace.py` |
| `ipai_ai_agents_ui` | `test_ai_agents_controller.py` (not installable) |

## Addon Path Conventions

- IPAI custom modules: `addons/ipai/<module_name>/`
- OCA modules: `addons/oca/*/` (NOT tracked, hydrated at runtime via gitaggregate)
- Legacy IPAI modules: `addons/ipai_*/` at addons root (legacy location)
- OCA submodule pins: `.gitmodules`
- Update OCA: `git submodule update --remote addons/oca/<repo>`

### OCA Rules

- Never modify OCA module source -- create an `ipai_*` override module instead
- Never copy OCA files into `addons/ipai/` -- use proper `_inherit` overrides
- OCA repos cloned under `addons/oca/*/` are NOT tracked (only keep base marker files per `.gitignore`)

---

*Last updated: 2026-03-16*
