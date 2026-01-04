# PPM Monthly Close Scheduler

## 1. Overview
Automated monthly financial close scheduling with PPM and Notion workspace parity

**Technical Name**: `ipai_ppm_monthly_close`
**Category**: Project Management
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## 2. Functional Scope

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
* Multi-agency support (RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB)
* Role-based workflow (Owner → Reviewer → Approver)
* Gantt visualization
* Status tracking (To Do → In Progress → For Review → For Approval → Done)

Integration:
------------
* ipai_ppm_portfolio - Portfolio/program/project hierarchy
* project - Core Odoo project management
* mail - Activity tracking and notifications
* n8n - Automation workflows
    

## 3. Installation & Dependencies
Dependencies (CE/OCA):
- `base`
- `project`
- `mail`
- `resource`

## 4. Configuration
Key system parameters or settings groups:
- (Audit Pending)

## 5. Data Model
Defined Models:
- `ppm.close.task`
- `ppm.monthly.close`
- `ppm.close.template`

## 6. User Interface
- **Views**: 6 files
- **Menus**: (Audit Pending)

## 7. Security
- **Access Rules**: `ir.model.access.csv` found
- **Groups**: `security.xml` not found

## 8. Integrations
- (Audit Pending)

## 9. Verification Steps
```bash
# Install
odoo-bin -d <db> -i ipai_ppm_monthly_close --stop-after-init

# Upgrade
odoo-bin -d <db> -u ipai_ppm_monthly_close --stop-after-init
```