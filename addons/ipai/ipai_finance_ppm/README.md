# IPAI Finance PPM

## Overview

Finance Project Portfolio Management (Notion Parity).

- **Technical Name:** `ipai_finance_ppm`
- **Version:** 18.0.1.0.0
- **Category:** Accounting/Finance
- **License:** AGPL-3
- **Author:** InsightPulseAI
- **Application:** Yes
- **Installable:** Yes

## Business Use Case

*No business use case documented.*

## Functional Scope

### Data Models

- **ipai.close.task.step** (Model)
  - Month-End Close Task Step
  - Fields: 7 defined
- **ipai.finance.logframe** (Model)
  - Finance Logical Framework
  - Fields: 10 defined
- **ipai.finance.bir_schedule** (Model)
  - BIR Filing Schedule
  - Fields: 15 defined
- **project.task** (Model)
  - Fields: 1 defined
- **ipai.close.generator** (Model)
  - Closing Task Generator
  - Fields: 1 defined
- **ipai.bir.form.schedule** (Model)
  - Fields: 4 defined
- **finance.ppm.dashboard** (Model)
  - Finance PPM Automation Dashboard
  - Fields: 10 defined
- **finance.bir.deadline** (Model)
  - BIR Tax Filing Deadline
  - Fields: 14 defined
- **project.task** (Model)
  - Fields: 18 defined
- **ipai.bir.form.schedule** (Model)
  - BIR Compliance Schedule
  - Fields: 10 defined
- **ipai.bir.process.step** (Model)
  - BIR Process Step
  - Fields: 7 defined
- **res.users** (Model)
  - Fields: 1 defined
- **ipai.finance.task.template** (Model)
  - Finance SSC Monthly Task Template
  - Fields: 13 defined
- **ipai.finance.person** (Model)
  - Finance Team Directory
  - Fields: 5 defined
- **ipai.close.task.template** (Model)
  - Closing Task Template
  - Fields: 29 defined
- **ipai.close.generation.run** (Model)
  - Closing Task Generation Run
  - Fields: 23 defined
- **ipai.close.generated.map** (Model)
  - Generated Task Mapping
  - Fields: 6 defined

### Views

- : 10
- Form: 7
- Calendar: 2
- Search: 3
- Kanban: 2

### Menus

- `menu_finance_directory`: Directory
- `menu_finance_generated_tasks`: Generated Tasks
- `menu_finance_tasks`: Monthly Tasks
- `menu_finance_bir_deadlines`: BIR Deadlines
- `menu_finance_calendar`: Compliance Calendar
- ... and 7 more

## Installation & Dependencies

### Dependencies

- `base` (CE Core)
- `mail` (CE Core)
- `project` (CE Core)

### Installation

```bash
# Install module
odoo-bin -d <database> -i ipai_finance_ppm --stop-after-init

# Upgrade module
odoo-bin -d <database> -u ipai_finance_ppm --stop-after-init
```

## Configuration

### System Parameters

- `bir.reminder.mattermost.webhook`: https://mattermost.insightpulseai.net/hooks/REPLACE_WITH_ACTUAL_WEBHOOK_ID
- `bir.reminder.n8n.webhook`: https://ipa.insightpulseai.net/webhook/bir-reminder
- `bir.overdue.n8n.webhook`: https://ipa.insightpulseai.net/webhook/bir-overdue-nudge

### Scheduled Actions

- **Finance PPM: Generate Daily Tasks** (Active)
- **BIR Deadline Reminder - 9AM** (Active)
- **BIR Deadline Reminder - 5PM** (Active)
- **BIR Overdue Daily Nudge** (Active)

## Security

### Access Rules

*10 access rules defined in ir.model.access.csv*

## Integrations

- Odoo Mail (Email notifications)

## Upgrade Notes

- Current Version: 18.0.1.0.0
- No breaking changes documented

## Verification Steps

```bash
# 1. Verify module is installed
psql -d <database> -c "SELECT name, state FROM ir_module_module WHERE name = 'ipai_finance_ppm'"

# 2. Check module info
odoo-bin shell -d <database> -c 'print(env["ir.module.module"].search([("name", "=", "ipai_finance_ppm")]).state)'
```

## Data Files

- `security/ir.model.access.csv`
- `views/finance_person_views.xml`
- `views/finance_bir_deadline_views.xml`
- `views/finance_task_views.xml`
- `views/bir_schedule_views.xml`
- `views/ppm_dashboard_views.xml`
- `views/project_task_views.xml`
- `views/menus.xml`
- `data/finance_person_seed.xml`
- `data/bir_schedule_seed.xml`
- `data/finance_cron.xml`

## Static Validation Status

- Passed: 5
- Warnings: 0
- Failed: 0
