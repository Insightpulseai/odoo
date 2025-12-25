# ipai_ppm_a1

**Module**: `ipai_ppm_a1`
**Version**: `unknown`
**Category**: `uncategorized`
**License**: `LGPL-3`
**Author**: `Unknown`
**Website**: ``

---

## Overview

**Summary**: No summary provided

**Description**: No description provided

**Installable**: ❌ No
**Application**: ❌ No (library/integration module)
**Auto-Install**: ❌ No (manual install required)

---

## Dependencies

**Odoo Core Modules**:
- None (base module only)

**IPAI Module Dependencies**:
- None (no IPAI dependencies)

---

## Data Model

**Total Models**: 11

### Model: `a1.export.run`

**Description**: A1 Seed Export/Import Run

**Python Class**: `A1ExportRun`  
**File**: `addons/ipai/ipai_ppm_a1/models/export_run.py`

**Fields**:

| Field Name | Type | File |
|------------|------|------|
| `run_type` | Selection | export_run.py |
| `status` | Selection | export_run.py |
| `seed_json` | Text | export_run.py |
| `seed_hash` | Char | export_run.py |
| `created_count` | Integer | export_run.py |
| `updated_count` | Integer | export_run.py |
| `unchanged_count` | Integer | export_run.py |
| `error_count` | Integer | export_run.py |
| `log` | Text | export_run.py |
| `company_id` | Many2one | export_run.py |
| `webhook_url` | Char | export_run.py |

### Model: `a1.workstream`

**Description**: A1 Workstream

**Python Class**: `A1Workstream`  
**File**: `addons/ipai/ipai_ppm_a1/models/a1_workstream.py`

**Fields**:

| Field Name | Type | File |
|------------|------|------|
| `code` | Char | a1_workstream.py |
| `name` | Char | a1_workstream.py |
| `sequence` | Integer | a1_workstream.py |
| `active` | Boolean | a1_workstream.py |
| `phase_code` | Char | a1_workstream.py |
| `owner_role_id` | Many2one | a1_workstream.py |
| `owner_user_id` | Many2one | a1_workstream.py |
| `template_ids` | One2many | a1_workstream.py |
| `template_count` | Integer | a1_workstream.py |
| `company_id` | Many2one | a1_workstream.py |
| `close_category_id` | Many2one | a1_workstream.py |

### Model: `a1.task`

**Description**: A1 Task

**Python Class**: `A1Task`  
**File**: `addons/ipai/ipai_ppm_a1/models/a1_task.py`

**Fields**:

| Field Name | Type | File |
|------------|------|------|
| `name` | Char | a1_task.py |
| `sequence` | Integer | a1_task.py |
| `tasklist_id` | Many2one | a1_task.py |
| `template_id` | Many2one | a1_task.py |
| `workstream_id` | Many2one | a1_task.py |
| `external_key` | Char | a1_task.py |
| `owner_role` | Char | a1_task.py |
| `owner_id` | Many2one | a1_task.py |
| `reviewer_role` | Char | a1_task.py |
| `reviewer_id` | Many2one | a1_task.py |
| `approver_role` | Char | a1_task.py |
| `approver_id` | Many2one | a1_task.py |
| `prep_deadline` | Date | a1_task.py |
| `review_deadline` | Date | a1_task.py |
| `approval_deadline` | Date | a1_task.py |
| `state` | Selection | a1_task.py |
| `prep_done_date` | Datetime | a1_task.py |
| `prep_done_by` | Many2one | a1_task.py |
| `review_done_date` | Datetime | a1_task.py |
| `review_done_by` | Many2one | a1_task.py |
| `approval_done_date` | Datetime | a1_task.py |
| `approval_done_by` | Many2one | a1_task.py |
| `checklist_ids` | One2many | a1_task.py |
| `checklist_progress` | Float | a1_task.py |
| `company_id` | Many2one | a1_task.py |
| `close_task_id` | Many2one | a1_task.py |

### Model: `a1.task.checklist`

**Description**: A1 Task Checklist Item

**Python Class**: `A1TaskChecklist`  
**File**: `addons/ipai/ipai_ppm_a1/models/a1_task.py`

