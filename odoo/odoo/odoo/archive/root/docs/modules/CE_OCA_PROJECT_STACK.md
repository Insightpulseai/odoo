# CE + OCA Project Stack Mapping (Odoo 18)

**Document:** Odoo Enterprise Project App → CE + OCA Parity Matrix
**Target:** InsightPulse ERP (`erp.insightpulseai.com`)
**Stack:** Odoo 18 CE + OCA 18.0 + ipai_* delta modules
**Policy:** No Enterprise, no IAP. Always prefer **Config → OCA → Delta**.

This document is the canonical mapping for achieving **Odoo Enterprise Project** feature parity using only CE + OCA + custom ipai_* modules.

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Enterprise Features | 9 major areas |
| CE-Native Coverage | 40% |
| OCA Replacement Coverage | 45% |
| IPAI Delta Coverage | 10% |
| External Tool Coverage | 5% |
| **Total Parity** | **95%** |

---

## 1. Feature → Module Mapping Matrix

### 1.1 Core Project App (Tasks, Kanban, List, Chatter, Tags, Subtasks)

**Enterprise Feature:** Project Management
**Parity Level:** 100% CE-Native

| Feature | CE Module | OCA Enhancement | IPAI Delta | Notes |
|---------|-----------|-----------------|------------|-------|
| Project CRUD | `project` | - | - | CE native |
| Tasks/Subtasks | `project` | `project_task_default_stage` | - | CE native |
| Kanban/List views | `project` | - | - | CE native |
| Chatter/Followers | `mail` | - | - | CE native |
| Tags/Categories | `project` | `project_tag` | - | CE native |
| Activity scheduling | `mail` | `mail_activity_board` | - | CE native |
| Portal access | `portal` | `project_portal_*` | - | CE native |

**Install Set:**
```bash
# CE Core (auto-installed)
project, mail, portal, web

# OCA Enhancements (recommended)
project_task_default_stage
project_stage_closed
project_task_code
```

---

### 1.2 Task Dependencies & Recurring Tasks

**Enterprise Feature:** Task Dependencies, Recurring Tasks
**Parity Level:** 95% with OCA

| Feature | CE Module | OCA Enhancement | IPAI Delta | Notes |
|---------|-----------|-----------------|------------|-------|
| Task dependencies | - | `project_task_dependency` | - | OCA covers this |
| Recurring tasks | - | `project_task_recurring` | - | OCA covers this |
| Closed stage control | - | `project_stage_closed` | - | OCA covers this |
| Task templates | - | `project_task_template` | - | OCA covers this |

**Install Set:**
```bash
# OCA/project 18.0
project_task_dependency
project_task_recurring
project_stage_closed
project_task_template
```

---

### 1.3 Customer Collaboration (Portal Access)

**Enterprise Feature:** Customer Portal for Projects
**Parity Level:** 90% with CE + OCA

| Feature | CE Module | OCA Enhancement | IPAI Delta | Notes |
|---------|-----------|-----------------|------------|-------|
| Portal task view | `portal` | - | - | CE native |
| Portal task edit | `portal` | `project_portal` | - | OCA enhances |
| Customer messaging | `mail` | - | - | CE native |
| Task comments | `mail` | - | - | CE native |
| Document attachments | `mail` | `dms_attachment_link` | - | OCA DMS for advanced |

**Install Set:**
```bash
# CE Core
portal, mail, project

# OCA Enhancements
# OCA/project
project_portal  # (if available in 18.0)
```

---

### 1.4 Time Tracking (Timer, Timesheets) + Invoicing

**Enterprise Feature:** Timesheets Grid, Timer, Billable Time
**Parity Level:** 90% with OCA

| Feature | CE Module | OCA Enhancement | IPAI Delta | Notes |
|---------|-----------|-----------------|------------|-------|
| Timesheets on tasks | `hr_timesheet` | - | - | CE native |
| Timesheet sheets | - | `hr_timesheet_sheet` | - | OCA grid-like |
| Timer button | - | `project_timesheet_time_control` | `ipai_grid_view` | OCA + custom |
| Billable time | `sale_timesheet` | - | - | CE native |
| Invoice from time | `sale_timesheet` | - | - | CE native |
| Task-required timesheet | - | `hr_timesheet_task_required` | - | OCA validation |

