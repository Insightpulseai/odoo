# IPAI Module Suite - Technical Documentation

## Overview

The **IPAI (InsightPulse AI)** module suite is a comprehensive collection of 30 OCA-compliant Odoo 18 CE modules designed for enterprise financial management, project portfolio management, workspace collaboration, and operational governance.

**Repository**: `odoo-ce` (DigitalOcean deployment at erp.insightpulseai.net)
**Odoo Version**: 18.0 Community Edition
**OCA Compliance**: Full AGPL-3 compliance with OCA standards
**Total Modules**: 30 modules across 5 architectural layers

## Module Architecture Layers

### Finance Layer (14 modules)
Core financial operations, BIR tax compliance, month-end closing, and project portfolio management:

- **ipai_finance_ppm** - Finance Project Portfolio Management (Notion parity)
- **ipai_ppm_a1** - A1 Control Center (logframe + BIR schedule + task automation)
- **ipai_close_orchestration** - Close cycle orchestration engine
- **ipai_finance_bir_compliance** - BIR compliance (1601-C, 2550Q, 1702-RT, etc.)
- **ipai_finance_month_end** - Month-end closing templates and generators
- **ipai_finance_monthly_closing** - Monthly closing workflows
- **ipai_finance_ppm_closing** - PPM closing generator
- **ipai_finance_ppm_dashboard** - ECharts-based PPM dashboards
- **ipai_finance_ppm_tdi** - Transaction data ingestion for analytics
- **ipai_finance_project_hybrid** - Hybrid project/finance integration (IM1/IM2)
- **ipai_clarity_ppm_parity** - Clarity PPM feature parity
- **ipai_bir_compliance** - Tax Shield (Philippines)
- **ipai_ppm** - Portfolio & Program Management
- **ipai_ppm_monthly_close** - Monthly close scheduler

### WorkOS Layer (1 module)
Notion/AFFiNE-style workspace collaboration platform:

- **ipai_workspace_core** - Core workspace engine (blocks, pages, databases)

### Platform/Utilities Layer (2 modules)
Platform utilities and branding:

- **ipai_ce_branding** - InsightPulse AI branding customization
- **ipai_ce_cleaner** - CE cleaner (removes Enterprise/IAP dependencies)

### Industry Layer (2 modules)
Industry-specific configurations:

- **ipai_industry_accounting_firm** - Accounting firm operations
- **ipai_industry_marketing_agency** - Marketing agency operations

### Other/Operations Layer (11 modules)
Operational tools, asset management, and custom utilities:

- **ipai_advisor** - Azure Advisor-style recommendations engine
- **ipai_assets** - Equipment/asset checkout tracking (Cheqroom parity)
- **ipai_equipment** - Equipment management
- **ipai_expense** - Expense & Travel (PH tax rules)
- **ipai_master_control** - Work intake and master control
- **ipai_project_program** - Program + IM projects
- **ipai_srm** - Supplier Relationship Management
- **ipai_custom_routes** - Custom URL routing
- **ipai_default_home** - Default home page customization
- **ipai_dev_studio_base** - Dev studio base module
- **ipai_portal_fix** - Portal fixes for Odoo 18

## Quick Start

### Installation Order

**Critical**: Install modules in dependency order to avoid circular dependency errors.

```bash
# 1. Platform utilities (no dependencies)
odoo -d production -i ipai_ce_cleaner,ipai_ce_branding --stop-after-init

# 2. Core operations modules
odoo -d production -i ipai_advisor,ipai_assets,ipai_equipment --stop-after-init

# 3. Finance base modules
odoo -d production -i ipai_finance_ppm,ipai_bir_compliance --stop-after-init

# 4. Finance PPM stack
odoo -d production -i ipai_ppm_a1,ipai_close_orchestration,ipai_finance_bir_compliance --stop-after-init

# 5. Finance advanced (depends on PPM)
odoo -d production -i ipai_finance_month_end,ipai_finance_ppm_dashboard,ipai_finance_ppm_tdi --stop-after-init

# 6. WorkOS (optional - Notion parity)
odoo -d production -i ipai_workspace_core --stop-after-init

# 7. Industry modules (optional)
odoo -d production -i ipai_industry_accounting_firm,ipai_industry_marketing_agency --stop-after-init
```

See [INSTALLATION.md](./INSTALLATION.md) for detailed installation procedures, upgrade paths, and troubleshooting.

## Key Features

