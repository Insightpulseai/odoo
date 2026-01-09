# Odoo 18 CE Module Install Order

> **Philosophy**: Config → OCA → Delta (ipai_*)
>
> 1. Use Odoo's built-in configuration first
> 2. Use vetted OCA community modules second
> 3. Only create ipai_* modules for truly custom needs

---

## Phase 1: Odoo 18 CE Core Modules

Install these **first** via `docker compose --profile ce-init up`

### 1.1 Platform / Technical Base (Always Required)

```
base,web,base_setup,base_import,bus,mail,digest,iap,web_tour,web_editor,portal,resource,calendar
```

| Module | Purpose | Required |
|--------|---------|----------|
| `base` | Core framework | Yes |
| `web` | Web UI framework | Yes |
| `base_setup` | Setup wizards | Yes |
| `base_import` | Data import | Yes |
| `bus` | Longpolling/websocket | Yes |
| `mail` | Chatter, messaging, activity | Yes |
| `digest` | Digest emails | Recommended |
| `iap` | In-app purchase framework | Recommended |
| `web_tour` | Tours/onboarding | Recommended |
| `web_editor` | Rich text editor | Recommended |
| `portal` | Customer portal | Yes |
| `resource` | Working time/calendar | Yes |
| `calendar` | Calendar events | Yes |

### 1.2 CRM + Sales (Customer Operations)

```
contacts,sales_team,crm,sale,sale_management,sale_crm
```

| Module | Purpose | Required |
|--------|---------|----------|
| `contacts` | Partner management | Yes |
| `sales_team` | Sales teams | Yes |
| `crm` | CRM pipeline | Yes |
| `sale` | Core sales orders | Yes |
| `sale_management` | Sales quotations | Yes |
| `sale_crm` | CRM-Sales integration | Yes |

### 1.3 Finance / Accounting Core

```
analytic,account,account_payment
```

| Module | Purpose | Required |
|--------|---------|----------|
| `analytic` | Analytic accounting | Yes |
| `account` | Core accounting | Yes |
| `account_payment` | Payment handling | Yes |

### 1.4 Procurement + Inventory

```
purchase,purchase_requisition,stock,stock_account,stock_landed_costs,stock_picking_batch
```

| Module | Purpose | Required |
|--------|---------|----------|
| `purchase` | Purchase orders | Yes |
| `purchase_requisition` | Purchase agreements | Optional |
| `stock` | Inventory management | Yes |
| `stock_account` | Inventory valuation | Yes |
| `stock_landed_costs` | Landed costs | Optional |
| `stock_picking_batch` | Batch transfers | Optional |

### 1.5 Sales-Stock-Purchase Bridges

```
sale_stock,sale_purchase,purchase_stock
```

| Module | Purpose | Required |
|--------|---------|----------|
| `sale_stock` | Sales-Inventory integration | Yes |
| `sale_purchase` | Sales-Purchase integration | Optional |
| `purchase_stock` | Purchase-Inventory integration | Yes |

### 1.6 Manufacturing (If Applicable)

```
mrp,maintenance
```

| Module | Purpose | Required |
|--------|---------|----------|
| `mrp` | Manufacturing | Optional |
| `maintenance` | Equipment maintenance | Optional |

### 1.7 Projects + Services

```
project,project_todo,hr_timesheet,sale_timesheet
```

| Module | Purpose | Required |
|--------|---------|----------|
| `project` | Project management | Yes |
| `project_todo` | Personal tasks | Optional |
| `hr_timesheet` | Timesheet tracking | Yes |
| `sale_timesheet` | Billable timesheets | Yes |

### 1.8 HR Core

```
hr,hr_contract,hr_holidays,hr_attendance,hr_expense,hr_recruitment,hr_skills
```

| Module | Purpose | Required |
|--------|---------|----------|
| `hr` | HR core | Yes |
| `hr_contract` | Employee contracts | Optional |
| `hr_holidays` | Leave management | Optional |
| `hr_attendance` | Attendance tracking | Optional |
| `hr_expense` | Expense management | Yes |
| `hr_recruitment` | Recruiting | Optional |
| `hr_skills` | Skills matrix | Optional |

### 1.9 Website (If Portal/eCommerce Needed)

```
website,website_sale,website_crm,website_blog,website_forum,website_slides,website_event
```

| Module | Purpose | Required |
|--------|---------|----------|
| `website` | Website builder | Optional |
| `website_sale` | eCommerce | Optional |
| `website_crm` | Website CRM forms | Optional |
| `website_blog` | Blog | Optional |
| `website_forum` | Community forum | Optional |
| `website_slides` | eLearning | Optional |
| `website_event` | Event management | Optional |

