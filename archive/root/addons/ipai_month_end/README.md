# IPAI Month-End Closing

## Overview

SAP AFC replacement - Month-end closing automation

- **Technical Name:** `ipai_month_end`
- **Version:** 18.0.1.0.0
- **Category:** Accounting
- **License:** AGPL-3
- **Author:** IPAI
- **Application:** Yes
- **Installable:** Yes

## Business Use Case

Month-end closing automation with SAP Advanced Financial Closing (AFC) feature parity.

        Features:
        - Template-driven task management
        - RACI workflow (Prep → Review → Approve)
        - Holiday-aware workday scheduling (Philippines)
        - Overdue notifications
        - Progress tracking dashboards

        Replaces SAP AFC at zero licensing cost.

## Functional Scope

### Data Models

- **ipai.month.end.closing** (Model)
  - Month-End Closing
  - Fields: 10 defined
- **ipai.month.end.task.template** (Model)
  - Month-End Task Template
  - Fields: 15 defined
- **ipai.ph.holiday** (Model)
  - Philippine Holiday
  - Fields: 4 defined
- **ipai.month.end.task** (Model)
  - Month-End Task
  - Fields: 24 defined

### Views

- : 4
- Form: 4
- Search: 4
- Kanban: 2
- Calendar: 1

### Menus

- `menu_month_end_root`: Month-End Closing
- `menu_closings`: Closings
- `menu_tasks`: Tasks
- `menu_config`: Configuration
- `menu_task_templates`: Task Templates
- ... and 1 more

## Installation & Dependencies

### Dependencies

- `base` (CE Core)
- `mail` (CE Core)
- `account` (CE Core)

### Installation

```bash
# Install module
odoo-bin -d <database> -i ipai_month_end --stop-after-init

# Upgrade module
odoo-bin -d <database> -u ipai_month_end --stop-after-init
```

## Configuration

*No specific configuration required.*

### Scheduled Actions

- **Month-End: Send Overdue Notifications** (Active)

## Security

### Access Rules

*8 access rules defined in ir.model.access.csv*

## Integrations

- Odoo Mail (Email notifications)

## Upgrade Notes

- Current Version: 18.0.1.0.0
- No breaking changes documented

## Verification Steps

```bash
# 1. Verify module is installed
psql -d <database> -c "SELECT name, state FROM ir_module_module WHERE name = 'ipai_month_end'"

# 2. Check module info
odoo-bin shell -d <database> -c 'print(env["ir.module.module"].search([("name", "=", "ipai_month_end")]).state)'
```

## Data Files

- `security/ir.model.access.csv`
- `data/ph_holidays.xml`
- `data/task_templates.xml`
- `data/ir_cron.xml`
- `views/ph_holiday_views.xml`
- `views/task_template_views.xml`
- `views/closing_views.xml`
- `views/task_views.xml`
- `views/menu.xml`

## Static Validation Status

- Passed: 5
- Warnings: 0
- Failed: 0
