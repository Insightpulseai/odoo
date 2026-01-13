# Prod-Canonical Install Requirements

_Generated: 2026-01-13T23:28:26.794910Z_

## What exists in this repo (truth scan)

- Docker compose present: **True**
- Compose file: `docker-compose.yml`
- Custom addons detected: **321**
- Seed scripts detected: **2**

## Odoo modules implied (from custom addon manifests)

- `account`
- `analytic`
- `auth_oauth`
- `base`
- `calendar`
- `contacts`
- `crm`
- `disable_odoo_online`
- `hr`
- `hr_expense`
- `hr_timesheet`
- `ipai_agent_core`
- `ipai_ai_core`
- `ipai_ai_provider_pulser`
- `ipai_ask_ai`
- `ipai_design_system_apps_sdk`
- `ipai_dev_studio_base`
- `ipai_document_ai`
- `ipai_expense`
- `ipai_finance_close_seed`
- `ipai_finance_ppm`
- `ipai_integrations`
- `ipai_platform_audit`
- `ipai_platform_permissions`
- `ipai_platform_theme`
- `ipai_platform_workflow`
- `ipai_ppm_monthly_close`
- `ipai_project_program`
- `ipai_theme_aiux`
- `ipai_theme_fluent2`
- `ipai_ui_brand_tokens`
- `ipai_workos_blocks`
- `ipai_workos_canvas`
- `ipai_workos_collab`
- `ipai_workos_core`
- `ipai_workos_db`
- `ipai_workos_search`
- `ipai_workos_templates`
- `ipai_workos_views`
- `ipai_workspace_core`
- `mail`
- `maintenance`
- `mass_mailing`
- `portal`
- `project`
- `purchase`
- `remove_odoo_enterprise`
- `resource`
- `sale`
- `stock`
- `utm`
- `web`
- `website`

## Models touched by seed scripts (implied functional areas)

### `data/finance_seed/import_all.py`
- No models detected

### `data/finance_seed/update_tasks_after_import.py`
- No models detected

## Enterprise-only smell scan (heuristic)

- `documents` in `addons/ipai/ipai_agent_core/__manifest__.py`
- `documents` in `addons/ipai/ipai_ask_ai_chatter/__manifest__.py`
- `studio` in `addons/ipai/ipai_dev_studio_base/__manifest__.py`
- `documents` in `addons/ipai/ipai_dev_studio_base/__manifest__.py`
- `studio` in `addons/ipai/ipai_studio_ai/__manifest__.py`
- `documents` in `addons/ipai/ipai_document_ai/__manifest__.py`
- `studio` in `addons/ipai/ipai_ai_studio/__manifest__.py`
- `sign` in `addons/ipai_finance_ppm_golive/__manifest__.py`
- `documents` in `addons/ipai_ocr_gateway/__manifest__.py`
- `web_enterprise` in `addons/ipai_theme_tbwa_backend/__manifest__.py`

## Verification (CLI-only)

```bash
# when docker is up
docker compose up -d
docker ps

# Container names from actual scan:
# - odoo-core (port 8069)
# - odoo-dev (port 9069)
# - odoo-marketing (port 8070)
# - odoo-accounting (port 8071)

# run seed scripts (adjust container name and db)
# docker exec -i odoo-core odoo shell -d odoo_core < data/finance_seed/import_all.py
# docker exec -i odoo-core odoo shell -d odoo_core < data/finance_seed/update_tasks_after_import.py
```