**Fields**:

| Field Name | Type | File |
|------------|------|------|
| `task_id` | Many2one | a1_task.py |
| `template_item_id` | Many2one | a1_task.py |
| `code` | Char | a1_task.py |
| `name` | Char | a1_task.py |
| `sequence` | Integer | a1_task.py |
| `item_type` | Selection | a1_task.py |
| `is_required` | Boolean | a1_task.py |
| `is_done` | Boolean | a1_task.py |
| `value_text` | Text | a1_task.py |
| `value_attachment_id` | Many2one | a1_task.py |
| `done_date` | Datetime | a1_task.py |
| `done_by` | Many2one | a1_task.py |

### Model: `a1.template`

**Description**: A1 Task Template

**Python Class**: `A1Template`  
**File**: `addons/ipai/ipai_ppm_a1/models/a1_template.py`

**Fields**:

| Field Name | Type | File |
|------------|------|------|
| `code` | Char | a1_template.py |
| `name` | Char | a1_template.py |
| `sequence` | Integer | a1_template.py |
| `active` | Boolean | a1_template.py |
| `workstream_id` | Many2one | a1_template.py |
| `phase_code` | Char | a1_template.py |
| `owner_role` | Char | a1_template.py |
| `reviewer_role` | Char | a1_template.py |
| `approver_role` | Char | a1_template.py |
| `prep_days` | Float | a1_template.py |
| `review_days` | Float | a1_template.py |
| `approval_days` | Float | a1_template.py |
| `total_days` | Float | a1_template.py |
| `step_ids` | One2many | a1_template.py |
| `checklist_ids` | One2many | a1_template.py |
| `company_id` | Many2one | a1_template.py |
| `close_template_id` | Many2one | a1_template.py |

### Model: `a1.template.step`

**Description**: A1 Template Step

**Python Class**: `A1TemplateStep`  
**File**: `addons/ipai/ipai_ppm_a1/models/a1_template.py`

**Fields**:

| Field Name | Type | File |
|------------|------|------|
| `template_id` | Many2one | a1_template.py |
| `code` | Char | a1_template.py |
| `name` | Char | a1_template.py |
| `sequence` | Integer | a1_template.py |
| `assignee_role` | Char | a1_template.py |
| `effort_days` | Float | a1_template.py |
| `deadline_offset_days` | Integer | a1_template.py |

### Model: `a1.template.checklist`

**Description**: A1 Template Checklist Item

**Python Class**: `A1TemplateChecklist`  
**File**: `addons/ipai/ipai_ppm_a1/models/a1_template.py`

**Fields**:

| Field Name | Type | File |
|------------|------|------|
| `template_id` | Many2one | a1_template.py |
| `code` | Char | a1_template.py |
| `name` | Char | a1_template.py |
| `sequence` | Integer | a1_template.py |
| `item_type` | Selection | a1_template.py |
| `is_required` | Boolean | a1_template.py |
| `instructions` | Text | a1_template.py |

### Model: `a1.tasklist`

**Description**: A1 Tasklist (Period Run)

**Python Class**: `A1Tasklist`  
**File**: `addons/ipai/ipai_ppm_a1/models/a1_tasklist.py`

**Fields**:

| Field Name | Type | File |
|------------|------|------|
| `name` | Char | a1_tasklist.py |
| `period_start` | Date | a1_tasklist.py |
| `period_end` | Date | a1_tasklist.py |
| `period_label` | Char | a1_tasklist.py |
| `state` | Selection | a1_tasklist.py |
| `task_ids` | One2many | a1_tasklist.py |
| `task_count` | Integer | a1_tasklist.py |
| `task_done_count` | Integer | a1_tasklist.py |
| `progress` | Float | a1_tasklist.py |
| `company_id` | Many2one | a1_tasklist.py |
| `close_cycle_id` | Many2one | a1_tasklist.py |
| `webhook_url` | Char | a1_tasklist.py |

### Model: `a1.check`

**Description**: A1 Check / STC Scenario

**Python Class**: `A1Check`  
**File**: `addons/ipai/ipai_ppm_a1/models/a1_check.py`

