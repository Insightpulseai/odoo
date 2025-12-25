# ipai_close_orchestration

**Module**: `ipai_close_orchestration`
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

**Total Models**: 9

### Model: `close.task.template`

**Description**: Close Task Template

**Python Class**: `CloseTaskTemplate`  
**File**: `addons/ipai/ipai_close_orchestration/models/close_template.py`

**Fields**:

| Field Name | Type | File |
|------------|------|------|
| `code` | Char | close_template.py |
| `name` | Char | close_template.py |
| `sequence` | Integer | close_template.py |
| `active` | Boolean | close_template.py |
| `category_id` | Many2one | close_template.py |
| `preparer_role` | Selection | close_template.py |
| `reviewer_role` | Selection | close_template.py |
| `approver_role` | Selection | close_template.py |
| `preparer_id` | Many2one | close_template.py |
| `reviewer_id` | Many2one | close_template.py |
| `approver_id` | Many2one | close_template.py |
| `prep_days` | Float | close_template.py |
| `review_days` | Float | close_template.py |
| `approval_days` | Float | close_template.py |
| `prep_offset` | Integer | close_template.py |
| `review_offset` | Integer | close_template.py |
| `approval_offset` | Integer | close_template.py |
| `checklist_ids` | One2many | close_template.py |
| `company_id` | Many2one | close_template.py |
| `a1_template_id` | Many2one | close_template.py |

### Model: `close.task.template.checklist`

**Description**: Close Task Template Checklist

**Python Class**: `CloseTaskTemplateChecklist`  
**File**: `addons/ipai/ipai_close_orchestration/models/close_template.py`

**Fields**:

| Field Name | Type | File |
|------------|------|------|
| `template_id` | Many2one | close_template.py |
| `code` | Char | close_template.py |
| `name` | Char | close_template.py |
| `sequence` | Integer | close_template.py |
| `is_required` | Boolean | close_template.py |
| `instructions` | Text | close_template.py |

### Model: `close.task.category`

**Description**: Close Task Category

**Python Class**: `CloseTaskCategory`  
**File**: `addons/ipai/ipai_close_orchestration/models/close_category.py`

**Fields**:

| Field Name | Type | File |
|------------|------|------|
| `code` | Char | close_category.py |
| `name` | Char | close_category.py |
| `sequence` | Integer | close_category.py |
| `active` | Boolean | close_category.py |
| `color` | Integer | close_category.py |
| `company_id` | Many2one | close_category.py |
| `a1_workstream_id` | Many2one | close_category.py |
| `template_ids` | One2many | close_category.py |
| `description` | Text | close_category.py |

### Model: `close.approval.gate.template`

**Description**: Close Approval Gate Template

**Python Class**: `CloseApprovalGateTemplate`  
**File**: `addons/ipai/ipai_close_orchestration/models/close_gate.py`

**Fields**:

| Field Name | Type | File |
|------------|------|------|
| `code` | Char | close_gate.py |
| `name` | Char | close_gate.py |
| `sequence` | Integer | close_gate.py |
| `active` | Boolean | close_gate.py |
| `gate_type` | Selection | close_gate.py |
| `pass_criteria` | Text | close_gate.py |
| `company_id` | Many2one | close_gate.py |
| `a1_check_id` | Many2one | close_gate.py |

### Model: `close.approval.gate`

**Description**: Close Approval Gate

**Python Class**: `CloseApprovalGate`  
**File**: `addons/ipai/ipai_close_orchestration/models/close_gate.py`

**Fields**:

| Field Name | Type | File |
|------------|------|------|
| `name` | Char | close_gate.py |
| `sequence` | Integer | close_gate.py |
| `cycle_id` | Many2one | close_gate.py |
| `template_id` | Many2one | close_gate.py |
| `gate_type` | Selection | close_gate.py |
| `state` | Selection | close_gate.py |
| `approver_id` | Many2one | close_gate.py |
| `approved_date` | Datetime | close_gate.py |
| `approved_by` | Many2one | close_gate.py |
| `threshold_value` | Float | close_gate.py |
| `actual_value` | Float | close_gate.py |
| `block_reason` | Text | close_gate.py |
| `company_id` | Many2one | close_gate.py |

