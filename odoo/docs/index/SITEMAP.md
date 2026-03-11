# Odoo CE 18.0 - InsightPulse AI Module Sitemap

**Production Instance**: https://erp.insightpulseai.com
**Database**: production
**Last Updated**: 2025-12-17

---

## Module Overview

| Module | Purpose | Status | Key Features |
|--------|---------|--------|--------------|
| `ipai_cash_advance` | Cash advance management | ✅ Installed | Request workflow, approval tracking |
| `ipai_ce_branding` | Custom branding for CE | ✅ Installed | Logo, colors, company info |
| `ipai_ce_cleaner` | UI cleanup and optimization | ✅ Installed | Remove clutter, streamline menus |
| `ipai_clarity_ppm_parity` | Clarity PPM integration | ✅ Installed | Projects, phases, milestones, BIR schedule |
| `ipai_default_home` | Default home page config | 🆕 Deployed | Apps Dashboard after login |
| `ipai_dev_studio_base` | Development studio base | ✅ Installed | Custom development tools |
| `ipai_docs` | Document management | ✅ Installed | Wiki, knowledge base, tags |
| `ipai_docs_project` | Project documentation | ✅ Installed | Link docs to projects/tasks |
| `ipai_equipment` | Asset/equipment tracking | ✅ Installed | Bookings, incidents, maintenance |
| `ipai_expense` | Expense management | ✅ Installed | Categories, policies, approvals |
| `ipai_finance_ppm` | Finance PPM dashboard | 🚧 In Progress | Logframe, BIR calendar, ECharts |
| `ipai_industry_accounting_firm` | Accounting firm workspace | ✅ Installed | Client management, engagement tracking |
| `ipai_industry_marketing_agency` | Marketing agency workspace | ✅ Installed | Campaign management, client briefs |
| `ipai_ocr_expense` | OCR expense automation | ✅ Installed | PaddleOCR-VL, auto-extraction |
| `ipai_ppm_monthly_close` | Month-end closing workflow | ✅ Installed | Checklists, templates, automation |
| `ipai_workspace_core` | Workspace core functionality | ✅ Installed | Multi-tenant workspace base |

---

## URL Structure

### Authentication
- **Login**: https://erp.insightpulseai.com/web/login?db=production
- **Database Selector**: https://erp.insightpulseai.com/web/database/selector

### Main Application
- **Apps Dashboard**: https://erp.insightpulseai.com/odoo (default after login)
- **Discuss**: https://erp.insightpulseai.com/odoo/discuss
- **Calendar**: https://erp.insightpulseai.com/odoo/calendar

### Finance & Compliance
- **Expenses**: https://erp.insightpulseai.com/odoo/hr_expense
- **OCR Expense Logs**: https://erp.insightpulseai.com/odoo/ipai_ocr_expense.ocr_expense_log
- **Cash Advances**: https://erp.insightpulseai.com/odoo/ipai_cash_advance.cash_advance
- **BIR Schedule**: https://erp.insightpulseai.com/odoo/ipai_clarity_ppm_parity.finance_bir_schedule
- **Finance PPM Dashboard**: https://erp.insightpulseai.com/ipai/finance/ppm

### Project Management
- **Projects**: https://erp.insightpulseai.com/odoo/project
- **Tasks**: https://erp.insightpulseai.com/odoo/project.task
- **Milestones**: https://erp.insightpulseai.com/odoo/project.milestone
- **Month-End Close**: https://erp.insightpulseai.com/odoo/ipai_ppm_monthly_close.ppm_monthly_close

### Equipment & Assets
- **Equipment**: https://erp.insightpulseai.com/odoo/ipai_equipment.equipment
- **Bookings**: https://erp.insightpulseai.com/odoo/ipai_equipment.booking
- **Incidents**: https://erp.insightpulseai.com/odoo/ipai_equipment.incident

### Documentation
- **Documents**: https://erp.insightpulseai.com/odoo/ipai_docs.doc
- **Tags**: https://erp.insightpulseai.com/odoo/ipai_docs.doc_tag
- **Workspaces**: https://erp.insightpulseai.com/odoo/ipai_workspace_core.workspace

### Settings
- **Users**: https://erp.insightpulseai.com/odoo/res.users
- **Companies**: https://erp.insightpulseai.com/odoo/res.company
- **Apps**: https://erp.insightpulseai.com/odoo/apps

---

## Module File Structure

### ipai_clarity_ppm_parity (Clarity PPM Integration)
```
addons/ipai_clarity_ppm_parity/
├── __manifest__.py
├── data/
│   ├── bir_schedule_2025_2026.xml          # BIR filing calendar
│   ├── bir_schedule_seed.xml               # BIR form templates
│   ├── clarity_data.xml                    # Clarity PPM sync data
│   ├── finance_person_seed.xml             # Finance team members
│   ├── month_end_closing_checklists.xml    # Month-end checklists (33 items)
│   ├── month_end_closing_detailed_workflow.xml
│   ├── month_end_closing_nov_dec_2025.xml
│   └── ppm_seed_users.xml                  # Finance users (RIM, CKVC, etc.)
├── models/
│   ├── project_checklist.py
│   ├── project_milestone.py
│   ├── project_phase.py
│   ├── project_project.py                  # Extended project model
│   └── project_task.py
└── views/
    └── project_project_views.xml           # Project views
```