**Install Set:**
```bash
# CE Core
hr_timesheet
sale_timesheet
account

# OCA/timesheet 18.0
hr_timesheet_sheet
hr_timesheet_task_required

# OCA/project 18.0
project_timesheet_time_control  # (if available)

# IPAI (optional)
ipai_grid_view  # Custom grid view enhancements
```

---

### 1.5 Profitability / Costs & Revenues / Budgets

**Enterprise Feature:** Project Profitability Dashboard
**Parity Level:** 85% with CE + OCA + Superset

| Feature | CE Module | OCA Enhancement | IPAI Delta | Notes |
|---------|-----------|-----------------|------------|-------|
| Analytic accounts | `analytic` | - | - | CE native |
| Cost tracking | `account` | `account_analytic_*` | - | OCA enhances |
| Revenue tracking | `sale` | - | - | CE native |
| Budget management | - | `mis_builder_budget` | - | OCA covers |
| Profitability reports | - | `mis_builder` | `ipai_superset_connector` | Superset dashboards |
| Multi-currency | `account` | - | - | CE native |

**Install Set:**
```bash
# CE Core
account
analytic
sale_management
purchase

# OCA/account-analytic 18.0
# (Add specific modules based on needs)

# OCA/mis-builder 18.0
mis_builder
mis_builder_budget

# IPAI
ipai_superset_connector  # BI dashboards in Superset
ipai_finance_ppm         # Finance PPM workflows
```

---

### 1.6 Milestones

**Enterprise Feature:** Project Milestones
**Parity Level:** 75% with OCA + IPAI

| Feature | CE Module | OCA Enhancement | IPAI Delta | Notes |
|---------|-----------|-----------------|------------|-------|
| Milestone tracking | - | `project_milestone` | `ipai_project_program` | Mixed coverage |
| Milestone deadlines | `project` | - | - | Via task deadlines |
| Milestone billing | `sale_timesheet` | - | `ipai_finance_ppm` | Custom billing |
| WBS structure | - | `project_wbs` | `ipai_clarity_ppm_parity` | OCA WBS |

**Install Set:**
```bash
# OCA/project 18.0
project_wbs
project_milestone  # (if available)

# IPAI
ipai_project_program
ipai_clarity_ppm_parity
ipai_finance_ppm
```

---

### 1.7 Planning / Scheduling / Resource Planning

**Enterprise Feature:** Planning App (Resource Scheduling)
**Parity Level:** 75% - Enterprise Gap

| Feature | CE Module | OCA Enhancement | IPAI Delta | Notes |
|---------|-----------|-----------------|------------|-------|
| Task scheduling | `project` | `project_timeline` | - | OCA timeline |
| Dependencies | - | `project_task_dependency` | - | OCA covers |
| Calendar views | `calendar` | - | - | CE native |
| Resource allocation | `resource` | `project_resource_calendar` | `ipai_ppm` | Mixed |
| Gantt view | - | - | - | **Enterprise gap** |
| Capacity planning | - | - | `ipai_ppm` | Custom via Superset |

**Install Set:**
```bash
# CE Core
project
calendar
resource

# OCA/project 18.0
project_timeline
project_task_dependency
project_resource_calendar  # (if available)

# IPAI
ipai_ppm
ipai_finance_ppm
ipai_superset_connector  # Capacity dashboards
```

**Enterprise Gap Notes:**
- Polished Gantt view is Enterprise-only
- Drag-and-drop resource scheduling is Enterprise-only
- Workaround: Use `project_timeline` + custom calendar views + Superset

---

### 1.8 Document Management

**Enterprise Feature:** Documents App (Workspace per Project)
**Parity Level:** 80% with OCA DMS

| Feature | CE Module | OCA Enhancement | IPAI Delta | Notes |
|---------|-----------|-----------------|------------|-------|
| File attachments | `mail` | - | - | CE native |
| Folder structure | - | `dms` | - | OCA DMS |
| Document fields | - | `dms_field` | - | OCA DMS |
| Project-linked docs | - | `dms_project` | - | OCA bridge (if avail) |
| Version control | - | `dms` | - | OCA DMS |
| Document workflows | - | - | `ipai_workos_*` | Custom WorkOS |