**Fields**:

| Field Name | Type | File |
|------------|------|------|
| `code` | Char | a1_check.py |
| `name` | Char | a1_check.py |
| `sequence` | Integer | a1_check.py |
| `active` | Boolean | a1_check.py |
| `check_type` | Selection | a1_check.py |
| `severity` | Selection | a1_check.py |
| `template_ids` | Many2many | a1_check.py |
| `pass_criteria` | Text | a1_check.py |
| `fail_action` | Text | a1_check.py |
| `company_id` | Many2one | a1_check.py |
| `close_gate_template_id` | Many2one | a1_check.py |

### Model: `a1.check.result`

**Description**: A1 Check Result

**Python Class**: `A1CheckResult`  
**File**: `addons/ipai/ipai_ppm_a1/models/a1_check.py`

**Fields**:

| Field Name | Type | File |
|------------|------|------|
| `check_id` | Many2one | a1_check.py |
| `task_id` | Many2one | a1_check.py |
| `result` | Selection | a1_check.py |
| `result_notes` | Text | a1_check.py |
| `executed_by` | Many2one | a1_check.py |
| `executed_date` | Datetime | a1_check.py |
| `attachment_ids` | Many2many | a1_check.py |

### Model: `a1.role`

**Description**: A1 Role Configuration

**Python Class**: `A1Role`  
**File**: `addons/ipai/ipai_ppm_a1/models/a1_role.py`

**Fields**:

| Field Name | Type | File |
|------------|------|------|
| `code` | Char | a1_role.py |
| `name` | Char | a1_role.py |
| `sequence` | Integer | a1_role.py |
| `active` | Boolean | a1_role.py |
| `group_ids` | Many2many | a1_role.py |
| `default_user_id` | Many2one | a1_role.py |
| `fallback_user_id` | Many2one | a1_role.py |
| `company_id` | Many2one | a1_role.py |
| `description` | Text | a1_role.py |

---

## Security

**Security Groups**: 3

### Group: `group_a1_user`

**Name**: User  
**Category**: `module_category_a1`  
**File**: `addons/ipai/ipai_ppm_a1/security/a1_security.xml`

### Group: `group_a1_manager`

**Name**: Manager  
**Category**: `module_category_a1`  
**File**: `addons/ipai/ipai_ppm_a1/security/a1_security.xml`

### Group: `group_a1_admin`

**Name**: Administrator  
**Category**: `module_category_a1`  
**File**: `addons/ipai/ipai_ppm_a1/security/a1_security.xml`

**Access Rules (ir.model.access.csv)**: 33