### Model: `close.exception`

**Description**: Close Exception

**Python Class**: `CloseException`  
**File**: `addons/ipai/ipai_close_orchestration/models/close_exception.py`

**Fields**:

| Field Name | Type | File |
|------------|------|------|
| `name` | Char | close_exception.py |
| `exception_type` | Selection | close_exception.py |
| `severity` | Selection | close_exception.py |
| `state` | Selection | close_exception.py |
| `cycle_id` | Many2one | close_exception.py |
| `task_id` | Many2one | close_exception.py |
| `reported_by` | Many2one | close_exception.py |
| `assigned_to` | Many2one | close_exception.py |
| `escalated_to` | Many2one | close_exception.py |
| `escalation_count` | Integer | close_exception.py |
| `last_escalated` | Datetime | close_exception.py |
| `escalation_deadline` | Datetime | close_exception.py |
| `resolved_date` | Datetime | close_exception.py |
| `resolved_by` | Many2one | close_exception.py |
| `company_id` | Many2one | close_exception.py |

### Model: `close.task`

**Description**: Close Task

**Python Class**: `CloseTask`  
**File**: `addons/ipai/ipai_close_orchestration/models/close_task.py`

**Fields**:

| Field Name | Type | File |
|------------|------|------|
| `name` | Char | close_task.py |
| `sequence` | Integer | close_task.py |
| `cycle_id` | Many2one | close_task.py |
| `template_id` | Many2one | close_task.py |
| `category_id` | Many2one | close_task.py |
| `external_key` | Char | close_task.py |
| `preparer_id` | Many2one | close_task.py |
| `reviewer_id` | Many2one | close_task.py |
| `approver_id` | Many2one | close_task.py |
| `prep_deadline` | Date | close_task.py |
| `review_deadline` | Date | close_task.py |
| `approval_deadline` | Date | close_task.py |
| `state` | Selection | close_task.py |
| `prep_done_date` | Datetime | close_task.py |
| `prep_done_by` | Many2one | close_task.py |
| `review_done_date` | Datetime | close_task.py |
| `review_done_by` | Many2one | close_task.py |
| `approval_done_date` | Datetime | close_task.py |
| `approval_done_by` | Many2one | close_task.py |
| `checklist_ids` | One2many | close_task.py |
| `checklist_progress` | Float | close_task.py |
| `exception_ids` | One2many | close_task.py |
| `has_open_exceptions` | Boolean | close_task.py |
| `company_id` | Many2one | close_task.py |
| `a1_task_id` | Many2one | close_task.py |

### Model: `close.task.checklist`

**Description**: Close Task Checklist

**Python Class**: `CloseTaskChecklist`  
**File**: `addons/ipai/ipai_close_orchestration/models/close_task.py`

**Fields**:

| Field Name | Type | File |
|------------|------|------|
| `task_id` | Many2one | close_task.py |
| `code` | Char | close_task.py |
| `name` | Char | close_task.py |
| `sequence` | Integer | close_task.py |
| `is_required` | Boolean | close_task.py |
| `is_done` | Boolean | close_task.py |
| `instructions` | Text | close_task.py |
| `done_date` | Datetime | close_task.py |
| `done_by` | Many2one | close_task.py |

### Model: `close.cycle`

**Description**: Close Cycle

**Python Class**: `CloseCycle`  
**File**: `addons/ipai/ipai_close_orchestration/models/close_cycle.py`

**Fields**:

| Field Name | Type | File |
|------------|------|------|
| `name` | Char | close_cycle.py |
| `period_start` | Date | close_cycle.py |
| `period_end` | Date | close_cycle.py |
| `period_label` | Char | close_cycle.py |
| `state` | Selection | close_cycle.py |
| `task_ids` | One2many | close_cycle.py |
| `task_count` | Integer | close_cycle.py |
| `task_done_count` | Integer | close_cycle.py |
| `progress` | Float | close_cycle.py |
| `exception_ids` | One2many | close_cycle.py |
| `exception_count` | Integer | close_cycle.py |
| `open_exception_count` | Integer | close_cycle.py |
| `gate_ids` | One2many | close_cycle.py |
| `gates_ready` | Boolean | close_cycle.py |
| `company_id` | Many2one | close_cycle.py |
| `a1_tasklist_id` | Many2one | close_cycle.py |
| `webhook_url` | Char | close_cycle.py |

