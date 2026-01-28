# Addons Manifest System

**Purpose**: Machine-readable, authoritative placement for OCA and ipai addons in the odoo-ce repository.

## Two-Tier Manifest System

### 1. Mount Validation (`addons.manifest.json`)

**Location**: Repository root
**Purpose**: Devcontainer mount declarations and CI validation
**Scope**: Currently configured mounts for active development

**Usage**:
```bash
# Validate current mount configuration
./scripts/verify-addons-mounts.sh --verbose

# CI validation runs automatically on push/PR
```

**Contents**:
- Odoo version (18.0)
- Source directories (oca, ipai)
- Mount declarations with priorities
- Validation rules
- Last validation timestamp

### 2. OCA/ipai Comprehensive Manifest (`config/addons_manifest.oca_ipai.json`)

**Location**: `config/addons_manifest.oca_ipai.json`
**Purpose**: Complete OCA repository catalog and must-have module lists
**Scope**: All OCA repos required for EE parity (19 repos, 80+ priority modules)

**Usage**:
```bash
# Verify filesystem placement against manifest
./scripts/verify_oca_ipai_layout.sh

# Clone missing OCA repositories
./scripts/clone_missing_oca_repos.sh
```

**Contents**:
- 19 OCA repository definitions (name, url, path, purpose)
- Must-have module lists per repository (80+ modules)
- ipai custom addon root declaration

## OCA Repository Catalog (19 repos)

| Repository | Purpose | Priority Modules |
|------------|---------|------------------|
| **ai** | AI/LLM integration | (new, to be populated) |
| **automation** | Automation tools | (varies by use case) |
| **queue** | Async job queue | `queue_job`, `queue_job_cron_jobrunner` |
| **connector** | Generic connector framework | (framework, no direct modules) |
| **rest-framework** | REST API + OpenAPI | (framework for API development) |
| **server-tools** | Admin tools, exceptions, tiers | `mass_editing`, `auditlog`, `base_tier_validation` (8 modules) |
| **server-env** | Environment-dependent config | `server_environment`, `server_environment_files` |
| **server-ux** | Server UX helpers | `base_tier_validation_formula`, `date_range` (3 modules) |
| **web** | Web UI extensions | `web_m2x_options`, `web_responsive` (7 modules) |
| **reporting-engine** | Reporting helpers | `report_xlsx`, `report_xlsx_helper` (4 modules) |
| **account-financial-reporting** | GL/TB/Open items | `account_financial_report` (2 modules) |
| **account-financial-tools** | Assets, fiscal year | `account_asset_management`, `account_fiscal_year` (4 modules) |
| **account-reconcile** | Bank reconciliation | `account_reconcile_oca`, `base_transaction_id` (4 modules) |
| **bank-statement-import** | Bank import (OFX/CAMT) | `account_statement_import_ofx` (4 modules) |
| **account-invoicing** | Invoice tools | `account_invoice_refund_link`, `account_invoice_merge` (3 modules) |
| **sale-workflow** | Advanced sales | `sale_order_type`, `sale_tier_validation` (13 modules) |
| **purchase-workflow** | Advanced purchase | `purchase_tier_validation`, `purchase_request` (5 modules) |
| **partner-contact** | Partner extensions | `partner_firstname`, `partner_company_group` (5 modules) |
| **crm** | CRM extensions | `crm_stage_probability`, `crm_lead_firstname` (2 modules) |

**Total**: 80+ must-have modules across 19 repositories for EE parity.

## Must-Have Module Summary

### Server Administration (11 modules)
- `mass_editing` - Batch record editing
- `auditlog` - Comprehensive audit logging
- `auth_admin_passkey` - Admin emergency access
- `base_exception` - Exception handling framework
- `base_tier_validation` - Multi-tier approval workflows
- `scheduler_error_mailer` - Cron failure notifications
- `base_technical_user` - Technical user management
- `base_cron_exclusion` - Cron job exclusion
- `base_tier_validation_formula` - Formula-based approvals
- `base_tier_validation_forward` - Approval delegation
- `date_range` - Date range management

### Web UI (7 modules)
- `web_m2x_options` - Many2many/many2one enhancements
- `web_export_view` - Export list views
- `web_tree_many2one_clickable` - Clickable tree relations
- `web_responsive` - Mobile-responsive UI
- `web_no_bubble` - Prevent field bubbling
- `web_refresher` - Auto-refresh views
- `web_ir_actions_act_multi` - Multi-record actions

### Reporting (4 modules)
- `report_xlsx` - Excel report generation
- `report_xlsx_helper` - XLSX report utilities
- `report_qweb_pdf_watermark` - PDF watermarking
- `report_qweb_parameter` - Parameterized reports

### Queue & Background Jobs (2 modules)
- `queue_job` - Asynchronous job queue
- `queue_job_cron_jobrunner` - Cron-based job execution

### Accounting & Finance (18 modules)
- **Financial Reporting**: `account_financial_report`, `account_financial_report_qweb`
- **Reconciliation**: `account_reconcile_oca`, `account_reconcile_oca_queue`, `account_statement_base`, `base_transaction_id`
- **Bank Import**: `account_statement_import`, `account_statement_import_ofx`, `account_statement_import_camt`, `account_statement_import_mt940`
- **Invoicing**: `account_invoice_refund_link`, `account_invoice_merge`, `account_invoice_check_total`
- **Financial Tools**: `account_asset_management`, `account_fiscal_year`, `account_lock_date_update`, `account_move_name_sequence`

