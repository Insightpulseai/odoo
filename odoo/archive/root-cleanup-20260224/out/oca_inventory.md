# OCA Module Inventory for EE→CE+OCA Migration

**Target Version:** Odoo 19.0 CE
**Generated:** 2026-01-27
**Purpose:** Curated, proven OCA modules for replacing Enterprise-only features

---

## Maturity Criteria

| Level | Description |
|-------|-------------|
| **proven** | Active maintenance, >100 stars, regular commits, OCA-certified, multi-version support |
| **stable** | Released for target version, passing CI, no critical issues |
| **experimental** | Ported but limited testing, may have edge cases |

---

## Tier 0: Foundation

### server-tools
**URL:** https://github.com/OCA/server-tools
**Maturity:** proven | **Stars:** ~1200

| Module | Purpose | Replaces EE | License | Risk |
|--------|---------|-------------|---------|------|
| `base_exception` | Exception management framework | - | AGPL-3 | None |
| `base_technical_user` | Technical user for automation | - | AGPL-3 | None |
| `auditlog` | Audit trail for model changes | data_recycle (partial) | AGPL-3 | Performance on high-volume |
| `base_cron_exclusion` | Prevent concurrent cron | - | AGPL-3 | None |
| `module_auto_update` | Auto-detect changed modules | - | LGPL-3 | Caution in production |
| `base_view_inheritance_extension` | Enhanced xpath | - | LGPL-3 | None |

### server-ux
**URL:** https://github.com/OCA/server-ux
**Maturity:** proven | **Stars:** ~400

| Module | Purpose | Replaces EE | License | Risk |
|--------|---------|-------------|---------|------|
| `date_range` | Reusable date ranges | - | AGPL-3 | None - essential |
| `date_range_account` | Accounting date ranges | - | AGPL-3 | None |
| `base_tier_validation` | Multi-level approvals | approvals (partial) | AGPL-3 | None - recommended |
| `base_tier_validation_formula` | Formula-based rules | approvals | AGPL-3 | None |
| `server_action_mass_edit` | Mass edit records | - | AGPL-3 | None |

### server-backend
**URL:** https://github.com/OCA/server-backend
**Maturity:** proven | **Stars:** ~300

| Module | Purpose | Replaces EE | License | Risk |
|--------|---------|-------------|---------|------|
| `base_user_role` | Role-based access | - | AGPL-3 | None |
| `base_user_role_company` | Company-specific roles | - | AGPL-3 | None |

---

## Tier 1: Platform UX

### web
**URL:** https://github.com/OCA/web
**Maturity:** proven | **Stars:** ~900

| Module | Purpose | Replaces EE | License | Risk |
|--------|---------|-------------|---------|------|
| `web_responsive` | Mobile-responsive backend | - | LGPL-3 | None - highly recommended |
| `web_refresher` | Auto-refresh views | - | AGPL-3 | None |
| `web_dialog_size` | Resizable dialogs | - | LGPL-3 | None |
| `web_advanced_search` | Advanced search operators | - | AGPL-3 | None |
| `web_m2x_options` | M2O/M2M field options | - | AGPL-3 | None |
| `web_widget_x2many_2d_matrix` | 2D matrix widget | - | AGPL-3 | None |
| `web_tree_many2one_clickable` | Clickable M2O in trees | - | AGPL-3 | None |

---

## Tier 2: Background Processing

### queue
**URL:** https://github.com/OCA/queue
**Maturity:** proven | **Stars:** ~300

| Module | Purpose | Replaces EE | License | Risk |
|--------|---------|-------------|---------|------|
| `queue_job` | Background job framework | - | LGPL-3 | Requires jobrunner |
| `queue_job_cron` | Cron-based execution | - | LGPL-3 | None |

---

## Tier 4: Reporting & BI

### reporting-engine
**URL:** https://github.com/OCA/reporting-engine
**Maturity:** proven | **Stars:** ~500

| Module | Purpose | Replaces EE | License | Risk |
|--------|---------|-------------|---------|------|
| `report_xlsx` | XLSX report generation | - | AGPL-3 | None - essential |
| `report_xlsx_helper` | XLSX helper utilities | - | AGPL-3 | None |
| `bi_sql_editor` | SQL-based BI reports | spreadsheet (partial) | AGPL-3 | SQL injection risk |
| `sql_export` | Export SQL results | - | AGPL-3 | None |
| `sql_export_excel` | SQL to Excel export | - | AGPL-3 | None |
| `kpi_dashboard` | KPI dashboard builder | spreadsheet (partial) | AGPL-3 | None |
| `report_csv` | CSV report generation | - | AGPL-3 | None |