---

## Security

**Security Groups**: 3

### Group: `group_close_user`

**Name**: User  
**Category**: `module_category_close`  
**File**: `addons/ipai/ipai_close_orchestration/security/close_security.xml`

### Group: `group_close_manager`

**Name**: Manager  
**Category**: `module_category_close`  
**File**: `addons/ipai/ipai_close_orchestration/security/close_security.xml`

### Group: `group_close_admin`

**Name**: Administrator  
**Category**: `module_category_close`  
**File**: `addons/ipai/ipai_close_orchestration/security/close_security.xml`

**Access Rules (ir.model.access.csv)**: 27

| Access ID | Model | Group | Read | Write | Create | Delete |
|-----------|-------|-------|------|-------|--------|--------|
| `access_close_category_user` | `model_close_task_category` | `group_close_user` | ✅ | ❌ | ❌ | ❌ |
| `access_close_category_manager` | `model_close_task_category` | `group_close_manager` | ✅ | ✅ | ✅ | ❌ |
| `access_close_category_admin` | `model_close_task_category` | `group_close_admin` | ✅ | ✅ | ✅ | ✅ |
| `access_close_template_user` | `model_close_task_template` | `group_close_user` | ✅ | ❌ | ❌ | ❌ |
| `access_close_template_manager` | `model_close_task_template` | `group_close_manager` | ✅ | ✅ | ✅ | ❌ |
| `access_close_template_admin` | `model_close_task_template` | `group_close_admin` | ✅ | ✅ | ✅ | ✅ |
| `access_close_template_checklist_user` | `model_close_task_template_checklist` | `group_close_user` | ✅ | ❌ | ❌ | ❌ |
| `access_close_template_checklist_manager` | `model_close_task_template_checklist` | `group_close_manager` | ✅ | ✅ | ✅ | ❌ |
| `access_close_template_checklist_admin` | `model_close_task_template_checklist` | `group_close_admin` | ✅ | ✅ | ✅ | ✅ |
| `access_close_cycle_user` | `model_close_cycle` | `group_close_user` | ✅ | ❌ | ❌ | ❌ |
| `access_close_cycle_manager` | `model_close_cycle` | `group_close_manager` | ✅ | ✅ | ✅ | ❌ |
| `access_close_cycle_admin` | `model_close_cycle` | `group_close_admin` | ✅ | ✅ | ✅ | ✅ |
| `access_close_task_user` | `model_close_task` | `group_close_user` | ✅ | ✅ | ❌ | ❌ |
| `access_close_task_manager` | `model_close_task` | `group_close_manager` | ✅ | ✅ | ✅ | ❌ |
| `access_close_task_admin` | `model_close_task` | `group_close_admin` | ✅ | ✅ | ✅ | ✅ |
| `access_close_task_checklist_user` | `model_close_task_checklist` | `group_close_user` | ✅ | ✅ | ❌ | ❌ |
| `access_close_task_checklist_manager` | `model_close_task_checklist` | `group_close_manager` | ✅ | ✅ | ✅ | ❌ |
| `access_close_task_checklist_admin` | `model_close_task_checklist` | `group_close_admin` | ✅ | ✅ | ✅ | ✅ |
| `access_close_exception_user` | `model_close_exception` | `group_close_user` | ✅ | ✅ | ✅ | ❌ |
| `access_close_exception_manager` | `model_close_exception` | `group_close_manager` | ✅ | ✅ | ✅ | ❌ |
| `access_close_exception_admin` | `model_close_exception` | `group_close_admin` | ✅ | ✅ | ✅ | ✅ |
| `access_close_gate_template_user` | `model_close_approval_gate_template` | `group_close_user` | ✅ | ❌ | ❌ | ❌ |
| `access_close_gate_template_manager` | `model_close_approval_gate_template` | `group_close_manager` | ✅ | ✅ | ✅ | ❌ |
| `access_close_gate_template_admin` | `model_close_approval_gate_template` | `group_close_admin` | ✅ | ✅ | ✅ | ✅ |
| `access_close_gate_user` | `model_close_approval_gate` | `group_close_user` | ✅ | ✅ | ❌ | ❌ |
| `access_close_gate_manager` | `model_close_approval_gate` | `group_close_manager` | ✅ | ✅ | ✅ | ❌ |
| `access_close_gate_admin` | `model_close_approval_gate` | `group_close_admin` | ✅ | ✅ | ✅ | ✅ |

