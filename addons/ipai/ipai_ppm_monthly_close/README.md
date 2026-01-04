# PPM Monthly Close Scheduler

## Overview

Automated monthly financial close scheduling with PPM and Notion workspace parity

- **Technical Name:** `ipai_ppm_monthly_close`
- **Version:** 18.0.1.0.0
- **Category:** Project Management
- **License:** AGPL-3
- **Author:** InsightPulse AI
- **Application:** No
- **Installable:** Yes

## Business Use Case

Monthly Financial Close Scheduler
==================================

Implements recurring monthly close workflow with:

* PPM-style project scheduling (Clarity parity)
* Task templates with owner/reviewer/approver roles
* Business day calculation (S = C - 3 working days)
* Automated task creation via cron
* Notion workspace parity (database view)
* n8n integration for notifications

Features:
---------
* Recurring schedule: 3rd business day before month-end
* Multi-agency support (RIM, CKVC, BO...

## Functional Scope

### Data Models

- **ppm.close.task** (Model)
  - Monthly Close Task
  - Fields: 25 defined
- **ppm.close.template** (Model)
  - Monthly Close Task Template
  - Fields: 14 defined
- **ppm.monthly.close** (Model)
  - Monthly Financial Close Schedule
  - Fields: 13 defined

### Views

- : 3
- Form: 3
- Calendar: 1
- Search: 1

### Menus

- `menu_ppm_monthly_close_root`: Monthly Close
- `menu_ppm_monthly_close`: Close Schedules
- `menu_ppm_close_task`: Tasks
- `menu_ppm_close_template`: Templates

## Installation & Dependencies

### Dependencies

- `base` (CE Core)
- `project` (CE Core)
- `mail` (CE Core)
- `resource` (CE Core)

### Installation

```bash
# Install module
odoo-bin -d <database> -i ipai_ppm_monthly_close --stop-after-init

# Upgrade module
odoo-bin -d <database> -u ipai_ppm_monthly_close --stop-after-init
```

## Configuration

*No specific configuration required.*

### Scheduled Actions

- **Create Next Month's Close Schedule** (Active)
- **Send Daily Task Reminders** (Active)

## Security

### Access Rules

*6 access rules defined in ir.model.access.csv*

## Integrations

- Odoo Mail (Email notifications)

## Upgrade Notes

- Current Version: 18.0.1.0.0
- No breaking changes documented

## Verification Steps

```bash
# 1. Verify module is installed
psql -d <database> -c "SELECT name, state FROM ir_module_module WHERE name = 'ipai_ppm_monthly_close'"

# 2. Check module info
odoo-bin shell -d <database> -c 'print(env["ir.module.module"].search([("name", "=", "ipai_ppm_monthly_close")]).state)'
```

## Data Files

- `security/ir.model.access.csv`
- `data/ppm_close_template_data_REAL.xml`
- `data/ppm_close_cron.xml`
- `views/ppm_monthly_close_views.xml`
- `views/ppm_close_task_views.xml`
- `views/ppm_close_template_views.xml`
- `views/ppm_close_menu.xml`

## Static Validation Status

- Passed: 5
- Warnings: 0
- Failed: 0