### Sales Workflow (13 modules)
- `sale_order_type` - Order type classification
- `sale_tier_validation` - Sales approval workflows
- `sale_order_line_sequence` - Line sequencing
- `sale_fixed_discount` - Fixed discounts
- `sale_order_line_date` - Line-level dates
- `sale_elaboration` - Order elaboration
- `sale_order_invoicing_finished_task` - Task-based invoicing
- `sale_exception` - Sales exceptions
- `sale_order_revision` - Order revisions
- `sale_blanket_order` - Blanket orders
- `sale_order_archive` - Order archiving
- `sale_delivery_block` - Delivery blocking
- `sale_invoice_block` - Invoice blocking

### Purchase Workflow (5 modules)
- `purchase_tier_validation` - Purchase approvals
- `purchase_order_line_sequence` - Line sequencing
- `purchase_exception` - Purchase exceptions
- `purchase_request` - Purchase requisitions
- `purchase_blanket_order` - Blanket orders

### Partner/Contact (5 modules)
- `partner_firstname` - First/last name split
- `partner_contact_birthdate` - Birthdate tracking
- `partner_contact_gender` - Gender field
- `partner_contact_job_position` - Job positions
- `partner_company_group` - Company grouping

### CRM (2 modules)
- `crm_stage_probability` - Stage-based probability
- `crm_lead_firstname` - Lead name management

## Filesystem Layout

```
odoo-ce/
├── addons/
│   ├── oca/                    # OCA repositories (19 repos)
│   │   ├── ai/
│   │   ├── automation/
│   │   ├── queue/
│   │   ├── connector/
│   │   ├── rest-framework/
│   │   ├── server-tools/
│   │   ├── server-env/
│   │   ├── server-ux/
│   │   ├── web/
│   │   ├── reporting-engine/
│   │   ├── account-financial-reporting/
│   │   ├── account-financial-tools/
│   │   ├── account-reconcile/
│   │   ├── bank-statement-import/
│   │   ├── account-invoicing/
│   │   ├── sale-workflow/
│   │   ├── purchase-workflow/
│   │   ├── partner-contact/
│   │   └── crm/
│   └── ipai/                   # ipai custom modules (38+ modules)
│       └── ipai_*/
│
├── config/
│   ├── addons_manifest.oca_ipai.json   # Comprehensive OCA/ipai catalog
│   └── README_ADDONS_MANIFEST.md       # This file
│
├── scripts/
│   ├── verify-addons-mounts.sh         # Mount validation
│   ├── verify_oca_ipai_layout.sh       # OCA/ipai layout verification
│   └── clone_missing_oca_repos.sh      # Clone missing OCA repos
│
└── addons.manifest.json                # Mount declarations + validation
```

## Workflows

### Initial Setup (Clone OCA Repos)

```bash
# 1. Verify current state
./scripts/verify_oca_ipai_layout.sh

# 2. Clone missing OCA repositories (uses branch 18.0)
./scripts/clone_missing_oca_repos.sh

# 3. Verify all repos cloned
./scripts/verify_oca_ipai_layout.sh

# 4. Validate mounts for devcontainer
./scripts/verify-addons-mounts.sh --verbose
```

### Development Workflow

```bash
# Before starting work: Validate environment
./scripts/verify-addons-mounts.sh

# During development: Check OCA repo status
./scripts/verify_oca_ipai_layout.sh

# Before commit: Run validation
./scripts/verify-addons-mounts.sh --ci
```

### CI/CD Integration

**Automated validation runs on**:
- Push to main/develop branches
- PRs modifying addons/, manifests, or devcontainer config
- Manual workflow dispatch

**Validation steps**:
1. Manifest JSON syntax validation
2. Source directory existence check
3. Mount path validation with module counting
4. DevContainer mount configuration check
5. OCA lock file validation

## Module Installation (Future)

The manifest declares **desired modules**, not installed state. To install must-have modules:

```bash
# (Future script - not yet implemented)
# ./scripts/install_oca_must_have_modules.sh

# Manual installation via Odoo CLI:
odoo -d odoo_core -u module_name1,module_name2 --stop-after-init
```

## Maintenance

### Adding New OCA Repository

1. Edit `config/addons_manifest.oca_ipai.json`:
   ```json
   {
     "name": "new-repo",
     "type": "git",
     "url": "https://github.com/OCA/new-repo.git",
     "path": "addons/oca/new-repo",
     "purpose": "Description"
   }
   ```

2. Clone the repository:
   ```bash
   ./scripts/clone_missing_oca_repos.sh
   ```

3. Update `addons.manifest.json` if mount needed:
   ```json
   {
     "name": "OCA New Repo",
     "source": "./addons/oca/new-repo",
     "priority": 2,
     "required": false
   }
   ```

4. Update `.devcontainer/devcontainer.json` mounts if needed.

### Updating Must-Have Module Lists

Edit `config/addons_manifest.oca_ipai.json` under `oca_must_have_modules`:

```json
"server-tools": [
  "mass_editing",
  "auditlog",
  "new_module_name"
]
```

## References

- **Mount Validation**: `addons.manifest.json`
- **OCA Catalog**: `config/addons_manifest.oca_ipai.json`
- **Verification Scripts**: `scripts/verify_*.sh`
- **CI Workflow**: `.github/workflows/validate-addons-mounts.yml`