**Record Rules (ir.rule)**: 6

### Rule: `close_cycle_company_rule`

**Name**: Close Cycle: Company  
**Model**: `model_close_cycle`  
**Domain**: `[('company_id', 'in', company_ids)]`  
**Groups**: `[(4, ref('group_close_user'))]`  
**File**: `addons/ipai/ipai_close_orchestration/security/close_security.xml`

### Rule: `close_task_company_rule`

**Name**: Close Task: Company  
**Model**: `model_close_task`  
**Domain**: `[('company_id', 'in', company_ids)]`  
**Groups**: `[(4, ref('group_close_user'))]`  
**File**: `addons/ipai/ipai_close_orchestration/security/close_security.xml`

### Rule: `close_template_company_rule`

**Name**: Close Template: Company  
**Model**: `model_close_task_template`  
**Domain**: `[('company_id', 'in', company_ids)]`  
**Groups**: `[(4, ref('group_close_user'))]`  
**File**: `addons/ipai/ipai_close_orchestration/security/close_security.xml`

### Rule: `close_category_company_rule`

**Name**: Close Category: Company  
**Model**: `model_close_task_category`  
**Domain**: `[('company_id', 'in', company_ids)]`  
**Groups**: `[(4, ref('group_close_user'))]`  
**File**: `addons/ipai/ipai_close_orchestration/security/close_security.xml`

### Rule: `close_exception_company_rule`

**Name**: Close Exception: Company  
**Model**: `model_close_exception`  
**Domain**: `[('company_id', 'in', company_ids)]`  
**Groups**: `[(4, ref('group_close_user'))]`  
**File**: `addons/ipai/ipai_close_orchestration/security/close_security.xml`

### Rule: `close_gate_company_rule`

**Name**: Close Gate: Company  
**Model**: `model_close_approval_gate`  
**Domain**: `[('company_id', 'in', company_ids)]`  
**Groups**: `[(4, ref('group_close_user'))]`  
**File**: `addons/ipai/ipai_close_orchestration/security/close_security.xml`

---

## UI (Menus, Actions, Views)

**Menus**: 10

| Menu ID | Name | Parent | Action | Sequence | File |
|---------|------|--------|--------|----------|------|
| `close_menu_root` | Close Orchestration | `` | `` | 41 | close_menu.xml |
| `close_menu_operations` | Operations | `close_menu_root` | `` | 10 | close_menu.xml |
| `close_menu_cycles` | Close Cycles | `close_menu_operations` | `close_cycle_action` | 10 | close_menu.xml |
| `close_menu_tasks` | Tasks | `close_menu_operations` | `close_task_action` | 20 | close_menu.xml |
| `close_menu_exceptions` | Exceptions | `close_menu_operations` | `close_exception_action` | 30 | close_menu.xml |
| `close_menu_gates` | Approval Gates | `close_menu_operations` | `close_gate_action` | 40 | close_menu.xml |
| `close_menu_config` | Configuration | `close_menu_root` | `` | 20 | close_menu.xml |
| `close_menu_categories` | Categories | `close_menu_config` | `close_category_action` | 10 | close_menu.xml |
| `close_menu_templates` | Task Templates | `close_menu_config` | `close_template_action` | 20 | close_menu.xml |
| `close_menu_gate_templates` | Gate Templates | `close_menu_config` | `close_gate_template_action` | 30 | close_menu.xml |

**Actions**: 7