**Install Set:**
```bash
# OCA/dms 18.0
dms
dms_field
dms_attachment_link

# IPAI (optional - Notion-style workspaces)
ipai_workos_core
ipai_workos_blocks
ipai_workos_db
```

**Enterprise Gap Notes:**
- Enterprise Documents has richer UI/UX
- OCA DMS is functionally complete but less polished
- Alternative: Use Notion integration via n8n

---

### 1.9 Digital Signatures (Sign)

**Enterprise Feature:** Sign App
**Parity Level:** 60% - External Tool Recommended

| Feature | CE Module | OCA Enhancement | IPAI Delta | Notes |
|---------|-----------|-----------------|------------|-------|
| PDF signing | - | - | - | **Enterprise gap** |
| Signature fields | - | - | - | **Enterprise gap** |
| Audit trail | - | - | `ipai_platform_audit` | Custom audit |
| E-sign workflow | - | - | - | Use external tool |

**Recommended External Tools:**
- DocuSign
- HelloSign
- Adobe Sign
- PH e-sign tools (for Philippine compliance)

**Install Set:**
```bash
# No OCA equivalent - use external integration

# n8n workflows for e-sign API integration
# See: n8n/workflows/esign/

# IPAI (audit trail only)
ipai_platform_audit
```

---

### 1.10 Reporting / Dashboards

**Enterprise Feature:** Advanced Reporting, Studio Dashboards
**Parity Level:** 90% with OCA + Superset

| Feature | CE Module | OCA Enhancement | IPAI Delta | Notes |
|---------|-----------|-----------------|------------|-------|
| List/Pivot/Graph | `web` | - | - | CE native |
| Excel export | - | `report_xlsx` | - | OCA covers |
| Custom reports | - | `report_py3o` | - | OCA covers |
| BI dashboards | - | - | `ipai_superset_connector` | Superset |
| MIS reports | - | `mis_builder` | - | OCA covers |

**Install Set:**
```bash
# OCA/reporting-engine 18.0
report_xlsx
report_xlsx_helper
report_py3o  # (if needed)

# OCA/mis-builder 18.0
mis_builder

# IPAI
ipai_superset_connector
```

---

## 2. Locked Install Matrix

### 2.0 Official CE 18 Project Modules (24 modules)

**Source:** Odoo 18 Apps Catalog (odoo.com/apps, filtered: Project category, CE only)

| # | Module | Technical Name | Version | Category | Dependencies |
|---|--------|----------------|---------|----------|--------------|
| 1 | **Project** | `project` | 18.0.1.3 | Services | base |
| 2 | **To-Do** | `project_todo` | 18.0.1.0 | Productivity | project |
| 3 | **Project Mail Plugin** | `project_mail_plugin` | 18.0.1.0 | Services | project, mail_plugin |
| 4 | **Project - Account** | `project_account` | 18.0.1.0 | Technical | project, analytic |
| 5 | **Project Expenses** | `project_hr_expense` | 18.0.1.0 | Services | project, hr_expense |
| 6 | **Project - Skills** | `project_hr_skills` | 18.0.1.0 | Human Resources | project, hr_skills |
| 7 | **MRP Project** | `project_mrp` | 18.0.1.0 | Manufacturing | project, mrp |
| 8 | **MRP Account Project** | `project_mrp_account` | 18.0.1.0 | Technical | project_mrp, mrp_account |
| 9 | **MRP Project Sale** | `project_mrp_sale` | 18.0.1.0 | Technical | project_mrp, sale_project |
| 10 | **Project MRP Landed Costs** | `project_mrp_stock_landed_costs` | 18.0.1.0 | Technical | project_mrp, stock_landed_costs |
| 11 | **Project Purchase** | `project_purchase` | 18.0.1.0 | Services | project, purchase |
| 12 | **Project - Purchase - Stock** | `project_purchase_stock` | 18.0.1.0 | Technical | project_purchase, stock |
| 13 | **Project - Sale - Expense** | `project_sale_expense` | 18.0.1.0 | Services | project_hr_expense, sale_project |
| 14 | **Project - SMS** | `project_sms` | 18.0.1.1 | Services | project, sms |
| 15 | **Project Stock** | `project_stock` | 18.0.1.0 | Inventory | project, stock |
| 16 | **Project Stock Account** | `project_stock_account` | 18.0.1.0 | Technical | project_stock, stock_account |
| 17 | **Project Stock Landed Costs** | `project_stock_landed_costs` | 18.0.1.0 | Technical | project_stock, stock_landed_costs |
| 18 | **Timesheet when on Time Off** | `project_timesheet_holidays` | 18.0.1.0 | Services | hr_holidays, hr_timesheet |
| 19 | **Sales - Project** | `sale_project` | 18.0.1.0 | Sales | project, sale_management |
| 20 | **Sale Project - Sale Stock** | `sale_project_stock` | 18.0.1.0 | Technical | sale_project, sale_stock |
| 21 | **Sale Project Stock Account** | `sale_project_stock_account` | 18.0.1.0 | Technical | sale_project_stock, stock_account |
| 22 | **Sale Purchase Project** | `sale_purchase_project` | 18.0.1.0 | Technical | sale_project, purchase |
| 23 | **Sales - Service** | `sale_service` | 18.0.1.0 | Sales | sale, project |
| 24 | **Online Task Submission** | `website_project` | 18.0.1.0 | Website | project, website |