### ipai_ppm_monthly_close (Month-End Closing)
```
addons/ipai_ppm_monthly_close/
├── __manifest__.py
├── README.md
├── INSTALL_NOVEMBER_2025.md
├── data/
│   ├── ppm_close_cron.xml                  # Auto-task creation cron
│   └── ppm_close_template_data_REAL.xml    # Closing templates
├── models/
│   ├── ppm_close_task.py                   # Individual close tasks
│   ├── ppm_close_template.py               # Reusable templates
│   └── ppm_monthly_close.py                # Main close schedule
├── views/
│   ├── ppm_close_menu.xml
│   ├── ppm_close_task_views.xml
│   ├── ppm_close_template_views.xml
│   └── ppm_monthly_close_views.xml
├── tests/
│   └── test_monthly_close.py
└── wizards/
```

### ipai_ocr_expense (OCR Automation)
```
addons/ipai_ocr_expense/
├── __manifest__.py
├── data/
│   └── ir_actions_server.xml               # Server actions for OCR
├── models/
│   ├── hr_expense.py                       # Extended expense model
│   ├── hr_expense_ocr.py                   # OCR processing logic
│   ├── ocr_expense_log.py                  # OCR audit logs
│   └── res_config_settings.py              # OCR settings
├── views/
│   ├── hr_expense_views.xml
│   ├── ipai_ocr_expense_views.xml
│   ├── ipai_ocr_settings_views.xml
│   └── ocr_expense_log_views.xml
└── tests/
    └── test_expense_ocr.py
```

### ipai_default_home (Default Home Page)
```
addons/ipai_default_home/
├── __manifest__.py
├── README.md
├── __init__.py
└── data/
    └── default_home_data.xml               # Apps Dashboard config
```

### ipai_docs (Document Management)
```
addons/ipai_docs/
├── __manifest__.py
├── models/
│   ├── ipai_doc.py                         # Document model
│   └── ipai_doc_tag.py                     # Tag model
├── views/
│   ├── ipai_doc_tag_views.xml
│   ├── ipai_doc_views.xml
│   └── menu.xml
└── tests/
    └── test_workspace_visibility.py
```

### ipai_equipment (Asset Tracking)
```
addons/ipai_equipment/
├── __manifest__.py
├── data/
│   ├── ipai_equipment_cron.xml             # Auto-return bookings
│   └── ipai_equipment_sequences.xml        # Booking numbers
├── models/
│   └── equipment.py                        # Equipment, booking, incident
├── views/
│   ├── ipai_equipment_menus.xml
│   └── ipai_equipment_views.xml
└── tests/
    └── test_booking_cron.py
```

---

## User Roles & Permissions

### Finance Team (8 employees)
| Code | Name | Email | Role |
|------|------|-------|------|
| RIM | Rita Mae Quebral | rita.quebral@omc.com | Senior Finance Manager |
| CKVC | Cyndie Kat Cabrera | ckvc@omc.com | Finance Supervisor |
| BOM | Benjie Lim | benjie.lim@omc.com | Finance Officer |
| JPAL | Jerome Paladin | jerome.paladin@omc.com | Finance Staff |
| JLI | Justin Li | justin.li@omc.com | Finance Staff |
| JAP | Jinky Paladin | jinky.paladin@omc.com | Finance Staff |
| LAS | Lhea Santos | lhea.santos@omc.com | Finance Staff |
| RMQB | Rita Mae Quebral | rita.quebral@omc.com | Finance Director |

### Access Levels
- **Admin**: Full access to all modules
- **Finance Director**: Approval authority, reporting
- **Finance Manager**: Task management, review
- **Finance Staff**: Data entry, processing

---

## Integration Points

### External Services
- **PaddleOCR-VL**: https://ade-ocr-backend-*.ondigitalocean.app
- **n8n Workflows**: https://ipa.insightpulseai.com
- **Mattermost**: https://mattermost.insightpulseai.com
- **Supabase**: https://xkxyvboeubffxxbebsll.supabase.co

### Database Connections
- **Odoo PostgreSQL**: odoo-db:5432 (internal Docker network)
- **Supabase PostgreSQL**: aws-1-us-east-1.pooler.supabase.com:6543

### API Endpoints
- **XML-RPC**: https://erp.insightpulseai.com/xmlrpc/2/common
- **JSON-RPC**: https://erp.insightpulseai.com/jsonrpc
- **Finance PPM API**: https://erp.insightpulseai.com/ipai/finance/ppm/api/*

