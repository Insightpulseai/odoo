# OCA Module Installation from Allowlist

## Overview

This guide documents the installation of all 73 OCA modules defined in `config/oca/module_allowlist.yml`.

## Allowlist Summary

**Total Modules**: 73
**Install Packs**: 9 (foundation → web_ux → accounting_core → accounting_reconcile → accounting_statements → purchase_workflow → hr_modules → project_timesheet → crm_extensions → reporting)

### Module Breakdown by Pack

1. **foundation** (19 modules) - Server tools and base infrastructure
2. **web_ux** (7 modules) - Frontend improvements
3. **accounting_core** (8 modules) - Financial management base
4. **accounting_reconcile** (2 modules) - Reconciliation tools
5. **accounting_statements** (7 modules) - Bank statement processing
6. **purchase_workflow** (7 modules) - Procurement improvements
7. **hr_modules** (3 modules) - Human resources
8. **project_timesheet** (4 modules) - Project and timesheet management
9. **crm_extensions** (6 modules) - Sales pipeline improvements
10. **reporting** (6 modules) - Reports and exports

**Optional**:
- **documents** (1 module)
- **ai_pack** (3 modules - experimental)

## Installation Methods

### Method 1: Automated Installation (Recommended)

**Script**: `scripts/oca/install_from_allowlist.sh`

This script:
- Validates allowlist (no TODOs, all modules exist)
- Installs modules in dependency order (respects install_order)
- Provides detailed progress output
- Supports dry-run mode

#### Prerequisites

1. **Odoo server must be running**:
   ```bash
   # Check Odoo is running
   curl -s http://localhost:8069/web/health | grep "status"
   ```

2. **Python dependencies**:
   ```bash
   pip3 install pyyaml
   ```

3. **Environment variables** (optional):
   ```bash
   export ODOO_URL="http://localhost:8069"
   export ODOO_DB="odoo"
   export ODOO_USER="admin"
   export ODOO_PASS="admin"
   ```

#### Dry Run (Preview Install Plan)

```bash
./scripts/oca/install_from_allowlist.sh --dry-run
```

**Expected Output**:
```
Found 73 modules in 9 packs

Pack: foundation (19 modules)
  - base_exception
  - base_rest
  - base_rest_auth_api_key
  ... (16 more)

Pack: web_ux (7 modules)
  - web_dialog_size
  ... (6 more)

... (7 more packs)
```

#### Full Installation

```bash
./scripts/oca/install_from_allowlist.sh
```

**Expected Output**:
```
═══════════════════════════════════════════════════════════
   OCA Module Installation from Allowlist
═══════════════════════════════════════════════════════════

   Odoo URL: http://localhost:8069
   Database: odoo
   Allowlist: config/oca/module_allowlist.yml

Validating allowlist...
✓ No TODO placeholders found
✓ All 73 modules found in inventory

Found 73 modules in 9 packs

Connecting to Odoo...
Connected as user ID: 2

Checking module availability...
✓ Already installed: 0
○ To install: 73

Installing pack 'foundation': 19/19 modules
  Installing base_exception... ✓
  Installing base_rest... ✓
  ... (17 more)

Installing pack 'web_ux': 7/7 modules
  Installing web_dialog_size... ✓
  ... (6 more)

... (7 more packs)

═══════════════════════════════════════════════════════════
   Installation Summary
═══════════════════════════════════════════════════════════
  Already installed: 0
  Newly installed:   73
  Failed:            0
  Total modules:     73

✓ All modules installed successfully!
```

### Method 2: Manual Installation (Per Pack)

If automated installation fails, install pack-by-pack manually:

#### Pack 1: Foundation (19 modules)

```bash
odoo-bin -d odoo -i base_exception,base_rest,base_rest_auth_api_key,base_rest_pydantic,base_technical_features,base_technical_user,base_view_inheritance_extension,component,component_event,connector,extendable,extendable_fastapi,fastapi,fastapi_auth_api_key,fastapi_auth_jwt,pydantic,server_environment,server_environment_data_encryption,auditlog,date_range --stop-after-init
```

