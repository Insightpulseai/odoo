# IPAI PPM A1 Control Center

## 1. Overview
A1 Control Center - Workstreams, Templates, Tasks, Checks + Seed Import/Export

**Technical Name**: `ipai_ppm_a1`
**Category**: Project/Portfolio
**Version**: 18.0.1.0.0
**Author**: IPAI

## 2. Functional Scope

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
- Hierarchical template structure (phase → workstream → template → steps)
- Idempotent seed import with external key mapping
- Webhook support for n8n integration
- Multi-company aware with record rules
    

## 3. Installation & Dependencies
Dependencies (CE/OCA):
- `base`
- `mail`
- `project`

## 4. Configuration
Key system parameters or settings groups:
- (Audit Pending)

## 5. Data Model
Defined Models:
- `a1.role`
- `a1.check`
- `a1.task.checklist`
- `a1.tasklist`
- `a1.check.result`
- `a1.task`
- `a1.export.run`
- `a1.template`
- `a1.template.checklist`
- `a1.template.step`
- `a1.workstream`

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
odoo-bin -d <db> -i ipai_ppm_a1 --stop-after-init

# Upgrade
odoo-bin -d <db> -u ipai_ppm_a1 --stop-after-init
```