| Access ID | Model | Group | Read | Write | Create | Delete |
|-----------|-------|-------|------|-------|--------|--------|
| `access_a1_role_user` | `model_a1_role` | `group_a1_user` | ✅ | ❌ | ❌ | ❌ |
| `access_a1_role_manager` | `model_a1_role` | `group_a1_manager` | ✅ | ✅ | ✅ | ❌ |
| `access_a1_role_admin` | `model_a1_role` | `group_a1_admin` | ✅ | ✅ | ✅ | ✅ |
| `access_a1_workstream_user` | `model_a1_workstream` | `group_a1_user` | ✅ | ❌ | ❌ | ❌ |
| `access_a1_workstream_manager` | `model_a1_workstream` | `group_a1_manager` | ✅ | ✅ | ✅ | ❌ |
| `access_a1_workstream_admin` | `model_a1_workstream` | `group_a1_admin` | ✅ | ✅ | ✅ | ✅ |
| `access_a1_template_user` | `model_a1_template` | `group_a1_user` | ✅ | ❌ | ❌ | ❌ |
| `access_a1_template_manager` | `model_a1_template` | `group_a1_manager` | ✅ | ✅ | ✅ | ❌ |
| `access_a1_template_admin` | `model_a1_template` | `group_a1_admin` | ✅ | ✅ | ✅ | ✅ |
| `access_a1_template_step_user` | `model_a1_template_step` | `group_a1_user` | ✅ | ❌ | ❌ | ❌ |
| `access_a1_template_step_manager` | `model_a1_template_step` | `group_a1_manager` | ✅ | ✅ | ✅ | ❌ |
| `access_a1_template_step_admin` | `model_a1_template_step` | `group_a1_admin` | ✅ | ✅ | ✅ | ✅ |
| `access_a1_template_checklist_user` | `model_a1_template_checklist` | `group_a1_user` | ✅ | ❌ | ❌ | ❌ |
| `access_a1_template_checklist_manager` | `model_a1_template_checklist` | `group_a1_manager` | ✅ | ✅ | ✅ | ❌ |
| `access_a1_template_checklist_admin` | `model_a1_template_checklist` | `group_a1_admin` | ✅ | ✅ | ✅ | ✅ |
| `access_a1_tasklist_user` | `model_a1_tasklist` | `group_a1_user` | ✅ | ❌ | ❌ | ❌ |
| `access_a1_tasklist_manager` | `model_a1_tasklist` | `group_a1_manager` | ✅ | ✅ | ✅ | ❌ |
| `access_a1_tasklist_admin` | `model_a1_tasklist` | `group_a1_admin` | ✅ | ✅ | ✅ | ✅ |
| `access_a1_task_user` | `model_a1_task` | `group_a1_user` | ✅ | ✅ | ❌ | ❌ |
| `access_a1_task_manager` | `model_a1_task` | `group_a1_manager` | ✅ | ✅ | ✅ | ❌ |
| `access_a1_task_admin` | `model_a1_task` | `group_a1_admin` | ✅ | ✅ | ✅ | ✅ |
| `access_a1_task_checklist_user` | `model_a1_task_checklist` | `group_a1_user` | ✅ | ✅ | ❌ | ❌ |
| `access_a1_task_checklist_manager` | `model_a1_task_checklist` | `group_a1_manager` | ✅ | ✅ | ✅ | ❌ |
| `access_a1_task_checklist_admin` | `model_a1_task_checklist` | `group_a1_admin` | ✅ | ✅ | ✅ | ✅ |
| `access_a1_check_user` | `model_a1_check` | `group_a1_user` | ✅ | ❌ | ❌ | ❌ |
| `access_a1_check_manager` | `model_a1_check` | `group_a1_manager` | ✅ | ✅ | ✅ | ❌ |
| `access_a1_check_admin` | `model_a1_check` | `group_a1_admin` | ✅ | ✅ | ✅ | ✅ |
| `access_a1_check_result_user` | `model_a1_check_result` | `group_a1_user` | ✅ | ✅ | ✅ | ❌ |
| `access_a1_check_result_manager` | `model_a1_check_result` | `group_a1_manager` | ✅ | ✅ | ✅ | ❌ |
| `access_a1_check_result_admin` | `model_a1_check_result` | `group_a1_admin` | ✅ | ✅ | ✅ | ✅ |
| `access_a1_export_run_user` | `model_a1_export_run` | `group_a1_user` | ✅ | ❌ | ❌ | ❌ |
| `access_a1_export_run_manager` | `model_a1_export_run` | `group_a1_manager` | ✅ | ✅ | ✅ | ❌ |
| `access_a1_export_run_admin` | `model_a1_export_run` | `group_a1_admin` | ✅ | ✅ | ✅ | ✅ |

**Record Rules (ir.rule)**: 6

### Rule: `a1_workstream_company_rule`

**Name**: A1 Workstream: Company  
**Model**: `model_a1_workstream`  
**Domain**: `[('company_id', 'in', company_ids)]`  
**Groups**: `[(4, ref('group_a1_user'))]`  
**File**: `addons/ipai/ipai_ppm_a1/security/a1_security.xml`

### Rule: `a1_template_company_rule`

**Name**: A1 Template: Company  
**Model**: `model_a1_template`  
**Domain**: `[('company_id', 'in', company_ids)]`  
**Groups**: `[(4, ref('group_a1_user'))]`  
**File**: `addons/ipai/ipai_ppm_a1/security/a1_security.xml`

### Rule: `a1_tasklist_company_rule`

