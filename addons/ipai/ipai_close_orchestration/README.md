# IPAI Close Cycle Orchestration

## 1. Overview
Close Cycle Orchestration - Cycles, Tasks, Templates, Checklists, Exceptions, Gates

**Technical Name**: `ipai_close_orchestration`
**Category**: Accounting/Close
**Version**: 18.0.1.0.0
**Author**: IPAI

## 2. Functional Scope

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
- Cron for due date reminders
- Cron for exception auto-escalation
- Cron for gate status checks
- Webhook events for n8n integration

Bridged from A1 Control Center (ipai_ppm_a1) for seamless
configuration-to-execution flow.
    

## 3. Installation & Dependencies
Dependencies (CE/OCA):
- `base`
- `mail`

## 4. Configuration
Key system parameters or settings groups:
- (Audit Pending)

## 5. Data Model
Defined Models:
- `close.approval.gate`
- `close.task.checklist`
- `close.approval.gate.template`
- `close.cycle`
- `close.exception`
- `close.task.category`
- `close.task.template`
- `close.task.template.checklist`
- `close.task`

## 6. User Interface
- **Views**: 8 files
- **Menus**: (Audit Pending)

## 7. Security
- **Access Rules**: `ir.model.access.csv` found
- **Groups**: `security.xml` not found

## 8. Integrations
- (Audit Pending)

## 9. Verification Steps
```bash
# Install
odoo-bin -d <db> -i ipai_close_orchestration --stop-after-init

# Upgrade
odoo-bin -d <db> -u ipai_close_orchestration --stop-after-init
```