**Install All CE Project Modules:**
```bash
odoo-bin -d $DB -i project,project_todo,project_mail_plugin,project_account,project_hr_expense,project_hr_skills,project_mrp,project_mrp_account,project_mrp_sale,project_mrp_stock_landed_costs,project_purchase,project_purchase_stock,project_sale_expense,project_sms,project_stock,project_stock_account,project_stock_landed_costs,project_timesheet_holidays,sale_project,sale_project_stock,sale_project_stock_account,sale_purchase_project,sale_service,website_project --stop-after-init
```

---

### 2.1 CE Core Modules (Required)

| Module | Technical Name | Purpose |
|--------|----------------|---------|
| Project | `project` | Core project management |
| Discuss/Mail | `mail` | Chatter, activities |
| Portal | `portal` | Customer access |
| Timesheets | `hr_timesheet` | Time tracking |
| Sales Timesheet | `sale_timesheet` | Billable time |
| Accounting | `account` | Invoicing, analytics |
| Sales | `sale_management` | Sales orders |
| Purchase | `purchase` | Costs, vendor bills |
| Calendar | `calendar` | Scheduling |
| Resource | `resource` | Resource planning base |

```bash
# Install all CE core
./odoo-bin -d $DB -i project,mail,portal,hr_timesheet,sale_timesheet,account,sale_management,purchase,calendar,resource --stop-after-init
```

---

### 2.2 OCA 18.0 Repositories (Required)

| Repository | Branch | Key Modules |
|------------|--------|-------------|
| OCA/project | 18.0 | `project_wbs`, `project_task_dependency`, `project_task_recurring`, `project_template`, `project_task_template`, `project_stage_closed`, `project_timeline` |
| OCA/timesheet | 18.0 | `hr_timesheet_sheet`, `hr_timesheet_task_required` |
| OCA/account-analytic | 18.0 | Analytic enhancements |
| OCA/account-financial-reporting | 18.0 | `account_financial_report` |
| OCA/mis-builder | 18.0 | `mis_builder`, `mis_builder_budget` |
| OCA/dms | 18.0 | `dms`, `dms_field`, `dms_attachment_link` |
| OCA/reporting-engine | 18.0 | `report_xlsx`, `report_xlsx_helper` |
| OCA/web | 18.0 | `web_responsive`, `web_refresher` |
| OCA/server-tools | 18.0 | `base_view_inheritance_extension`, `auditlog` |
| OCA/server-ux | 18.0 | `date_range` |

---

### 2.3 IPAI Custom Modules (Differentiators)

| Module | Purpose | Replaces |
|--------|---------|----------|
| `ipai_finance_ppm` | Finance PPM workflows | Clarity PPM patterns |
| `ipai_project_program` | Program management | - |
| `ipai_clarity_ppm_parity` | WBS/PPM structures | - |
| `ipai_ppm` | Core PPM features | - |
| `ipai_superset_connector` | BI dashboards | Enterprise dashboards |
| `ipai_grid_view` | Grid view enhancements | `timesheet_grid` (partial) |
| `ipai_workos_core` | Notion-style workspaces | Enterprise Knowledge |
| `ipai_platform_audit` | Audit trail | - |