**Name**: A1 Tasklist: Company  
**Model**: `model_a1_tasklist`  
**Domain**: `[('company_id', 'in', company_ids)]`  
**Groups**: `[(4, ref('group_a1_user'))]`  
**File**: `addons/ipai/ipai_ppm_a1/security/a1_security.xml`

### Rule: `a1_task_company_rule`

**Name**: A1 Task: Company  
**Model**: `model_a1_task`  
**Domain**: `[('company_id', 'in', company_ids)]`  
**Groups**: `[(4, ref('group_a1_user'))]`  
**File**: `addons/ipai/ipai_ppm_a1/security/a1_security.xml`

### Rule: `a1_role_company_rule`

**Name**: A1 Role: Company  
**Model**: `model_a1_role`  
**Domain**: `[('company_id', 'in', company_ids)]`  
**Groups**: `[(4, ref('group_a1_user'))]`  
**File**: `addons/ipai/ipai_ppm_a1/security/a1_security.xml`

### Rule: `a1_check_company_rule`

**Name**: A1 Check: Company  
**Model**: `model_a1_check`  
**Domain**: `[('company_id', 'in', company_ids)]`  
**Groups**: `[(4, ref('group_a1_user'))]`  
**File**: `addons/ipai/ipai_ppm_a1/security/a1_security.xml`

---

## UI (Menus, Actions, Views)

**Menus**: 9

| Menu ID | Name | Parent | Action | Sequence | File |
|---------|------|--------|--------|----------|------|
| `a1_menu_root` | A1 Control Center | `` | `` | 40 | a1_menu.xml |
| `a1_menu_operations` | Operations | `a1_menu_root` | `` | 10 | a1_menu.xml |
| `a1_menu_tasklists` | Tasklists | `a1_menu_operations` | `a1_tasklist_action` | 10 | a1_menu.xml |
| `a1_menu_tasks` | Tasks | `a1_menu_operations` | `a1_task_action` | 20 | a1_menu.xml |
| `a1_menu_config` | Configuration | `a1_menu_root` | `` | 20 | a1_menu.xml |
| `a1_menu_workstreams` | Workstreams | `a1_menu_config` | `a1_workstream_action` | 10 | a1_menu.xml |
| `a1_menu_templates` | Task Templates | `a1_menu_config` | `a1_template_action` | 20 | a1_menu.xml |
| `a1_menu_checks` | Checks / STCs | `a1_menu_config` | `a1_check_action` | 30 | a1_menu.xml |
| `a1_menu_roles` | Roles | `a1_menu_config` | `a1_role_action` | 40 | a1_menu.xml |

**Actions**: 6

| Action ID | Name | Model | View Mode | File |
|-----------|------|-------|-----------|------|
| `a1_workstream_action` | Workstreams | `a1.workstream` | list,form | a1_workstream_views.xml |
| `a1_tasklist_action` | Tasklists | `a1.tasklist` | list,form | a1_tasklist_views.xml |
| `a1_template_action` | Task Templates | `a1.template` | list,form | a1_template_views.xml |
| `a1_task_action` | Tasks | `a1.task` | list,kanban,form | a1_task_views.xml |
| `a1_check_action` | Checks / STCs | `a1.check` | list,form | a1_check_views.xml |
| `a1_role_action` | Roles | `a1.role` | list,form | a1_check_views.xml |

**Views**: 18

