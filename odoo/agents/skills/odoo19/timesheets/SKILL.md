---
name: timesheets
description: Time tracking for projects and tasks with billing rate targets, leaderboards, and time-off integration
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# timesheets -- Odoo 19.0 Skill Reference

## Overview

Odoo Timesheets tracks time spent by employees on project tasks. It supports billable and non-billable time logging, billing rate indicators with employee targets, gamified leaderboards, and automatic time-off entries. Timesheets integrate with Project (task-level tracking), Sales (invoicing based on timesheets), Helpdesk (ticket time tracking), Planning (shift progress), and HR Time Off (automatic entries for approved leave). Used by employees, project managers, and billing/finance teams.

## Key Concepts

- **Timesheet Entry**: A record of time spent by an employee on a specific project/task, with date, hours, and optional description.
- **Billing Rate**: The ratio of billable hours to total hours logged, displayed as a percentage.
- **Billing Time Target**: Monthly target hours of billable time set per employee.
- **Leaderboard**: Gamified ranking of employees by billing rate or total time logged.
- **Encoding Method**: How time is entered -- in **hours** or **days**.
- **Time Off Entry**: Auto-generated timesheet entry for approved time off requests and public holidays.
- **Billable vs. Non-Billable**: Time logged on projects linked to sales orders is billable; time on internal projects is non-billable.

## Core Workflows

### 1. Log Time on Tasks

1. Open a project task (via **Project** or **Timesheets** app).
2. Go to the **Timesheets** tab.
3. Click **Add a line**.
4. Select the **Date**, **Employee**, optionally add a **Description**.
5. Enter **Hours Spent**.
6. The **Allocated Time** percentage and **Remaining Hours** update automatically.

### 2. Log Time via Grid View

1. Navigate to **Timesheets > My Timesheets** (grid view).
2. The grid shows days as columns and project/task combinations as rows.
3. Click a cell to enter hours for that day and task.
4. Add new rows by clicking **Add a line** and selecting project/task.

### 3. Configure Billing Rate Indicators

1. Navigate to **Timesheets > Configuration > Settings**.
2. Enable **Billing Rate Indicators**, click **Save**.
3. Click **Set employee billable time targets**.
4. On the employee form, **Settings** tab, set the **Billing Time Target** (monthly hours or days).
5. Billing rate indicators appear in the top-right of **My Timesheets** view showing: `logged billable / target` and completion percentage (green if met, red if below).

### 4. Enable and Use Leaderboard

1. In **Timesheets > Configuration > Settings**, enable **Billing Rate Leaderboard**, click **Save**.
2. The leaderboard appears alongside billing rate indicators in **My Timesheets**.
3. It shows the top 3 performers by billing rate percentage.
4. Click the leaderboard area to see all team members.
5. Switch between **Billing Rate Leaderboard** and **Total Time Leaderboard** via the dropdown.

### 5. Configure Time Off Entries

1. Activate developer mode.
2. Navigate to **Timesheets > Configuration > Settings**.
3. Enable **Time Off** checkbox in the Time Off section.
4. Configure the **Project** (default: Internal) and **Task** (default: Time Off) for time-off entries.
5. When an employee's time off is approved, timesheet entries are auto-created on the configured project/task.

## Technical Reference

### Models

| Model | Description |
|-------|-------------|
| `account.analytic.line` | Timesheet entries (shared with analytic accounting) |
| `project.project` | Projects (timesheets are logged against these) |
| `project.task` | Tasks (timesheets are logged against these) |
| `hr.employee` | Employees (with billing time target) |

### Key Fields on `account.analytic.line` (Timesheet Mode)

| Field | Type | Description |
|-------|------|-------------|
| `project_id` | Many2one | Project |
| `task_id` | Many2one | Task |
| `employee_id` | Many2one | Employee who logged time |
| `date` | Date | Date of work |
| `unit_amount` | Float | Hours (or days) spent |
| `name` | Char | Description of work |
| `so_line` | Many2one | Linked sales order line |
| `amount` | Monetary | Cost amount (based on employee hourly cost) |

### Key Fields on `hr.employee` (Timesheet-Related)

| Field | Type | Description |
|-------|------|-------------|
| `timesheet_cost` | Float | Employee hourly cost |
| `billing_time_target` | Float | Monthly billable time target |

### Leaderboard Tips

- Tips are stored as records and displayed randomly each day on the leaderboard.
- Manage tips at **Timesheets > Configuration > Tips**.

### Menu Paths

- My Timesheets: `Timesheets > My Timesheets`
- All Timesheets: `Timesheets > All Timesheets`
- Configuration: `Timesheets > Configuration > Settings / Tips`

## API / RPC Patterns

<!-- TODO: Timesheets-specific external API examples not found in docs -->

Standard ORM access:

```python
# Log a timesheet entry
env['account.analytic.line'].create({
    'project_id': project_id,
    'task_id': task_id,
    'employee_id': employee_id,
    'date': '2026-02-18',
    'unit_amount': 3.5,
    'name': 'Implemented login feature',
})

# Get total hours for a task
entries = env['account.analytic.line'].search([('task_id', '=', task_id)])
total = sum(entries.mapped('unit_amount'))
```

## Version Notes (19.0)

<!-- TODO: Specific 18-to-19 breaking changes not documented in the reviewed RST files. -->

- Billing rate indicators and leaderboards are optional features enabled in settings.
- Time-off integration requires developer mode to access the configuration setting.
- Encoding method (hours vs. days) is configurable in Timesheets settings and affects billing time targets.
- Timesheet entries use `account.analytic.line` model (shared with analytic accounting), not a dedicated model.

## Common Pitfalls

- **Timesheet model is shared**: Timesheet entries live in `account.analytic.line`, which is also used for analytic accounting. Filtering by `project_id != False` is necessary to isolate timesheet entries.
- **Time-off entries require developer mode to configure**: The Time Off setting in Timesheets is only visible in developer mode, which can be confusing for administrators.
- **Billing rate target is per employee**: There is no team-level target. Each employee must have their individual target set, or the indicator shows 0%.
- **Hours vs. days encoding**: Switching the encoding method after data has been entered does not retroactively convert existing entries. Consistency is important.
- **Time off without validation creates immediate timesheets**: Time off types that do not require approval generate timesheet entries instantly upon request, which may surprise managers.