### mis-builder
**URL:** https://github.com/OCA/mis-builder
**Maturity:** proven | **Stars:** ~400

| Module | Purpose | Replaces EE | License | Risk |
|--------|---------|-------------|---------|------|
| `mis_builder` | P&L, Balance Sheet, KPI reports | accounting_reports (partial) | AGPL-3 | None - excellent |
| `mis_builder_budget` | Budget management | account_budget | AGPL-3 | None |

### account-financial-reporting
**URL:** https://github.com/OCA/account-financial-reporting
**Maturity:** proven | **Stars:** ~600

| Module | Purpose | Replaces EE | License | Risk |
|--------|---------|-------------|---------|------|
| `account_financial_report` | GL, Trial Balance, Partner Ledger | accounting_reports | AGPL-3 | None - essential |

### account-financial-tools
**URL:** https://github.com/OCA/account-financial-tools
**Maturity:** proven | **Stars:** ~400

| Module | Purpose | Replaces EE | License | Risk |
|--------|---------|-------------|---------|------|
| `account_lock_date` | Lock accounting periods | - | AGPL-3 | None |
| `account_fiscal_year` | Fiscal year management | - | AGPL-3 | None |
| `account_move_name_sequence` | Custom move sequences | - | AGPL-3 | None |
| `account_journal_lock_date` | Per-journal lock dates | - | AGPL-3 | None |

---

## Tier 5: Spreadsheet

### spreadsheet
**URL:** https://github.com/OCA/spreadsheet
**Maturity:** stable | **Stars:** ~100

| Module | Purpose | Replaces EE | License | Risk |
|--------|---------|-------------|---------|------|
| `spreadsheet_oca` | CE spreadsheet | spreadsheet | LGPL-3 | May lack some EE features |
| `spreadsheet_dashboard_oca` | Spreadsheet dashboards | spreadsheet_dashboard | LGPL-3 | May lack some EE features |

---

## Tier 6: Documents & Knowledge

### dms
**URL:** https://github.com/OCA/dms
**Maturity:** proven | **Stars:** ~300

| Module | Purpose | Replaces EE | License | Risk |
|--------|---------|-------------|---------|------|
| `dms` | Full document management | documents | LGPL-3 | None - excellent |
| `dms_field` | DMS field widget | documents | LGPL-3 | None |

### knowledge
**URL:** https://github.com/OCA/knowledge
**Maturity:** proven | **Stars:** ~200

| Module | Purpose | Replaces EE | License | Risk |
|--------|---------|-------------|---------|------|
| `document_page` | Internal wiki | knowledge (partial) | AGPL-3 | None |
| `document_page_approval` | Document approval workflow | knowledge | AGPL-3 | None |

---

## Tier 7: API Layer

### rest-framework
**URL:** https://github.com/OCA/rest-framework
**Maturity:** proven | **Stars:** ~300

| Module | Purpose | Replaces EE | License | Risk |
|--------|---------|-------------|---------|------|
| `base_rest` | REST API framework | - | LGPL-3 | None |
| `base_rest_pydantic` | Pydantic integration | - | LGPL-3 | None |
| `graphql_base` | GraphQL API support | - | LGPL-3 | None |

---

## Tier 8: Communication

### social
**URL:** https://github.com/OCA/social
**Maturity:** proven | **Stars:** ~400

| Module | Purpose | Replaces EE | License | Risk |
|--------|---------|-------------|---------|------|
| `mail_activity_board` | Activity management board | - | AGPL-3 | None |
| `mail_tracking` | Email tracking | marketing_automation (partial) | AGPL-3 | None |
| `mail_debrand` | Remove Odoo branding | - | AGPL-3 | None |

---

## Tier 9: Workflow Extensions

### purchase-workflow
**URL:** https://github.com/OCA/purchase-workflow
**Maturity:** proven | **Stars:** ~300

| Module | Purpose | Replaces EE | License | Risk |
|--------|---------|-------------|---------|------|
| `purchase_request` | Purchase request workflow | - | LGPL-3 | None |
| `purchase_order_approval_block` | PO approval blocking | approvals (partial) | AGPL-3 | None |
| `purchase_order_type` | Purchase order types | - | AGPL-3 | None |

### sale-workflow
**URL:** https://github.com/OCA/sale-workflow
**Maturity:** proven | **Stars:** ~400