| View ID | Name | Model | Type | File |
|---------|------|-------|------|------|
| `a1_workstream_view_tree` | a1.workstream.tree | `a1.workstream` |  ⚠️ (deprecated type='xml') | a1_workstream_views.xml |
| `a1_workstream_view_form` | a1.workstream.form | `a1.workstream` | form ⚠️ (deprecated type='xml') | a1_workstream_views.xml |
| `a1_workstream_view_search` | a1.workstream.search | `a1.workstream` | search ⚠️ (deprecated type='xml') | a1_workstream_views.xml |
| `a1_tasklist_view_tree` | a1.tasklist.tree | `a1.tasklist` |  ⚠️ (deprecated type='xml') | a1_tasklist_views.xml |
| `a1_tasklist_view_form` | a1.tasklist.form | `a1.tasklist` | form ⚠️ (deprecated type='xml') | a1_tasklist_views.xml |
| `a1_tasklist_view_search` | a1.tasklist.search | `a1.tasklist` | search ⚠️ (deprecated type='xml') | a1_tasklist_views.xml |
| `a1_template_view_tree` | a1.template.tree | `a1.template` |  ⚠️ (deprecated type='xml') | a1_template_views.xml |
| `a1_template_view_form` | a1.template.form | `a1.template` | form ⚠️ (deprecated type='xml') | a1_template_views.xml |
| `a1_template_view_search` | a1.template.search | `a1.template` | search ⚠️ (deprecated type='xml') | a1_template_views.xml |
| `a1_task_view_tree` | a1.task.tree | `a1.task` |  ⚠️ (deprecated type='xml') | a1_task_views.xml |
| `a1_task_view_form` | a1.task.form | `a1.task` | form ⚠️ (deprecated type='xml') | a1_task_views.xml |
| `a1_task_view_kanban` | a1.task.kanban | `a1.task` | kanban ⚠️ (deprecated type='xml') | a1_task_views.xml |
| `a1_task_view_search` | a1.task.search | `a1.task` | search ⚠️ (deprecated type='xml') | a1_task_views.xml |
| `a1_check_view_tree` | a1.check.tree | `a1.check` |  ⚠️ (deprecated type='xml') | a1_check_views.xml |
| `a1_check_view_form` | a1.check.form | `a1.check` | form ⚠️ (deprecated type='xml') | a1_check_views.xml |
| `a1_check_view_search` | a1.check.search | `a1.check` | search ⚠️ (deprecated type='xml') | a1_check_views.xml |
| `a1_role_view_tree` | a1.role.tree | `a1.role` |  ⚠️ (deprecated type='xml') | a1_check_views.xml |
| `a1_role_view_form` | a1.role.form | `a1.role` | form ⚠️ (deprecated type='xml') | a1_check_views.xml |

---

## Automation

**No scheduled actions found**

---

## Integrations

**No HTTP controllers found**

---

## Configuration

**No data or demo files declared**

---

## Operational

### Installation

```bash
# Install module
odoo -d <database> -i ipai_ppm_a1 --stop-after-init
```

### Upgrade

```bash
# Upgrade module
odoo -d <database> -u ipai_ppm_a1 --stop-after-init
```

### ⚠️ Odoo 18 Compatibility Issues

**CRITICAL**: The following issues must be fixed before installation on Odoo 18:

⚠️ Deprecated `type="xml"` attribute in view: `a1_workstream_view_tree` (addons/ipai/ipai_ppm_a1/views/a1_workstream_views.xml)

⚠️ Deprecated `type="xml"` attribute in view: `a1_workstream_view_form` (addons/ipai/ipai_ppm_a1/views/a1_workstream_views.xml)

⚠️ Deprecated `type="xml"` attribute in view: `a1_workstream_view_search` (addons/ipai/ipai_ppm_a1/views/a1_workstream_views.xml)

⚠️ Deprecated `type="xml"` attribute in view: `a1_tasklist_view_tree` (addons/ipai/ipai_ppm_a1/views/a1_tasklist_views.xml)

⚠️ Deprecated `type="xml"` attribute in view: `a1_tasklist_view_form` (addons/ipai/ipai_ppm_a1/views/a1_tasklist_views.xml)

⚠️ Deprecated `type="xml"` attribute in view: `a1_tasklist_view_search` (addons/ipai/ipai_ppm_a1/views/a1_tasklist_views.xml)

⚠️ Deprecated `type="xml"` attribute in view: `a1_template_view_tree` (addons/ipai/ipai_ppm_a1/views/a1_template_views.xml)

⚠️ Deprecated `type="xml"` attribute in view: `a1_template_view_form` (addons/ipai/ipai_ppm_a1/views/a1_template_views.xml)

⚠️ Deprecated `type="xml"` attribute in view: `a1_template_view_search` (addons/ipai/ipai_ppm_a1/views/a1_template_views.xml)

⚠️ Deprecated `type="xml"` attribute in view: `a1_task_view_tree` (addons/ipai/ipai_ppm_a1/views/a1_task_views.xml)

