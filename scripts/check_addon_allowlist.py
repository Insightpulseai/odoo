#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Legacy Allowlist (Grandfathered modules)
# Any NEW module not in this list will fail the build if it's in addons/ipai/
ALLOWLIST = {
    "ipai_advisor", "ipai_agent_core", "ipai_ai_agents", "ipai_ai_agents_ui",
    "ipai_ai_audit", "ipai_ai_connectors", "ipai_ai_copilot", "ipai_ai_core",
    "ipai_ai_prompts", "ipai_ai_provider_kapa", "ipai_ai_provider_pulser",
    "ipai_ai_sources_odoo", "ipai_ai_studio", "ipai_aiux_chat", "ipai_approvals",
    "ipai_ask_ai", "ipai_ask_ai_bridge", "ipai_ask_ai_chatter", "ipai_assets",
    "ipai_auth_oauth_internal", "ipai_bi_superset", "ipai_bir_compliance",
    "ipai_catalog_bridge", "ipai_ce_branding", "ipai_ce_cleaner", "ipai_ces_bundle",
    "ipai_chatgpt_sdk_theme", "ipai_clarity_ppm_parity", "ipai_close_orchestration",
    "ipai_command_center", "ipai_control_room", "ipai_copilot_hub", "ipai_copilot_ui",
    "ipai_custom_routes", "ipai_default_home", "ipai_design_system_apps_sdk",
    "ipai_dev_studio_base", "ipai_document_ai", "ipai_enterprise_bridge",
    "ipai_equipment", "ipai_expense", "ipai_expense_ocr", "ipai_finance_bir_compliance",
    "ipai_finance_close_automation", "ipai_finance_close_seed", "ipai_finance_month_end",
    "ipai_finance_monthly_closing", "ipai_finance_ppm", "ipai_finance_ppm_closing",
    "ipai_finance_ppm_dashboard", "ipai_finance_ppm_tdi", "ipai_finance_project_hybrid",
    "ipai_focalboard_connector", "ipai_industry_accounting_firm", "ipai_industry_marketing_agency",
    "ipai_integrations", "ipai_marketing_ai", "ipai_marketing_journey", "ipai_master_control",
    "ipai_mattermost_connector", "ipai_mcp_hub", "ipai_module_gating", "ipai_n8n_connector",
    "ipai_ocr_expense", "ipai_platform_theme", "ipai_portal_fix", "ipai_ppm",
    "ipai_ppm_a1", "ipai_ppm_dashboard_canvas", "ipai_ppm_monthly_close",
    "ipai_project_gantt", "ipai_project_profitability_bridge", "ipai_project_program",
    "ipai_project_suite", "ipai_saas_tenant", "ipai_sample_metrics", "ipai_scout_bundle",
    "ipai_settings_dashboard", "ipai_skill_api", "ipai_srm", "ipai_studio_ai",
    "ipai_superset_connector", "ipai_tenant_core", "ipai_test_fixtures", "ipai_theme_aiux",
    "ipai_theme_copilot", "ipai_theme_fluent2", "ipai_theme_tbwa", "ipai_theme_tbwa_backend",
    "ipai_ui_brand_tokens", "ipai_v18_compat", "ipai_web_fluent2", "ipai_web_icons_fluent",
    "ipai_web_theme_tbwa", "ipai_workspace_core"
}

IPAI_ROOT = Path("addons/ipai")

def main():
    if not IPAI_ROOT.exists():
        print(f"Skipping: {IPAI_ROOT} does not exist.")
        return 0

    errors = []
    # List all subdirectories in addons/ipai/
    found_modules = [f.name for f in IPAI_ROOT.iterdir() if f.is_dir() and not f.name.startswith(".")]

    for mod in found_modules:
        if mod == 'scripts': continue # Ignore scripts directory
        if mod not in ALLOWLIST and mod != "ipai_enterprise_bridge":
            # Strict Policy Violation
            errors.append(f"❌ Policy Violation: '{mod}' is not in the Allowlist.")

    if errors:
        print("\n🚨 CRITICAL: New custom modules detected in addons/ipai/.")
        print("Policy: All new EE replacement logic must go into 'ipai_enterprise_bridge'.")
        print("See: addons/ipai/ipai_enterprise_bridge/POLICY.md")
        print("\nViolations:")
        for e in errors:
            print(e)
        sys.exit(1)

    print("✅ Allowlist Check Passed. No unauthorized modules found.")

if __name__ == "__main__":
    main()