| Action ID | Name | Model | View Mode | File |
|-----------|------|-------|-----------|------|
| `close_category_action` | Categories | `close.task.category` | list,form | close_template_views.xml |
| `close_template_action` | Task Templates | `close.task.template` | list,form | close_template_views.xml |
| `close_task_action` | Close Tasks | `close.task` | list,kanban,form | close_task_views.xml |
| `close_gate_template_action` | Gate Templates | `close.approval.gate.template` | list,form | close_gate_views.xml |
| `close_gate_action` | Approval Gates | `close.approval.gate` | list,form | close_gate_views.xml |
| `close_cycle_action` | Close Cycles | `close.cycle` | list,form | close_cycle_views.xml |
| `close_exception_action` | Exceptions | `close.exception` | list,form | close_exception_views.xml |

**Views**: 20

| View ID | Name | Model | Type | File |
|---------|------|-------|------|------|
| `close_category_view_tree` | close.task.category.tree | `close.task.category` |  ⚠️ (deprecated type='xml') | close_template_views.xml |
| `close_category_view_form` | close.task.category.form | `close.task.category` | form ⚠️ (deprecated type='xml') | close_template_views.xml |
| `close_template_view_tree` | close.task.template.tree | `close.task.template` |  ⚠️ (deprecated type='xml') | close_template_views.xml |
| `close_template_view_form` | close.task.template.form | `close.task.template` | form ⚠️ (deprecated type='xml') | close_template_views.xml |
| `close_template_view_search` | close.task.template.search | `close.task.template` | search ⚠️ (deprecated type='xml') | close_template_views.xml |
| `close_task_view_tree` | close.task.tree | `close.task` |  ⚠️ (deprecated type='xml') | close_task_views.xml |
| `close_task_view_form` | close.task.form | `close.task` | form ⚠️ (deprecated type='xml') | close_task_views.xml |
| `close_task_view_kanban` | close.task.kanban | `close.task` | kanban ⚠️ (deprecated type='xml') | close_task_views.xml |
| `close_task_view_search` | close.task.search | `close.task` | search ⚠️ (deprecated type='xml') | close_task_views.xml |
| `close_gate_template_view_tree` | close.approval.gate.template.tree | `close.approval.gate.template` |  ⚠️ (deprecated type='xml') | close_gate_views.xml |
| `close_gate_template_view_form` | close.approval.gate.template.form | `close.approval.gate.template` | form ⚠️ (deprecated type='xml') | close_gate_views.xml |
| `close_gate_view_tree` | close.approval.gate.tree | `close.approval.gate` |  ⚠️ (deprecated type='xml') | close_gate_views.xml |
| `close_gate_view_form` | close.approval.gate.form | `close.approval.gate` | form ⚠️ (deprecated type='xml') | close_gate_views.xml |
| `close_gate_view_search` | close.approval.gate.search | `close.approval.gate` | search ⚠️ (deprecated type='xml') | close_gate_views.xml |
| `close_cycle_view_tree` | close.cycle.tree | `close.cycle` |  ⚠️ (deprecated type='xml') | close_cycle_views.xml |
| `close_cycle_view_form` | close.cycle.form | `close.cycle` | form ⚠️ (deprecated type='xml') | close_cycle_views.xml |
| `close_cycle_view_search` | close.cycle.search | `close.cycle` | search ⚠️ (deprecated type='xml') | close_cycle_views.xml |
| `close_exception_view_tree` | close.exception.tree | `close.exception` |  ⚠️ (deprecated type='xml') | close_exception_views.xml |
| `close_exception_view_form` | close.exception.form | `close.exception` | form ⚠️ (deprecated type='xml') | close_exception_views.xml |
| `close_exception_view_search` | close.exception.search | `close.exception` | search ⚠️ (deprecated type='xml') | close_exception_views.xml |

---

## Automation

**Scheduled Actions (ir.cron)**: 3

### Cron: `ir_cron_close_due_reminders`

**Name**: Close: Send Due Reminders  
**Model**: `model_close_task`  
**Function**: `model._cron_send_due_reminders()`  
**Interval**: 1 days  
**File**: `addons/ipai/ipai_close_orchestration/data/close_cron.xml`