### 1.10 Marketing + Communications

```
mass_mailing,im_livechat
```

| Module | Purpose | Required |
|--------|---------|----------|
| `mass_mailing` | Email marketing | Optional |
| `im_livechat` | Live chat | Optional |

### 1.11 Other CE Apps

```
point_of_sale,survey,lunch,fleet,repair
```

| Module | Purpose | Required |
|--------|---------|----------|
| `point_of_sale` | POS | Optional |
| `survey` | Surveys | Optional |
| `lunch` | Lunch orders | Optional |
| `fleet` | Vehicle management | Optional |
| `repair` | Repair orders | Optional |

---

## Phase 2: OCA Foundation Modules

Install **after** CE core via `docker compose --profile extended-init up`

### Tier 0: Foundation (Install First)

```
base_view_inheritance_extension,auditlog,date_range,base_user_role
```

| Module | OCA Repo | Purpose |
|--------|----------|---------|
| `base_view_inheritance_extension` | server-tools | View inheritance utilities |
| `auditlog` | server-tools | Audit trail |
| `date_range` | server-ux | Date range objects for reporting |
| `base_user_role` | server-backend | User role management |

### Tier 1: Platform UX

```
web_responsive,web_dialog_size,web_refresher
```

| Module | OCA Repo | Purpose |
|--------|----------|---------|
| `web_responsive` | web | Mobile-responsive UI |
| `web_dialog_size` | web | Resizable dialogs |
| `web_refresher` | web | Manual refresh button |

### Tier 2: Background Processing (Agent Runtime)

```
queue_job,queue_job_cron,queue_job_cron_jobrunner
```

| Module | OCA Repo | Purpose |
|--------|----------|---------|
| `queue_job` | queue | Async job queue |
| `queue_job_cron` | queue | Scheduled actions as jobs |
| `queue_job_cron_jobrunner` | queue | Cron runner integration |

### Tier 4: Reporting & BI

```
report_xlsx,mis_builder,account_financial_report,kpi_dashboard
```

| Module | OCA Repo | Purpose |
|--------|----------|---------|
| `report_xlsx` | reporting-engine | XLSX exports |
| `mis_builder` | mis-builder | KPI matrix reports (P&L, BS) |
| `account_financial_report` | account-financial-reporting | Financial statements |
| `kpi_dashboard` | reporting-engine | Dashboard widgets |

### Tier 5: Spreadsheet (CE Alternative)

```
spreadsheet_oca,spreadsheet_dashboard_oca
```

| Module | OCA Repo | Purpose |
|--------|----------|---------|
| `spreadsheet_oca` | spreadsheet | Embedded spreadsheets |
| `spreadsheet_dashboard_oca` | spreadsheet | Dashboard spreadsheets |

### Tier 6: Documents & Knowledge

```
document_page,dms
```

| Module | OCA Repo | Purpose |
|--------|----------|---------|
| `document_page` | knowledge | Wiki pages |
| `dms` | dms | Document management |

### Tier 7: API Layer (For AI + Integrations)

```
base_rest,base_rest_pydantic
```

| Module | OCA Repo | Purpose |
|--------|----------|---------|
| `base_rest` | rest-framework | REST API endpoints |
| `base_rest_pydantic` | rest-framework | Pydantic DTOs |

### Tier 8: Mail & Audit Polish

```
mail_activity_board,mail_debrand
```

| Module | OCA Repo | Purpose |
|--------|----------|---------|
| `mail_activity_board` | social | Activity dashboard |
| `mail_debrand` | social | Remove Odoo branding |

---

## Phase 3: IPAI Custom Modules

Install **after** OCA modules via `docker compose --profile init up`

### 3.1 Foundation Layer (Install First)

```
ipai_dev_studio_base → ipai_workspace_core → ipai_ce_branding
```

| Module | Depends On | Purpose |
|--------|------------|---------|
| `ipai_dev_studio_base` | base, web, mail, contacts, project | Base OCA/CE bundle |
| `ipai_workspace_core` | ipai_dev_studio_base | Unified workspace model |
| `ipai_ce_branding` | ipai_workspace_core | CE branding layer |

### 3.2 AI Platform Layer

```
ipai_ai_core → ipai_ai_agents → ipai_ai_prompts
```

| Module | Depends On | Purpose |
|--------|------------|---------|
| `ipai_ai_core` | ipai_ce_branding | AI framework core |
| `ipai_ai_agents` | ipai_ai_core | Agent system |
| `ipai_ai_prompts` | ipai_ai_core | Prompt management |
| `ipai_ask_ai` | ipai_ai_core | Ask AI copilot |

### 3.3 Finance PPM Layer