#### Pack 2: Web UX (7 modules)

```bash
odoo-bin -d odoo -i web_dialog_size,web_environment_ribbon,web_favicon,web_ir_actions_act_window_message,web_remember_tree_column_width,web_responsive,web_search_with_and --stop-after-init
```

#### Pack 3: Accounting Core (8 modules)

```bash
odoo-bin -d odoo -i account_financial_report,account_journal_restrict_mode,account_move_name_sequence,account_move_tier_validation,account_tax_balance,account_usability,account_reconcile_oca,account_reconcile_model_oca --stop-after-init
```

#### Pack 4: Accounting Reconcile (2 modules)

```bash
odoo-bin -d odoo -i account_reconcile_oca_add_default_filters,account_partner_reconcile --stop-after-init
```

#### Pack 5: Accounting Statements (7 modules)

```bash
odoo-bin -d odoo -i account_statement_base,account_statement_import_base,account_statement_import_file,account_statement_import_file_reconcile_oca,account_statement_import_camt,account_statement_import_camt54,account_statement_import_ofx --stop-after-init
```

#### Pack 6: Purchase Workflow (7 modules)

```bash
odoo-bin -d odoo -i purchase_advance_payment,purchase_exception,purchase_order_approval_block,purchase_order_line_sequence,purchase_tier_validation,purchase_request,purchase_request_tier_validation --stop-after-init
```

#### Pack 7: HR Modules (3 modules)

```bash
odoo-bin -d odoo -i hr_employee_firstname,hr_timesheet_task_stage,hr_timesheet_time_control --stop-after-init
```

#### Pack 8: Project Timesheet (4 modules)

```bash
odoo-bin -d odoo -i project_task_default_stage,project_task_stage_mgmt,project_task_stage_state,project_task_pull_request --stop-after-init
```

#### Pack 9: CRM Extensions (6 modules)

```bash
odoo-bin -d odoo -i crm_lead_code,crm_lead_currency,crm_lead_firstname,crm_industry,crm_phonecall,crm_stage_probability --stop-after-init
```

#### Pack 10: Reporting (6 modules)

```bash
odoo-bin -d odoo -i report_xlsx,report_xlsx_helper,report_xml,mis_builder,mis_builder_budget,partner_statement --stop-after-init
```

## Troubleshooting

### Module Not Found

**Error**: `✗ Not found: <module_name>`

**Cause**: Module not in addons path

**Fix**:
```bash
# Fetch missing OCA repositories
./scripts/oca/fetch_and_pin.sh

# Verify module exists
ls -la addons/oca/ | grep <module_name>
```

### Authentication Failed

**Error**: `ERROR: Authentication failed for user: admin`

**Fix**:
```bash
# Verify credentials
export ODOO_USER="admin"
export ODOO_PASS="<your-admin-password>"

# Or update database admin password
odoo-bin -d odoo -u base --stop-after-init
```

### Installation Timeout

**Error**: Installation hangs or times out

**Fix**:
```bash
# Increase timeout in script (add to XML-RPC calls)
# Or install smaller batches manually
```

### Dependency Conflicts

**Error**: Module dependencies not met

**Fix**:
```bash
# Install packs in order (foundation → web_ux → accounting_core → etc.)
# Do NOT skip packs
```

## Verification

After installation, verify all modules are installed:

```bash
./scripts/oca/install_from_allowlist.sh --dry-run
```

Expected output should show:
```
✓ Already installed: 73
○ To install: 0
```

## Next Steps

1. **Configure modules**: Set up module-specific configurations
2. **Update apps**: Navigate to Apps → Update Apps List
3. **Test functionality**: Verify each pack's features work
4. **Create backup**: Backup database after successful installation

## Evidence

- **Script**: `scripts/oca/install_from_allowlist.sh`
- **Allowlist**: `config/oca/module_allowlist.yml`
- **Validation**: `scripts/oca/clean_install_allowlist.sh`
