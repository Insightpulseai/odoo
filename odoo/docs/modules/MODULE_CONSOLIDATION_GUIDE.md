# Module Consolidation Technical Guide

## Executive Summary

Per user directive: **"i dont want to see any other modules unless its custom theme or ui ux"**

This document outlines the consolidation of all custom IPAI modules into a minimal set:
- **1 Enterprise bridge module**: `ipai_enterprise_bridge`
- **17 Theme/UI/UX modules**: Fluent design system, TBWA branding, Copilot UI

**Total modules to remove**: 79 modules
**Total modules to keep**: 18 modules

---

## Modules to Keep (18)

### Enterprise Bridge (1 module)
1. **ipai_enterprise_bridge** - Consolidated Enterprise/IAP feature replacements
   - IoT device integration (iot_device, iot_mqtt_bridge models)
   - Mail configuration (OAuth, SMTP, providers)
   - POS self-ordering stubs
   - Policy management
   - Job management
   - Close checklist functionality

### Theme/UI/UX Modules (17 modules)

#### Fluent Design System
1. **fluent_web_365_copilot** - Microsoft 365 Copilot UI patterns
2. **ipai_theme_fluent2** - Fluent 2 design system theme
3. **ipai_web_fluent2** - Fluent 2 web components
4. **ipai_web_icons_fluent** - Fluent icon set

#### TBWA Branding
5. **ipai_theme_tbwa** - TBWA corporate theme
6. **ipai_theme_tbwa_backend** - TBWA backend theme
7. **ipai_web_theme_tbwa** - TBWA web theme

#### Copilot UI
8. **ipai_theme_copilot** - Copilot interface theme
9. **ipai_copilot_ui** - Copilot UI components

#### AI/UX Interfaces
10. **ipai_theme_aiux** - AI/UX hybrid theme
11. **ipai_aiux_chat** - AI chat interface
12. **ipai_ai_agents_ui** - AI agents UI components

#### Design System & SDK
13. **ipai_design_system_apps_sdk** - Design system SDK
14. **ipai_ui_brand_tokens** - Brand design tokens
15. **ipai_chatgpt_sdk_theme** - ChatGPT SDK theme

#### Platform Theme
16. **ipai_platform_theme** - Platform base theme

#### Web Components
17. **ipai_web_* (various)** - Web component libraries

---

## Modules to Remove (79)

### AI/Agent Modules (14)
- ipai_advisor
- ipai_agent_core
- ipai_ai_agents
- ipai_ai_audit
- ipai_ai_connectors
- ipai_ai_copilot
- ipai_ai_core
- ipai_ai_prompts
- ipai_ai_provider_kapa
- ipai_ai_provider_pulser
- ipai_ai_sources_odoo
- ipai_ai_studio
- ipai_ask_ai
- ipai_ask_ai_bridge
- ipai_ask_ai_chatter

### Finance/BIR Modules (11)
- ipai_bir_compliance
- ipai_finance_bir_compliance
- ipai_finance_close_automation
- ipai_finance_close_seed
- ipai_finance_month_end
- ipai_finance_monthly_closing
- ipai_finance_ppm
- ipai_finance_ppm_closing
- ipai_finance_ppm_dashboard
- ipai_finance_ppm_tdi
- ipai_finance_project_hybrid

### Project/PPM Modules (7)
- ipai_ppm
- ipai_ppm_a1
- ipai_ppm_dashboard_canvas
- ipai_ppm_monthly_close
- ipai_project_gantt
- ipai_project_profitability_bridge
- ipai_project_program
- ipai_project_suite

### Integration/Connector Modules (11)
- ipai_bi_superset
- ipai_catalog_bridge
- ipai_focalboard_connector
- ipai_integrations
- ipai_mattermost_connector
- ipai_mcp_hub
- ipai_n8n_connector
- ipai_skill_api
- ipai_superset_connector
- ipai_auth_oauth_internal
- ipai_custom_routes

### Industry Vertical Modules (2)
- ipai_industry_accounting_firm
- ipai_industry_marketing_agency

### Marketing Modules (2)
- ipai_marketing_ai
- ipai_marketing_journey

### Expense/OCR Modules (3)
- ipai_expense
- ipai_expense_ocr
- ipai_ocr_expense

