# IPAI Close Cycle Orchestration

## Overview

Close Cycle Orchestration - Cycles, Tasks, Templates, Checklists, Exceptions, Gates

- **Technical Name:** `ipai_close_orchestration`
- **Version:** 18.0.1.0.0
- **Category:** Accounting/Close
- **License:** LGPL-3
- **Author:** IPAI
- **Application:** Yes
- **Installable:** Yes

## Business Use Case

IPAI Close Cycle Orchestration
==============================

Execution engine for month-end close and periodic closing processes.

Key Components:
- Close Cycles: Period-based closing runs
- Close Tasks: Individual close items with workflow
- Templates: Reusable task definitions
- Categories: Organizational groupings
- Checklists: Verification items
- Exceptions: Issue tracking and escalation
- Approval Gates: Control checkpoints

Workflow:
- prep → review → approval → done

Automation:
- Cron...

## Functional Scope

### Data Models

- **close.exception** (Model)
  - Close Exception
  - Fields: 17 defined
- **close.approval.gate.template** (Model)
  - Close Approval Gate Template
  - Fields: 9 defined
- **close.approval.gate** (Model)
  - Close Approval Gate
  - Fields: 14 defined
- **close.task.category** (Model)
  - Close Task Category
  - Fields: 9 defined
- **close.task.template** (Model)
  - Close Task Template
  - Fields: 21 defined
- **close.task.template.checklist** (Model)
  - Close Task Template Checklist
  - Fields: 6 defined
- **close.task** (Model)
  - Close Task
  - Fields: 26 defined
- **close.task.checklist** (Model)
  - Close Task Checklist
  - Fields: 9 defined
- **close.cycle** (Model)
  - Close Cycle
  - Fields: 18 defined

### Views

- : 7
- Form: 7
- Search: 5
- Kanban: 1

### Menus

- `close_menu_root`: Close Orchestration
- `close_menu_operations`: Operations
- `close_menu_cycles`: Close Cycles
- `close_menu_tasks`: Tasks
- `close_menu_exceptions`: Exceptions
- ... and 5 more

## Installation & Dependencies

### Dependencies

- `base` (CE Core)
- `mail` (CE Core)

### Installation

```bash
# Install module
odoo-bin -d <database> -i ipai_close_orchestration --stop-after-init

# Upgrade module
odoo-bin -d <database> -u ipai_close_orchestration --stop-after-init
```

## Configuration

*No specific configuration required.*

### Scheduled Actions

- **Close: Send Due Reminders** (Active)
- **Close: Auto-Escalate Exceptions** (Active)
- **Close: Check Approval Gates** (Active)

## Security

### Security Groups

- `group_close_user`: User
- `group_close_manager`: Manager
- `group_close_admin`: Administrator

### Access Rules

*27 access rules defined in ir.model.access.csv*

### Record Rules

- `close_cycle_company_rule`: Close Cycle: Company
- `close_task_company_rule`: Close Task: Company
- `close_template_company_rule`: Close Template: Company
- `close_category_company_rule`: Close Category: Company
- `close_exception_company_rule`: Close Exception: Company
- `close_gate_company_rule`: Close Gate: Company

## Integrations

- Odoo Mail (Email notifications)

## Upgrade Notes

- Current Version: 18.0.1.0.0
- No breaking changes documented

## Verification Steps

```bash
# 1. Verify module is installed
psql -d <database> -c "SELECT name, state FROM ir_module_module WHERE name = 'ipai_close_orchestration'"

# 2. Check module info
odoo-bin shell -d <database> -c 'print(env["ir.module.module"].search([("name", "=", "ipai_close_orchestration")]).state)'
```

## Data Files

- `security/close_security.xml`
- `security/ir.model.access.csv`
- `data/close_cron.xml`
- `views/close_cycle_views.xml`
- `views/close_task_views.xml`
- `views/close_template_views.xml`
- `views/close_exception_views.xml`
- `views/close_gate_views.xml`
- `views/close_menu.xml`

## Static Validation Status

- Passed: 5
- Warnings: 0
- Failed: 0