---

## Key Workflows

### Month-End Closing
1. **Preparation** (Finance Staff) → Oct 24-27
   - Payroll processing
   - Accruals and amortization
   - WIP reconciliation

2. **Review** (Finance Manager) → Oct 28-30
   - Validate entries
   - Check balances
   - Verify completeness

3. **Approval** (Finance Director) → Oct 31 - Nov 3
   - Final approval
   - Report generation
   - BIR form preparation

### BIR Filing
1. **1601-C** (Monthly) → Due 10th of following month
2. **0619-E** (Monthly) → Due 10th of following month
3. **2550Q** (Quarterly) → Due 60 days after quarter-end
4. **1702-RT** (Annual) → Due April 15

### Expense Approval
1. **Employee Submission** → Upload receipt + details
2. **OCR Processing** → PaddleOCR-VL extracts data
3. **Manager Review** → Validate against policy
4. **Finance Approval** → Final approval + reimbursement

---

## Navigation Menus

### Finance Menu
- Expenses
  - My Expenses
  - All Expenses
  - To Approve
  - OCR Logs
- Cash Advances
  - My Cash Advances
  - All Cash Advances
  - To Approve
- Reports
  - BIR Schedule
  - Month-End Closing
  - Finance PPM Dashboard

### Project Menu
- Projects
  - All Projects
  - My Projects
  - Clarity PPM Sync
- Tasks
  - My Tasks
  - All Tasks
  - Month-End Tasks
- Reporting
  - Milestones
  - Gantt Chart
  - Timeline

### Equipment Menu
- Equipment
  - All Equipment
  - Available
  - Booked
  - Under Maintenance
- Bookings
  - My Bookings
  - All Bookings
  - Calendar View
- Incidents
  - Open Incidents
  - Resolved
  - Maintenance History

### Documents Menu
- All Documents
- My Documents
- Tags
- Workspaces
- Search

---

## Database Tables (Key Models)

### Finance
- `hr_expense` - Expense records
- `ipai_cash_advance.cash_advance` - Cash advance requests
- `ipai_ocr_expense.ocr_expense_log` - OCR processing logs
- `ipai_finance.bir_schedule` - BIR filing schedule
- `ipai_finance.logframe` - Logical framework

### Project Management
- `project.project` - Projects
- `project.task` - Tasks
- `project.milestone` - Milestones
- `project.phase` - Project phases
- `project.task.checklist` - Task checklists
- `ipai_ppm_monthly_close.ppm_monthly_close` - Month-end close schedules
- `ipai_ppm_monthly_close.ppm_close_task` - Close tasks
- `ipai_ppm_monthly_close.ppm_close_template` - Close templates

### Equipment
- `ipai_equipment.equipment` - Equipment catalog
- `ipai_equipment.booking` - Equipment bookings
- `ipai_equipment.incident` - Equipment incidents

### Documents
- `ipai_docs.doc` - Documents
- `ipai_docs.doc_tag` - Document tags
- `ipai_workspace_core.workspace` - Workspaces

---

## Cron Jobs

| Job | Schedule | Purpose |
|-----|----------|---------|
| `ipai_equipment_auto_return` | Daily 8AM | Auto-return overdue bookings |
| `ipai_ppm_close_auto_tasks` | Daily 8AM | Create month-end close tasks |
| `ipai_ocr_expense_retry` | Hourly | Retry failed OCR extractions |

---

## Configuration

### System Parameters
- `web.base.url.redirect` = `/odoo` (Apps Dashboard)

### Company Settings
- **Name**: InsightPulse AI
- **Currency**: PHP
- **Timezone**: Asia/Manila
- **Language**: English

### OCR Settings
- **Provider**: PaddleOCR-VL
- **Endpoint**: https://ade-ocr-backend-*.ondigitalocean.app
- **Min Confidence**: 0.60
- **Retry Attempts**: 3

---

## Troubleshooting

### Common Issues
1. **OCR not working**: Check OCR service URL in Settings → OCR Expense
2. **Module not visible**: Apps → Update Apps List
3. **Wrong redirect after login**: Clear user's `action_id` in database
4. **BIR tasks not auto-created**: Check cron job `ipai_ppm_close_auto_tasks`

### Support Contacts
- **Admin**: admin@insightpulseai.com
- **Finance Director**: rita.quebral@omc.com
- **System Issues**: Contact server admin

---

## Recent Changes

### 2025-12-17
- ✅ Added month-end closing checklists (33 items)
- ✅ Created `ipai_default_home` module
- ✅ Fixed admin user redirect to Apps Dashboard
- ✅ Deployed all changes to production

### 2025-12-16
- ✅ Installed `ipai_clarity_ppm_parity` module
- ✅ Seeded BIR schedule for 2025-2026
- ✅ Created Finance team users (8 employees)

---

**End of Sitemap** | Generated: 2025-12-17 | Production: https://erp.insightpulseai.com