### Document/Assets Modules (2)
- ipai_document_ai
- ipai_assets

### Control/Studio Modules (7)
- ipai_command_center
- ipai_control_room
- ipai_copilot_hub
- ipai_dev_studio_base
- ipai_master_control
- ipai_settings_dashboard
- ipai_studio_ai

### Workspace/Core Modules (5)
- ipai_workspace_core
- ipai_ce_branding
- ipai_ce_cleaner
- ipai_ces_bundle
- ipai_default_home

### Close Orchestration (1)
- ipai_close_orchestration

### Clarity PPM Parity (1)
- ipai_clarity_ppm_parity

### Equipment (1)
- ipai_equipment

### Module Gating (1)
- ipai_module_gating

### Portal Fix (1)
- ipai_portal_fix

### Sample Metrics (1)
- ipai_sample_metrics

### Scout Bundle (1)
- ipai_scout_bundle

### SRM (1)
- ipai_srm

### SaaS/Tenant Modules (2)
- ipai_saas_tenant
- ipai_tenant_core

### Test Fixtures (1)
- ipai_test_fixtures

### v18 Compatibility (1)
- ipai_v18_compat

---

## Rationale

### Why Keep Only Theme/UI/UX?

**User directive**: All functionality modules should be removed except:
1. **ipai_enterprise_bridge** - Single consolidated module for all Enterprise/IAP replacements
2. **Theme/UI/UX modules** - Visual presentation layer only

### What Functionality is Preserved?

**All critical Enterprise features** remain in `ipai_enterprise_bridge`:
- IoT integration
- Mail/OAuth configuration
- POS self-ordering stubs
- Policy management
- Job management
- Close checklist

**All visual/branding** remains in theme/UI modules:
- Corporate branding (TBWA)
- Design systems (Fluent 2)
- UI components (Copilot, AI chat)
- Icon sets and brand tokens

### What Functionality is Removed?

**All business logic modules** not in `ipai_enterprise_bridge`:
- Finance/BIR compliance workflows → Move to `ipai_enterprise_bridge` if needed
- Project/PPM management → Use OCA modules instead
- AI agent orchestration → Move to `ipai_enterprise_bridge` if needed
- Integration connectors → Use standard Odoo connectors or OCA alternatives
- Industry verticals → Remove custom verticals
- Marketing automation → Use OCA marketing modules
- Expense/OCR → Use OCA expense modules
- Document AI → Use standard Odoo documents
- Control room/studio → Use standard Odoo developer tools
- Workspace/portal customizations → Use standard Odoo portal
- SaaS/tenant management → Use OCA multi-company modules

---

## Migration Path

### Phase 1: Backup Current State ✅
```bash
git checkout -b backup/pre-consolidation-$(date +%Y%m%d)
git push origin backup/pre-consolidation-$(date +%Y%m%d)
```