⚠️ **Odoo 18 Issue**: This cron job uses deprecated `numbercall` field. Remove before installation.

### Cron: `ir_cron_close_auto_escalate`

**Name**: Close: Auto-Escalate Exceptions  
**Model**: `model_close_exception`  
**Function**: `model._cron_auto_escalate()`  
**Interval**: 4 hours  
**File**: `addons/ipai/ipai_close_orchestration/data/close_cron.xml`

⚠️ **Odoo 18 Issue**: This cron job uses deprecated `numbercall` field. Remove before installation.

### Cron: `ir_cron_close_check_gates`

**Name**: Close: Check Approval Gates  
**Model**: `model_close_approval_gate`  
**Function**: `model._cron_check_gates()`  
**Interval**: 1 hours  
**File**: `addons/ipai/ipai_close_orchestration/data/close_cron.xml`

⚠️ **Odoo 18 Issue**: This cron job uses deprecated `numbercall` field. Remove before installation.

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
odoo -d <database> -i ipai_close_orchestration --stop-after-init
```

### Upgrade

```bash
# Upgrade module
odoo -d <database> -u ipai_close_orchestration --stop-after-init
```

### ⚠️ Odoo 18 Compatibility Issues

**CRITICAL**: The following issues must be fixed before installation on Odoo 18:

⚠️ Deprecated `numbercall` field in cron job: `ir_cron_close_due_reminders` (addons/ipai/ipai_close_orchestration/data/close_cron.xml)

⚠️ Deprecated `numbercall` field in cron job: `ir_cron_close_auto_escalate` (addons/ipai/ipai_close_orchestration/data/close_cron.xml)

⚠️ Deprecated `numbercall` field in cron job: `ir_cron_close_check_gates` (addons/ipai/ipai_close_orchestration/data/close_cron.xml)

⚠️ Deprecated `type="xml"` attribute in view: `close_category_view_tree` (addons/ipai/ipai_close_orchestration/views/close_template_views.xml)

⚠️ Deprecated `type="xml"` attribute in view: `close_category_view_form` (addons/ipai/ipai_close_orchestration/views/close_template_views.xml)

⚠️ Deprecated `type="xml"` attribute in view: `close_template_view_tree` (addons/ipai/ipai_close_orchestration/views/close_template_views.xml)

⚠️ Deprecated `type="xml"` attribute in view: `close_template_view_form` (addons/ipai/ipai_close_orchestration/views/close_template_views.xml)

⚠️ Deprecated `type="xml"` attribute in view: `close_template_view_search` (addons/ipai/ipai_close_orchestration/views/close_template_views.xml)

⚠️ Deprecated `type="xml"` attribute in view: `close_task_view_tree` (addons/ipai/ipai_close_orchestration/views/close_task_views.xml)

⚠️ Deprecated `type="xml"` attribute in view: `close_task_view_form` (addons/ipai/ipai_close_orchestration/views/close_task_views.xml)

⚠️ Deprecated `type="xml"` attribute in view: `close_task_view_kanban` (addons/ipai/ipai_close_orchestration/views/close_task_views.xml)

⚠️ Deprecated `type="xml"` attribute in view: `close_task_view_search` (addons/ipai/ipai_close_orchestration/views/close_task_views.xml)

⚠️ Deprecated `type="xml"` attribute in view: `close_gate_template_view_tree` (addons/ipai/ipai_close_orchestration/views/close_gate_views.xml)

⚠️ Deprecated `type="xml"` attribute in view: `close_gate_template_view_form` (addons/ipai/ipai_close_orchestration/views/close_gate_views.xml)

⚠️ Deprecated `type="xml"` attribute in view: `close_gate_view_tree` (addons/ipai/ipai_close_orchestration/views/close_gate_views.xml)

⚠️ Deprecated `type="xml"` attribute in view: `close_gate_view_form` (addons/ipai/ipai_close_orchestration/views/close_gate_views.xml)

⚠️ Deprecated `type="xml"` attribute in view: `close_gate_view_search` (addons/ipai/ipai_close_orchestration/views/close_gate_views.xml)

⚠️ Deprecated `type="xml"` attribute in view: `close_cycle_view_tree` (addons/ipai/ipai_close_orchestration/views/close_cycle_views.xml)

⚠️ Deprecated `type="xml"` attribute in view: `close_cycle_view_form` (addons/ipai/ipai_close_orchestration/views/close_cycle_views.xml)

⚠️ Deprecated `type="xml"` attribute in view: `close_cycle_view_search` (addons/ipai/ipai_close_orchestration/views/close_cycle_views.xml)

⚠️ Deprecated `type="xml"` attribute in view: `close_exception_view_tree` (addons/ipai/ipai_close_orchestration/views/close_exception_views.xml)

⚠️ Deprecated `type="xml"` attribute in view: `close_exception_view_form` (addons/ipai/ipai_close_orchestration/views/close_exception_views.xml)

⚠️ Deprecated `type="xml"` attribute in view: `close_exception_view_search` (addons/ipai/ipai_close_orchestration/views/close_exception_views.xml)

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
WHERE name = 'ipai_close_orchestration';
-- Expected: state='installed', latest_version='unknown'
```