### Finance PPM & BIR Compliance
- **Automated BIR filing**: 1601-C, 2550Q, 1702-RT, 0619-E, 1601-EQ, 1601-FQ
- **Logframe tracking**: Goal → Outcome → IM1/IM2 → Outputs → Activities
- **Task automation**: Auto-create prep/review/approval tasks for each BIR form
- **ECharts dashboards**: Real-time KPI tracking with visual parity to Clarity PPM
- **Multi-employee support**: 8 employees tracked separately with role-based access

### Month-End Closing
- **W101 Snapshot**: 101-day look-back reporting
- **Template-driven**: Reusable templates for recurring closing tasks
- **Approval workflows**: Supervisor → Manager → Director gates
- **Mattermost integration**: n8n-powered deadline alerts and escalations

### Project Portfolio Management
- **Clarity PPM parity**: Feature-for-feature replication of Clarity PPM workflows
- **A1 Control Center**: Centralized control panel for finance operations
- **Close orchestration**: Multi-stage close cycle execution engine
- **Hybrid projects**: Finance + operations integration (IM1/IM2 logic)

### Operations & Governance
- **Ops Advisor**: Azure Advisor-style recommendations for operational improvements
- **Asset Management**: Cheqroom-parity equipment checkout and reservation system
- **SRM**: Supplier Relationship Management with approval workflows

## Documentation Structure

This documentation suite contains:

1. **[README.md](./README.md)** (this file) - Overview and quick start
2. **[INSTALLATION.md](./INSTALLATION.md)** - Installation procedures, upgrade paths, troubleshooting
3. **[ARCHITECTURE.md](./ARCHITECTURE.md)** - System architecture, data flow, integration points
4. **[SECURITY_MODEL.md](./SECURITY_MODEL.md)** - Security groups, access control, RLS policies
5. **[OPERATIONS_RUNBOOK.md](./OPERATIONS_RUNBOOK.md)** - Operational procedures, monitoring, backup/restore
6. **[CHANGELOG.md](./CHANGELOG.md)** - Version history and migration notes
7. **[modules/](./modules/)** - Per-module technical documentation (30 modules)

## Module Documentation

Each module has comprehensive technical documentation in `modules/<module_name>/README.md` covering:

- **Overview**: Purpose, users, capabilities
- **Dependencies**: Install order, Odoo/OCA/IPAI deps
- **Data Model**: Models, fields, relations, constraints
- **UI/Views**: Menus, actions, views, reports
- **Business Flows**: Step-by-step workflows
- **Security**: Groups, access control, record rules
- **Automation**: Cron jobs, server actions, webhooks
- **Configuration**: Settings, parameters, environment variables
- **API**: Controllers, RPC methods, integrations
- **Testing**: Verification procedures, demo data
- **Troubleshooting**: Common errors and fixes
- **File Map**: Directory structure and file descriptions

## Production Status

**Current Production Database**: `odoo` (159.223.75.148)

**Installed Modules** (as of 2025-12-26):
- ✅ ipai_finance_monthly_closing (Month-end workflows)
- ✅ ipai_finance_ppm (Finance PPM core)
- ✅ ipai_ocr_expense (OCR expense automation)
- ✅ ipai_ocr_webhook (OCR webhook handler)
- ✅ ipai_branding_cleaner (Branding cleanup)
- ✅ ipai_ce_cleaner (Enterprise dependency removal)

**Production Data** (as of 2025-12-26):
- **Invoices**: 9
- **Project Tasks**: 302
- **Expenses**: 24 (OCR-processed)
- **Bank Statements**: 1

**Safety Gates**: All finance modules safe to install - production database is finance-live with active transaction data.

## Support & Contributing

**Primary Maintainer**: Jake Tolentino (Finance SSC Manager / Odoo Developer)
**Organization**: InsightPulse AI (TBWA)
**Repository**: https://github.com/jgtolentino/odoo-ce
**Documentation Issues**: Open issue in GitHub repository

## License

All IPAI modules are licensed under **AGPL-3** in compliance with OCA standards.

## Next Steps

1. Review [INSTALLATION.md](./INSTALLATION.md) for installation procedures
2. Review [ARCHITECTURE.md](./ARCHITECTURE.md) for system design
3. Review [SECURITY_MODEL.md](./SECURITY_MODEL.md) for access control
4. Explore [modules/](./modules/) for per-module technical details
5. Review [OPERATIONS_RUNBOOK.md](./OPERATIONS_RUNBOOK.md) for operational procedures