⚠️ Deprecated `type="xml"` attribute in view: `a1_task_view_form` (addons/ipai/ipai_ppm_a1/views/a1_task_views.xml)

⚠️ Deprecated `type="xml"` attribute in view: `a1_task_view_kanban` (addons/ipai/ipai_ppm_a1/views/a1_task_views.xml)

⚠️ Deprecated `type="xml"` attribute in view: `a1_task_view_search` (addons/ipai/ipai_ppm_a1/views/a1_task_views.xml)

⚠️ Deprecated `type="xml"` attribute in view: `a1_check_view_tree` (addons/ipai/ipai_ppm_a1/views/a1_check_views.xml)

⚠️ Deprecated `type="xml"` attribute in view: `a1_check_view_form` (addons/ipai/ipai_ppm_a1/views/a1_check_views.xml)

⚠️ Deprecated `type="xml"` attribute in view: `a1_check_view_search` (addons/ipai/ipai_ppm_a1/views/a1_check_views.xml)

⚠️ Deprecated `type="xml"` attribute in view: `a1_role_view_tree` (addons/ipai/ipai_ppm_a1/views/a1_check_views.xml)

⚠️ Deprecated `type="xml"` attribute in view: `a1_role_view_form` (addons/ipai/ipai_ppm_a1/views/a1_check_views.xml)

**Fix Procedure**:
1. Edit the affected files
2. Remove deprecated fields/attributes
3. Test installation in staging environment
4. Commit fixes with descriptive message

---

## Verification

### Module Installation Check

```sql
-- Verify module installed
SELECT name, state, latest_version
FROM ir_module_module
WHERE name = 'ipai_ppm_a1';
-- Expected: state='installed', latest_version='unknown'
```

### Data Model Verification

```sql
-- Verify tables created
SELECT COUNT(*) FROM a1_export_run;  -- a1.export.run
SELECT COUNT(*) FROM a1_workstream;  -- a1.workstream
SELECT COUNT(*) FROM a1_task;  -- a1.task
SELECT COUNT(*) FROM a1_task_checklist;  -- a1.task.checklist
SELECT COUNT(*) FROM a1_template;  -- a1.template
SELECT COUNT(*) FROM a1_template_step;  -- a1.template.step
SELECT COUNT(*) FROM a1_template_checklist;  -- a1.template.checklist
SELECT COUNT(*) FROM a1_tasklist;  -- a1.tasklist
SELECT COUNT(*) FROM a1_check;  -- a1.check
SELECT COUNT(*) FROM a1_check_result;  -- a1.check.result
SELECT COUNT(*) FROM a1_role;  -- a1.role
```

### Menu Verification

```sql
-- Verify menus created
SELECT id, name FROM ir_ui_menu
WHERE id IN (
  (SELECT id FROM ir_model_data WHERE module='ipai_ppm_a1' AND name='a1_menu_root'),
  (SELECT id FROM ir_model_data WHERE module='ipai_ppm_a1' AND name='a1_menu_operations'),
  (SELECT id FROM ir_model_data WHERE module='ipai_ppm_a1' AND name='a1_menu_tasklists'),
  (SELECT id FROM ir_model_data WHERE module='ipai_ppm_a1' AND name='a1_menu_tasks'),
  (SELECT id FROM ir_model_data WHERE module='ipai_ppm_a1' AND name='a1_menu_config'),
  (SELECT id FROM ir_model_data WHERE module='ipai_ppm_a1' AND name='a1_menu_workstreams'),
  (SELECT id FROM ir_model_data WHERE module='ipai_ppm_a1' AND name='a1_menu_templates'),
  (SELECT id FROM ir_model_data WHERE module='ipai_ppm_a1' AND name='a1_menu_checks'),
  (SELECT id FROM ir_model_data WHERE module='ipai_ppm_a1' AND name='a1_menu_roles')
);
```

---

**Documentation Generated**: 2025-12-26 02:06:55  
**Source**: Extracted from `addons/ipai/ipai_ppm_a1` via automated analysis  
**Note**: This documentation is generated from source code analysis. Manual verification recommended.
