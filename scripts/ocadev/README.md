# OCA/ipai Full Stack Installer

Idempotent scripts to install all CE + OCA + ipai modules in one shot.

## Quick Start

```bash
# 1. Ensure Docker daemon is running
# 2. Run installer
./scripts/ocadev/install_oca_ipai_full.sh

# 3. Verify installation
./scripts/ocadev/list_installed_modules.sh
```

## Scripts

### `install_oca_ipai_full.sh`

Idempotent installer that:
1. Starts Odoo stack (if not running)
2. Creates fresh DB with `base` module
3. Installs all 38 ipai_* modules
4. Installs core OCA modules (queue, web, reporting, accounting)

**Environment Variables**:
```bash
ODOO_DB=ipai_oca_full              # Database name
ODOO_COMPOSE_FILE=docker/docker-compose.ce19.yml  # Compose file path
ODOO_SERVICE=odoo                   # Service name in compose
OCA_MODULES="queue_job,mass_editing,..."  # OCA modules to install
```

**Usage**:
```bash
# Default (CE19, service 'odoo', DB 'ipai_oca_full')
./scripts/ocadev/install_oca_ipai_full.sh

# Custom DB name
ODOO_DB=ipai_dev ./scripts/ocadev/install_oca_ipai_full.sh

# Custom compose file (CE18)
ODOO_COMPOSE_FILE=docker/docker-compose.ce18.yml \
ODOO_SERVICE=odoo-core \
./scripts/ocadev/install_oca_ipai_full.sh
```

### `list_installed_modules.sh`

Lists all installed modules from `ir_module_module` table.

**Usage**:
```bash
# Default DB
./scripts/ocadev/list_installed_modules.sh

# Custom DB
ODOO_DB=ipai_dev ./scripts/ocadev/list_installed_modules.sh
```

## Module Summary

### CE Core
Standard Odoo 18 modules (account, sale, purchase, stock, project, hr, crm)

### OCA Modules (80+ available, 15 core installed by default)
- **Queue**: queue_job, queue_job_cron_jobrunner
- **Server Tools**: mass_editing, auditlog, base_tier_validation
- **Web**: web_responsive, web_m2x_options, web_export_view
- **Reporting**: report_xlsx, report_xlsx_helper
- **Accounting**: account_asset_management, account_financial_report, account_reconcile
- **Bank**: account_bank_statement_import, account_move_base_import

### ipai Custom Modules (38 modules)
- **AI & Agents**: 9 modules (agent_builder, ai_fields, ai_rag, copilot_ui, etc.)
- **Finance**: 5 modules (finance_ppm, expense_ocr, hr_payroll_ph, tax_return, workflow)
- **Design System**: 10 modules (themes, brand tokens, Fluent2, TBWA theme)
- **ESG**: 3 modules (esg, esg_social, equity)
- **Business Apps**: 5 modules (helpdesk, planning, project_templates, sign, whatsapp)
- **Verticals**: 2 modules (vertical_media, vertical_retail)
- **Infrastructure**: 4 modules (enterprise_bridge, foundation, design_system, documents_ai)

## Troubleshooting

### Docker daemon not running
```bash
# macOS (Colima)
colima start

# Linux
sudo systemctl start docker
```

### Permission errors
```bash
# Run from repo root
cd ~/Documents/GitHub/odoo-ce
./scripts/ocadev/install_oca_ipai_full.sh
```

### Module not found
Check that OCA repos are cloned:
```bash
find addons/oca -maxdepth 1 -type d | wc -l
# Should show 27+ directories
```

### Database connection errors
Verify PostgreSQL service is running:
```bash
docker compose -f docker/docker-compose.ce19.yml ps
```

## Rollback

### Drop database and start fresh
```bash
# Option 1: Create new DB with different name
ODOO_DB=ipai_oca_full_v2 ./scripts/ocadev/install_oca_ipai_full.sh

# Option 2: Drop via psql (if accessible)
docker compose -f docker/docker-compose.ce19.yml exec postgres \
  psql -U odoo -c "DROP DATABASE ipai_oca_full;"
```

## Deployment Patterns

### Development
```bash
ODOO_DB=ipai_dev ./scripts/ocadev/install_oca_ipai_full.sh
```

### Staging
```bash
ODOO_DB=ipai_staging \
ODOO_COMPOSE_FILE=deploy/docker-compose.staging.yml \
./scripts/ocadev/install_oca_ipai_full.sh
```

### Production (manual approval required)
```bash
# DO NOT run in production without testing in dev/staging first
ODOO_DB=ipai_prod \
ODOO_COMPOSE_FILE=deploy/docker-compose.prod.yml \
./scripts/ocadev/install_oca_ipai_full.sh
```

## Integration with Spec Kit

This installer implements:
- **T1.1** from `spec/ipai-odoo-devops-agent/tasks.md` - Clone missing OCA repos
- **T1.2** - Verify OCA/ipai layout
- **T2.1** - Database setup and module installation

Part of the IPAI Odoo DevOps Agent automation stack.