```
ipai_finance_ppm → ipai_finance_month_end → ipai_finance_bir_compliance
```

| Module | Depends On | Purpose |
|--------|------------|---------|
| `ipai_finance_ppm` | base, mail, project | Finance PPM core |
| `ipai_finance_month_end` | ipai_finance_ppm | Month-end close |
| `ipai_finance_bir_compliance` | ipai_finance_ppm | BIR tax compliance |
| `ipai_close_orchestration` | ipai_finance_month_end | Close orchestration |

### 3.4 Industry Verticals

| Module | Purpose |
|--------|---------|
| `ipai_industry_marketing_agency` | Marketing agency customizations |
| `ipai_industry_accounting_firm` | Accounting firm customizations |

### 3.5 Connectors

| Module | Purpose |
|--------|---------|
| `ipai_n8n_connector` | n8n workflow integration |
| `ipai_mattermost_connector` | Mattermost chat integration |
| `ipai_superset_connector` | Superset BI integration |

---

## Recommended Minimum Install

For **Odoo + Ask AI + Finance Ops** stack:

### CE Core (Required)
```bash
odoo -d odoo_core -i \
  base,web,base_setup,mail,portal,contacts,calendar,\
  account,account_payment,analytic,\
  purchase,stock,stock_account,\
  project,hr_timesheet \
  --stop-after-init
```

### OCA Foundation (Required)
```bash
odoo -d odoo_core -i \
  base_view_inheritance_extension,auditlog,date_range,\
  web_responsive,web_dialog_size,\
  queue_job,\
  report_xlsx,mis_builder,account_financial_report,\
  base_rest,\
  mail_activity_board,mail_debrand \
  --stop-after-init
```

### IPAI Platform (Required)
```bash
odoo -d odoo_core -i \
  ipai_dev_studio_base,ipai_workspace_core,ipai_ce_branding,\
  ipai_design_system_apps_sdk,ipai_ask_ai,ipai_command_center,\
  ipai_finance_ppm \
  --stop-after-init
```

---

## Docker Compose Profiles

| Profile | Purpose | Command |
|---------|---------|---------|
| `ce-init` | Install all CE core modules | `docker compose --profile ce-init up` |
| `extended-init` | Install OCA + IPAI platform | `docker compose --profile extended-init up` |
| `init` | Install IPAI base modules | `docker compose --profile init up` |
| (none) | Runtime services | `docker compose up -d` |

### Full Installation Sequence

```bash
# Step 1: Start PostgreSQL
docker compose up -d postgres

# Step 2: Install CE core modules
docker compose --profile ce-init up

# Step 3: Install OCA + IPAI platform modules
docker compose --profile extended-init up

# Step 4: Install IPAI base modules
docker compose --profile init up

# Step 5: Start runtime services
docker compose up -d odoo-core
```

---

## Module Verification

Check installed modules:

```bash
docker compose exec odoo-core odoo shell -d odoo_core << 'EOF'
installed = env['ir.module.module'].search([('state', '=', 'installed')])
for mod in installed.sorted('name'):
    print(f"{mod.name}: {mod.shortdesc}")
EOF
```

---

## addons_path Configuration

From `config/odoo-core.conf`:

```ini
addons_path = /usr/lib/python3/dist-packages/odoo/addons,\
/mnt/extra-addons/oca/server-tools,\
/mnt/extra-addons/oca/server-ux,\
/mnt/extra-addons/oca/server-backend,\
/mnt/extra-addons/oca/web,\
/mnt/extra-addons/oca/automation,\
/mnt/extra-addons/oca/queue,\
/mnt/extra-addons/oca/reporting-engine,\
/mnt/extra-addons/oca/mis-builder,\
/mnt/extra-addons/oca/account-financial-reporting,\
/mnt/extra-addons/oca/account-financial-tools,\
/mnt/extra-addons/oca/spreadsheet,\
/mnt/extra-addons/oca/knowledge,\
/mnt/extra-addons/oca/dms,\
/mnt/extra-addons/oca/rest-framework,\
/mnt/extra-addons/oca/social,\
/mnt/extra-addons/oca/account-reconcile,\
/mnt/extra-addons/oca/purchase-workflow,\
/mnt/extra-addons/oca/sale-workflow,\
/mnt/extra-addons/oca/hr-expense,\
/mnt/extra-addons/oca/project,\
/mnt/extra-addons/oca/contract,\
/mnt/extra-addons/oca/timesheet,\
/mnt/extra-addons/oca/connector,\
/mnt/extra-addons/oca/storage,\
/mnt/extra-addons/oca/ai,\
/mnt/extra-addons/ipai
```

**Order matters**: Later paths override earlier ones.

---

*Last updated: 2026-01-09*
