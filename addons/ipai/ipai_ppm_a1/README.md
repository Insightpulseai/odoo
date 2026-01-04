# IPAI PPM A1 Control Center

## Overview

A1 Control Center - Workstreams, Templates, Tasks, Checks + Seed Import/Export

- **Technical Name:** `ipai_ppm_a1`
- **Version:** 18.0.1.0.0
- **Category:** Project/Portfolio
- **License:** LGPL-3
- **Author:** IPAI
- **Application:** Yes
- **Installable:** Yes

## Business Use Case

IPAI PPM A1 Control Center
==========================

A1 Control Center for managing:
- Workstreams (organizational units)
- Task Templates (reusable task definitions)
- Tasks (period-specific instances)
- Checks/Scenarios (STC validation rules)
- Seed Import/Export (YAML-based configuration)

This module provides the "A1" layer that can instantiate into
close cycles via the ipai_close_orchestration module.

Key Features:
- Role-based workstream assignment (RIM, JPAL, BOM, CKVC, etc.)
- Hierarc...

## Functional Scope

### Data Models

- **a1.task** (Model)
  - A1 Task
  - Fields: 27 defined
- **a1.task.checklist** (Model)
  - A1 Task Checklist Item
  - Fields: 12 defined
- **a1.template** (Model)
  - A1 Task Template
  - Fields: 18 defined
- **a1.template.step** (Model)
  - A1 Template Step
  - Fields: 7 defined
- **a1.template.checklist** (Model)
  - A1 Template Checklist Item
  - Fields: 7 defined
- **a1.role** (Model)
  - A1 Role Configuration
  - Fields: 9 defined
- **a1.tasklist** (Model)
  - A1 Tasklist (Period Run)
  - Fields: 13 defined
- **a1.check** (Model)
  - A1 Check / STC Scenario
  - Fields: 12 defined
- **a1.check.result** (Model)
  - A1 Check Result
  - Fields: 8 defined
- **a1.workstream** (Model)
  - A1 Workstream
  - Fields: 12 defined
- **a1.export.run** (Model)
  - A1 Seed Export/Import Run
  - Fields: 11 defined

### Views

- : 6
- Form: 6
- Search: 5
- Kanban: 1

### Menus

- `a1_menu_root`: A1 Control Center
- `a1_menu_operations`: Operations
- `a1_menu_tasklists`: Tasklists
- `a1_menu_tasks`: Tasks
- `a1_menu_config`: Configuration
- ... and 4 more

## Installation & Dependencies

### Dependencies

- `base` (CE Core)
- `mail` (CE Core)
- `project` (CE Core)

### Installation

```bash
# Install module
odoo-bin -d <database> -i ipai_ppm_a1 --stop-after-init

# Upgrade module
odoo-bin -d <database> -u ipai_ppm_a1 --stop-after-init
```

## Configuration

*No specific configuration required.*

## Security

### Security Groups

- `group_a1_user`: User
- `group_a1_manager`: Manager
- `group_a1_admin`: Administrator

### Access Rules

*33 access rules defined in ir.model.access.csv*

### Record Rules

- `a1_workstream_company_rule`: A1 Workstream: Company
- `a1_template_company_rule`: A1 Template: Company
- `a1_tasklist_company_rule`: A1 Tasklist: Company
- `a1_task_company_rule`: A1 Task: Company
- `a1_role_company_rule`: A1 Role: Company
- `a1_check_company_rule`: A1 Check: Company

## Integrations

- Odoo Mail (Email notifications)

## Upgrade Notes

- Current Version: 18.0.1.0.0
- No breaking changes documented

## Verification Steps

```bash
# 1. Verify module is installed
psql -d <database> -c "SELECT name, state FROM ir_module_module WHERE name = 'ipai_ppm_a1'"

# 2. Check module info
odoo-bin shell -d <database> -c 'print(env["ir.module.module"].search([("name", "=", "ipai_ppm_a1")]).state)'
```

## Data Files

- `security/a1_security.xml`
- `security/ir.model.access.csv`
- `data/a1_role_data.xml`
- `views/a1_workstream_views.xml`
- `views/a1_template_views.xml`
- `views/a1_task_views.xml`
- `views/a1_tasklist_views.xml`
- `views/a1_check_views.xml`
- `views/a1_menu.xml`

## Static Validation Status

- Passed: 5
- Warnings: 0
- Failed: 0