### Data Model Verification

```sql
-- Verify tables created
SELECT COUNT(*) FROM close_task_template;  -- close.task.template
SELECT COUNT(*) FROM close_task_template_checklist;  -- close.task.template.checklist
SELECT COUNT(*) FROM close_task_category;  -- close.task.category
SELECT COUNT(*) FROM close_approval_gate_template;  -- close.approval.gate.template
SELECT COUNT(*) FROM close_approval_gate;  -- close.approval.gate
SELECT COUNT(*) FROM close_exception;  -- close.exception
SELECT COUNT(*) FROM close_task;  -- close.task
SELECT COUNT(*) FROM close_task_checklist;  -- close.task.checklist
SELECT COUNT(*) FROM close_cycle;  -- close.cycle
```

### Menu Verification

```sql
-- Verify menus created
SELECT id, name FROM ir_ui_menu
WHERE id IN (
  (SELECT id FROM ir_model_data WHERE module='ipai_close_orchestration' AND name='close_menu_root'),
  (SELECT id FROM ir_model_data WHERE module='ipai_close_orchestration' AND name='close_menu_operations'),
  (SELECT id FROM ir_model_data WHERE module='ipai_close_orchestration' AND name='close_menu_cycles'),
  (SELECT id FROM ir_model_data WHERE module='ipai_close_orchestration' AND name='close_menu_tasks'),
  (SELECT id FROM ir_model_data WHERE module='ipai_close_orchestration' AND name='close_menu_exceptions'),
  (SELECT id FROM ir_model_data WHERE module='ipai_close_orchestration' AND name='close_menu_gates'),
  (SELECT id FROM ir_model_data WHERE module='ipai_close_orchestration' AND name='close_menu_config'),
  (SELECT id FROM ir_model_data WHERE module='ipai_close_orchestration' AND name='close_menu_categories'),
  (SELECT id FROM ir_model_data WHERE module='ipai_close_orchestration' AND name='close_menu_templates'),
  (SELECT id FROM ir_model_data WHERE module='ipai_close_orchestration' AND name='close_menu_gate_templates')
);
```

### Scheduled Actions Verification

```sql
-- Verify cron jobs active
SELECT id, name, active, nextcall
FROM ir_cron
WHERE id IN (
  (SELECT id FROM ir_model_data WHERE module='ipai_close_orchestration' AND name='ir_cron_close_due_reminders'),
  (SELECT id FROM ir_model_data WHERE module='ipai_close_orchestration' AND name='ir_cron_close_auto_escalate'),
  (SELECT id FROM ir_model_data WHERE module='ipai_close_orchestration' AND name='ir_cron_close_check_gates')
);
-- Expected: active=true for all jobs
```

---

**Documentation Generated**: 2025-12-26 02:06:55  
**Source**: Extracted from `addons/ipai/ipai_close_orchestration` via automated analysis  
**Note**: This documentation is generated from source code analysis. Manual verification recommended.