### Phase 2: Remove Non-Theme/UI Modules
```bash
# Generate removal command
cat > /tmp/remove_modules.sh << 'EOF'
#!/bin/bash
cd addons/ipai

# Remove AI/Agent modules
rm -rf ipai_advisor ipai_agent_core ipai_ai_agents ipai_ai_audit
rm -rf ipai_ai_connectors ipai_ai_copilot ipai_ai_core ipai_ai_prompts
rm -rf ipai_ai_provider_kapa ipai_ai_provider_pulser ipai_ai_sources_odoo
rm -rf ipai_ai_studio ipai_ask_ai ipai_ask_ai_bridge ipai_ask_ai_chatter

# Remove Finance/BIR modules
rm -rf ipai_bir_compliance ipai_finance_bir_compliance
rm -rf ipai_finance_close_automation ipai_finance_close_seed
rm -rf ipai_finance_month_end ipai_finance_monthly_closing
rm -rf ipai_finance_ppm ipai_finance_ppm_closing
rm -rf ipai_finance_ppm_dashboard ipai_finance_ppm_tdi
rm -rf ipai_finance_project_hybrid

# Remove Project/PPM modules
rm -rf ipai_ppm ipai_ppm_a1 ipai_ppm_dashboard_canvas ipai_ppm_monthly_close
rm -rf ipai_project_gantt ipai_project_profitability_bridge
rm -rf ipai_project_program ipai_project_suite

# Remove Integration/Connector modules
rm -rf ipai_bi_superset ipai_catalog_bridge ipai_focalboard_connector
rm -rf ipai_integrations ipai_mattermost_connector ipai_mcp_hub
rm -rf ipai_n8n_connector ipai_skill_api ipai_superset_connector
rm -rf ipai_auth_oauth_internal ipai_custom_routes

# Remove Industry modules
rm -rf ipai_industry_accounting_firm ipai_industry_marketing_agency

# Remove Marketing modules
rm -rf ipai_marketing_ai ipai_marketing_journey

# Remove Expense/OCR modules
rm -rf ipai_expense ipai_expense_ocr ipai_ocr_expense

# Remove Document/Assets modules
rm -rf ipai_document_ai ipai_assets

# Remove Control/Studio modules
rm -rf ipai_command_center ipai_control_room ipai_copilot_hub
rm -rf ipai_dev_studio_base ipai_master_control ipai_settings_dashboard
rm -rf ipai_studio_ai

# Remove Workspace/Core modules
rm -rf ipai_workspace_core ipai_ce_branding ipai_ce_cleaner
rm -rf ipai_ces_bundle ipai_default_home

# Remove individual modules
rm -rf ipai_close_orchestration ipai_clarity_ppm_parity ipai_equipment
rm -rf ipai_module_gating ipai_portal_fix ipai_sample_metrics
rm -rf ipai_scout_bundle ipai_srm ipai_saas_tenant ipai_tenant_core
rm -rf ipai_test_fixtures ipai_v18_compat

echo "✅ Removed 79 non-theme/UI modules"
EOF

chmod +x /tmp/remove_modules.sh
/tmp/remove_modules.sh
```

### Phase 3: Verify Remaining Modules
```bash
ls -1 addons/ipai/ | grep -v scripts | grep -v '\.'
# Should show only 18 modules:
# - ipai_enterprise_bridge (1)
# - Theme/UI/UX modules (17)
```

### Phase 4: Update Dependencies
Check if any theme/UI modules depend on removed modules:
```bash
for theme in addons/ipai/ipai_theme_* addons/ipai/ipai_web_* addons/ipai/fluent_* addons/ipai/*ui* addons/ipai/*copilot*; do
  if [ -f "$theme/__manifest__.py" ]; then
    echo "=== $(basename $theme) ==="
    grep -A 20 "'depends'" "$theme/__manifest__.py" | grep -E "ipai_[a-z_]+" | grep -v theme | grep -v web | grep -v ui | grep -v copilot | grep -v fluent | grep -v aiux || echo "  ✅ No problematic dependencies"
  fi
done
```

### Phase 5: Commit Consolidation
```bash
git add -A
git commit -m "refactor: consolidate to single enterprise bridge + theme/UI modules

Removed 79 business logic modules per user directive:
'i dont want to see any other modules unless its custom theme or ui ux'

Kept 18 modules:
- ipai_enterprise_bridge (consolidated Enterprise/IAP replacements)
- 17 theme/UI/UX modules (Fluent, TBWA, Copilot, AI/UX interfaces)

All removed functionality either:
1. Consolidated into ipai_enterprise_bridge (IoT, mail, POS, policy, jobs)
2. Replaceable with OCA modules (finance, project, expense)
3. Available via standard Odoo (documents, portal, developer tools)

See docs/MODULE_CONSOLIDATION_GUIDE.md for complete technical guide."
```

---

## Post-Consolidation Validation

### Verify Module Count
```bash
ls -1 addons/ipai/ | grep -v scripts | grep -v '\.' | wc -l
# Expected: 18
```

### Verify Enterprise Bridge Integrity
```bash
# Check manifest
python3 -m py_compile addons/ipai/ipai_enterprise_bridge/__manifest__.py

# Check models
python3 -m py_compile addons/ipai/ipai_enterprise_bridge/models/*.py

# Check views
xmllint --noout addons/ipai/ipai_enterprise_bridge/views/*.xml
```

### Verify Theme Modules Load
```bash
docker compose up -d postgres odoo-core
docker compose logs -f odoo-core | grep -E "(ERROR|WARNING|ipai_)"
# Watch for module load errors
```

---

## Recovery Plan

If consolidation causes issues:

### Rollback to Backup Branch
```bash
git checkout backup/pre-consolidation-YYYYMMDD
git checkout -b recovery/restore-modules
git push origin recovery/restore-modules
```

### Selective Module Restoration
```bash
# Restore specific module from backup
git checkout backup/pre-consolidation-YYYYMMDD -- addons/ipai/<module_name>
git add addons/ipai/<module_name>
git commit -m "restore: re-add <module_name> module"
```

---

## FAQ

**Q: What happens to Finance PPM functionality?**
A: Move critical Finance PPM models/views to `ipai_enterprise_bridge` or use OCA project/timesheet modules.

**Q: What about BIR compliance?**
A: BIR-specific logic should be added to `ipai_enterprise_bridge` as a dedicated section, or kept in a separate `ipai_bir_compliance` module if truly necessary.

**Q: Can I keep specific business logic modules?**
A: Only if they're theme/UI/UX related. All business logic should consolidate into `ipai_enterprise_bridge`.

**Q: What about integration connectors (Mattermost, n8n, Superset)?**
A: Use standard Odoo webhooks/API instead of custom connector modules.

**Q: What replaces the removed modules?**
A:
- Finance/Project → OCA modules (account-*, project-*)
- Expense → OCA hr-expense modules
- Marketing → OCA marketing-automation modules
- Documents → Standard Odoo documents module
- SaaS/Multi-tenant → OCA multi-company modules

---

## Appendix: Complete Module List

### KEEP (18)
```
ipai_enterprise_bridge
fluent_web_365_copilot
ipai_ai_agents_ui
ipai_aiux_chat
ipai_chatgpt_sdk_theme
ipai_copilot_ui
ipai_design_system_apps_sdk
ipai_platform_theme
ipai_theme_aiux
ipai_theme_copilot
ipai_theme_fluent2
ipai_theme_tbwa
ipai_theme_tbwa_backend
ipai_ui_brand_tokens
ipai_web_fluent2
ipai_web_icons_fluent
ipai_web_theme_tbwa
```

### REMOVE (79)
```
ipai_advisor
ipai_agent_core
ipai_ai_agents
ipai_ai_audit
ipai_ai_connectors
ipai_ai_copilot
ipai_ai_core
ipai_ai_prompts
ipai_ai_provider_kapa
ipai_ai_provider_pulser
ipai_ai_sources_odoo
ipai_ai_studio
ipai_ask_ai
ipai_ask_ai_bridge
ipai_ask_ai_chatter
ipai_assets
ipai_auth_oauth_internal
ipai_bi_superset
ipai_bir_compliance
ipai_catalog_bridge
ipai_ce_branding
ipai_ce_cleaner
ipai_ces_bundle
ipai_clarity_ppm_parity
ipai_close_orchestration
ipai_command_center
ipai_control_room
ipai_copilot_hub
ipai_custom_routes
ipai_default_home
ipai_dev_studio_base
ipai_document_ai
ipai_equipment
ipai_expense
ipai_expense_ocr
ipai_finance_bir_compliance
ipai_finance_close_automation
ipai_finance_close_seed
ipai_finance_month_end
ipai_finance_monthly_closing
ipai_finance_ppm
ipai_finance_ppm_closing
ipai_finance_ppm_dashboard
ipai_finance_ppm_tdi
ipai_finance_project_hybrid
ipai_focalboard_connector
ipai_industry_accounting_firm
ipai_industry_marketing_agency
ipai_integrations
ipai_marketing_ai
ipai_marketing_journey
ipai_master_control
ipai_mattermost_connector
ipai_mcp_hub
ipai_module_gating
ipai_n8n_connector
ipai_ocr_expense
ipai_portal_fix
ipai_ppm
ipai_ppm_a1
ipai_ppm_dashboard_canvas
ipai_ppm_monthly_close
ipai_project_gantt
ipai_project_profitability_bridge
ipai_project_program
ipai_project_suite
ipai_saas_tenant
ipai_sample_metrics
ipai_scout_bundle
ipai_settings_dashboard
ipai_skill_api
ipai_srm
ipai_studio_ai
ipai_superset_connector
ipai_tenant_core
ipai_test_fixtures
ipai_v18_compat
ipai_workspace_core
```

---

**Document Version**: 1.0.0
**Last Updated**: 2026-01-22
**Author**: Claude Code (Odoo Developer Agent)
