# IPAI Module Namespace

## Overview

InsightPulse AI namespace for Odoo CE modules

- **Technical Name:** `ipai`
- **Version:** 18.0.1.0.0
- **Category:** Hidden
- **License:** AGPL-3
- **Author:** InsightPulse AI
- **Application:** No
- **Installable:** Yes

## Business Use Case

This is a namespace module for all IPAI (InsightPulse AI) custom modules.
        It provides the base namespace for the module hierarchy.

## Functional Scope

### Views

- : 65
- Form: 58
- Search: 31
- Calendar: 6
- Kanban: 9
- Tree: 12
- Pivot: 8
- Graph: 10

### Menus

- `menu_assets_root`: Assets
- `menu_assets`: Assets
- `menu_checkouts`: Checkouts
- `menu_reservations`: Reservations
- `menu_assets_config`: Configuration
- ... and 109 more

## Installation & Dependencies

### Dependencies

- `base` (CE Core)

### Installation

```bash
# Install module
odoo-bin -d <database> -i ipai --stop-after-init

# Upgrade module
odoo-bin -d <database> -u ipai --stop-after-init
```

## Configuration

### System Parameters

- `web.base.url.redirect`: /odoo
- `master_control.webhook_url`: http://localhost:8788
- `master_control.tenant_id`: 00000000-0000-0000-0000-000000000001
- `master_control.enabled`: true
- `master_control.events.employee_hire`: true
- `master_control.events.employee_departure`: true
- `master_control.events.expense_submit`: true
- `master_control.events.purchase_large`: true
- `master_control.expense_threshold`: 1000.0
- `master_control.purchase_threshold`: 5000.0
- `bir.reminder.mattermost.webhook`: https://mattermost.insightpulseai.net/hooks/REPLACE_WITH_ACTUAL_WEBHOOK_ID
- `bir.reminder.n8n.webhook`: https://ipa.insightpulseai.net/webhook/bir-reminder
- `bir.overdue.n8n.webhook`: https://ipa.insightpulseai.net/webhook/bir-overdue-nudge
- `web.base.url.redirect`: /odoo
- `mail.default_template_header_color`: #111111
- `mail.default_template_button_color`: #F9D000
- `auth_signup.allow_uninvited`: False
- `auth_signup.invitation_scope`: b2b
- `auth_signup.reset_password`: True

### Scheduled Actions

- **Create Next Month's Close Schedule** (Active)
- **Send Daily Task Reminders** (Active)
- **IPAI Finance: Seed if Empty** (Active)
- **Finance PPM: Generate Daily Tasks** (Active)
- **BIR Deadline Reminder - 9AM** (Active)
- **BIR Deadline Reminder - 5PM** (Active)
- **BIR Overdue Daily Nudge** (Active)
- **Generate Month-End Close Tasks** (Inactive)
- **Check BIR Filing Tasks** (Inactive)
- **IPAI: Generate Month-End Close (Monthly)** (Active)
- **Close: Send Due Reminders** (Active)
- **Close: Auto-Escalate Exceptions** (Active)
- **Close: Check Approval Gates** (Active)

## Security

### Security Groups

- `group_assets_user`: Asset User
- `group_assets_manager`: Asset Manager
- `group_assets_admin`: Asset Administrator
- `group_studio_ai_user`: Studio AI User
- `group_studio_ai_admin`: Studio AI Administrator
- `group_ppm_user`: PPM User
- `group_ppm_manager`: PPM Manager
- `group_ppm_admin`: PPM Administrator
- `group_advisor_user`: Advisor User
- `group_advisor_manager`: Advisor Manager
- `group_advisor_admin`: Advisor Administrator
- `group_ipai_finance_user`: IPAI Finance User
- `group_ipai_finance_manager`: IPAI Finance Manager
- `group_ipai_ai_studio_admin`: AI Studio Admin
- `group_finance_ppm_user`: Finance PPM User
- `group_finance_ppm_manager`: Finance PPM Manager
- `group_finance_ppm_admin`: Finance PPM Administrator
- `group_a1_user`: User
- `group_a1_manager`: Manager
- `group_a1_admin`: Administrator
- `group_close_user`: User
- `group_close_manager`: Manager
- `group_close_admin`: Administrator
- `group_srm_user`: SRM User
- `group_srm_manager`: SRM Manager
- `group_srm_admin`: SRM Administrator
- `group_ipai_expense_user`: Employee (User)
- `group_ipai_expense_manager`: Manager
- `group_ipai_expense_finance`: Finance Director

### Record Rules

- `rule_month_end_template_internal`: Month-End Templates - Internal Users
- `rule_month_end_template_step_internal`: Month-End Template Steps - Internal Users
- `rule_generate_month_end_wizard_internal`: Generate Month-End Wizard - Internal Users
- `rule_studio_ai_history_user`: Studio AI History: Users see own records
- `rule_studio_ai_history_admin`: Studio AI History: Admins see all
- `rule_bir_schedule_item_internal`: BIR Schedule Items - Internal Users
- `rule_bir_schedule_step_internal`: BIR Schedule Steps - Internal Users
- `rule_generate_bir_tasks_wizard_internal`: Generate BIR Tasks Wizard - Internal Users
- `finance_ppm_audit_user_rule`: Finance PPM Audit: User Access
- `finance_ppm_audit_manager_rule`: Finance PPM Audit: Manager Access
- `finance_ppm_audit_admin_rule`: Finance PPM Audit: Admin Access
- `a1_workstream_company_rule`: A1 Workstream: Company
- `a1_template_company_rule`: A1 Template: Company
- `a1_tasklist_company_rule`: A1 Tasklist: Company
- `a1_task_company_rule`: A1 Task: Company
- `a1_role_company_rule`: A1 Role: Company
- `a1_check_company_rule`: A1 Check: Company
- `rule_directory_person_internal`: Directory Persons - Internal Users
- `rule_convert_phases_wizard_internal`: Convert Phases Wizard - Internal Users
- `close_cycle_company_rule`: Close Cycle: Company
- `close_task_company_rule`: Close Task: Company
- `close_template_company_rule`: Close Template: Company
- `close_category_company_rule`: Close Category: Company
- `close_exception_company_rule`: Close Exception: Company
- `close_gate_company_rule`: Close Gate: Company
- `expense_rule_user_own`: Employee: Own Expenses Only
- `expense_rule_manager_team`: Manager: Team Expenses
- `expense_rule_finance_all`: Finance: All Expenses
- `travel_request_rule_user_own`: Employee: Own Travel Requests Only
- `travel_request_rule_manager_team`: Manager: Team Travel Requests
- `travel_request_rule_finance_all`: Finance: All Travel Requests

## Integrations

*No external integrations.*

## Upgrade Notes

- Current Version: 18.0.1.0.0
- No breaking changes documented

## Verification Steps

```bash
# 1. Verify module is installed
psql -d <database> -c "SELECT name, state FROM ir_module_module WHERE name = 'ipai'"

# 2. Check module info
odoo-bin shell -d <database> -c 'print(env["ir.module.module"].search([("name", "=", "ipai")]).state)'
```

## Static Validation Status

- Passed: 4
- Warnings: 0
- Failed: 0