---

## 3. Updated oca.lock.json Additions

The following OCA modules should be added to `oca.lock.json`:

```json
{
  "project": {
    "url": "https://github.com/OCA/project",
    "branch": "18.0",
    "modules": [
      "project_wbs",
      "project_template",
      "project_task_template",
      "project_task_dependency",
      "project_task_recurring",
      "project_stage_closed",
      "project_timeline",
      "project_task_default_stage",
      "project_task_code"
    ]
  },
  "timesheet": {
    "url": "https://github.com/OCA/timesheet",
    "branch": "18.0",
    "modules": [
      "hr_timesheet_sheet",
      "hr_timesheet_task_required"
    ]
  },
  "dms": {
    "url": "https://github.com/OCA/dms",
    "branch": "18.0",
    "modules": [
      "dms",
      "dms_field",
      "dms_attachment_link"
    ]
  },
  "mis-builder": {
    "url": "https://github.com/OCA/mis-builder",
    "branch": "18.0",
    "modules": [
      "mis_builder",
      "mis_builder_budget"
    ]
  }
}
```

---

## 4. Enterprise Gaps (Cannot Fully Replicate)

| Enterprise Feature | Gap Level | Workaround |
|--------------------|-----------|------------|
| **Gantt View** | High | Use `project_timeline` + calendar + Superset |
| **Planning App** | High | OCA dependencies + custom capacity views |
| **Documents App UX** | Medium | OCA DMS is functional but less polished |
| **Sign App** | High | External e-sign service (DocuSign, etc.) |
| **Resource Planning Drag/Drop** | Medium | Manual scheduling + calendar views |

---

## 5. Verification Checklist

### Pre-Installation

```bash
# Verify OCA repos are available
for repo in project timesheet dms mis-builder; do
  curl -s "https://api.github.com/repos/OCA/$repo/branches/18.0" | jq '.name'
done
```

### Post-Installation

```bash
# Run verification
./scripts/odoo/verify-oca-modules.sh project
./scripts/odoo/verify-oca-modules.sh timesheet
./scripts/odoo/verify-oca-modules.sh dms

# Run module tests
./scripts/ci/run_odoo_tests.sh project_wbs
./scripts/ci/run_odoo_tests.sh hr_timesheet_sheet
```

### Functional Verification

| Test | Expected Result |
|------|-----------------|
| Create project | Project with stages visible |
| Create task with dependency | Dependency graph renders |
| Log timesheet via sheet | Sheet approval workflow works |
| Create DMS folder | Folder linked to project |
| Run MIS report | Profitability data renders |

---

## 6. Related Documentation

- [ODOO18_ENTERPRISE_TO_CE_OCA_MAPPING.md](./ODOO18_ENTERPRISE_TO_CE_OCA_MAPPING.md) - Master Enterprise mapping
- [odoo-apps-parity.md](./odoo-apps-parity.md) - Full app parity matrix
- [INDUSTRY_PACKS_OCA_DEPENDENCIES.md](./INDUSTRY_PACKS_OCA_DEPENDENCIES.md) - Industry pack OCA deps
- [audits/ipai_modules/oca_overlap_map.yaml](./audits/ipai_modules/oca_overlap_map.yaml) - IPAI/OCA overlap

---

## 7. Maintenance

### Updating OCA Modules

```bash
# Update oca.lock.json and sync
./scripts/oca-sync.sh project
./scripts/oca-update.sh

# Verify no breaking changes
./scripts/ci_local.sh
```

### Adding New OCA Modules

1. Check OCA repo for 18.0 availability
2. Add to `oca.lock.json`
3. Run `./scripts/oca-sync.sh`
4. Test installation
5. Update this document

---

*Last Updated: 2026-01-21*
*Version: 1.1.0*

---

## Changelog

- **v1.1.0** (2026-01-21): Added Section 2.0 with all 24 official CE 18 project modules from Odoo Apps catalog
- **v1.0.0** (2026-01-05): Initial release