| Module | Purpose | Replaces EE | License | Risk |
|--------|---------|-------------|---------|------|
| `sale_order_type` | Sale order types | - | AGPL-3 | None |
| `sale_order_line_sequence` | SO line sequences | - | AGPL-3 | None |

### project
**URL:** https://github.com/OCA/project
**Maturity:** proven | **Stars:** ~400

| Module | Purpose | Replaces EE | License | Risk |
|--------|---------|-------------|---------|------|
| `project_timeline` | Gantt-like timeline | project_enterprise (gantt) | AGPL-3 | None |
| `project_task_dependency` | Task dependencies | project_enterprise | AGPL-3 | None |
| `project_wbs` | Work Breakdown Structure | - | AGPL-3 | None |
| `project_template` | Project templates | - | AGPL-3 | None |
| `project_task_recurring` | Recurring tasks | - | AGPL-3 | None |

### hr-expense
**URL:** https://github.com/OCA/hr-expense
**Maturity:** stable | **Stars:** ~100

| Module | Purpose | Replaces EE | License | Risk |
|--------|---------|-------------|---------|------|
| `hr_expense_advance_clearing` | Expense advances | - | AGPL-3 | None |

### timesheet
**URL:** https://github.com/OCA/timesheet
**Maturity:** proven | **Stars:** ~200

| Module | Purpose | Replaces EE | License | Risk |
|--------|---------|-------------|---------|------|
| `hr_timesheet_sheet` | Weekly timesheet sheets | timesheet_grid (partial) | AGPL-3 | None |

### contract
**URL:** https://github.com/OCA/contract
**Maturity:** proven | **Stars:** ~300

| Module | Purpose | Replaces EE | License | Risk |
|--------|---------|-------------|---------|------|
| `contract` | Recurring contracts | subscription (partial) | AGPL-3 | None - excellent |
| `contract_sale` | Contracts from SO | subscription | AGPL-3 | None |

### account-reconcile
**URL:** https://github.com/OCA/account-reconcile
**Maturity:** stable | **Stars:** ~200

| Module | Purpose | Replaces EE | License | Risk |
|--------|---------|-------------|---------|------|
| `account_reconcile_oca` | Enhanced reconciliation | account_accountant | AGPL-3 | None |

### multi-company
**URL:** https://github.com/OCA/multi-company
**Maturity:** proven | **Stars:** ~200

| Module | Purpose | Replaces EE | License | Risk |
|--------|---------|-------------|---------|------|
| `account_invoice_inter_company` | Inter-company invoicing | inter_company_rules | AGPL-3 | None |
| `purchase_sale_inter_company` | Inter-company SO/PO | inter_company_rules | AGPL-3 | None |

### bank-payment
**URL:** https://github.com/OCA/bank-payment
**Maturity:** proven | **Stars:** ~300

| Module | Purpose | Replaces EE | License | Risk |
|--------|---------|-------------|---------|------|
| `account_payment_order` | Payment order management | - | AGPL-3 | None |
| `account_banking_sepa_credit_transfer` | SEPA credit transfers | - | AGPL-3 | None |

---

## Tier 10: Integration

### connector
**URL:** https://github.com/OCA/connector
**Maturity:** proven | **Stars:** ~300

| Module | Purpose | Replaces EE | License | Risk |
|--------|---------|-------------|---------|------|
| `connector` | External system integration | - | LGPL-3 | None |

### storage
**URL:** https://github.com/OCA/storage
**Maturity:** stable | **Stars:** ~100

| Module | Purpose | Replaces EE | License | Risk |
|--------|---------|-------------|---------|------|
| `storage_backend` | Abstract storage backend | - | LGPL-3 | None |
| `storage_backend_s3` | S3/MinIO storage | - | LGPL-3 | None |

---

## Tier 11: AI/ML (Experimental)

### ai
**URL:** https://github.com/OCA/ai
**Maturity:** experimental | **Stars:** ~50

| Module | Purpose | Replaces EE | License | Risk |
|--------|---------|-------------|---------|------|
| `ai_oca_bridge` | AI integration framework | - | AGPL-3 | Experimental |

---

## Sources

- [OCA GitHub](https://github.com/oca)
- [OCA Must-Have Modules List](https://odoo-community.org/list-of-must-have-oca-modules)
- [Odoo 19 Release Notes](https://www.odoo.com/odoo-19-release-notes)
- [OCA account-financial-reporting](https://github.com/OCA/account-financial-reporting)
- [OCA reporting-engine](https://github.com/OCA/reporting-engine)
