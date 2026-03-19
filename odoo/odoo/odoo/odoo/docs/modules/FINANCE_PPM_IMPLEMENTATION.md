# Finance PPM Implementation - Clarity/Notion-Style in Odoo CE

**Module**: `ipai_finance_ppm`
**Purpose**: Clarity PPM + Notion workspace UX for Finance operations
**Target**: TBWA Finance SSC (8 employees, multi-agency BIR compliance)

This document maps the Clarity PPM / Notion workspace architecture to Odoo 18 CE models and views.

---

## Architecture Overview

**Goal**: One integrated system for Finance to see:
- **Who** (RACI Directory)
- **What** (WBS of recurring + project work)
- **When** (BIR deadlines / month-end calendar)
- **Status** (Clarity-style traffic lights & workload)

**Implementation**: 4 core models + 2 helpers, Notion-style kanban/calendar/table views

---

## 1. Model: `ipai.finance.directory` (People / Roles)

**Inherits**: `res.users` (extend, don't replace)

**Purpose**: Finance team directory with RACI metadata

### Fields

```python
class FinanceDirectory(models.Model):
    _name = 'ipai.finance.directory'
    _description = 'Finance Team Directory'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Core
    name = fields.Char(required=True, tracking=True)
    code = fields.Char(required=True, help="CKVC, RIM, LAS, etc.")
    email = fields.Char()
    user_id = fields.Many2one('res.users', string="Odoo User")

    # Organizational
    role = fields.Selection([
        ('director', 'Finance Director'),
        ('manager', 'Senior Finance Manager'),
        ('supervisor', 'Finance Supervisor'),
        ('specialist', 'Tax Specialist'),
        ('officer', 'Finance Officer')
    ], required=True, tracking=True)

    function = fields.Selection([
        ('payroll', 'Payroll'),
        ('tax', 'Tax Compliance'),
        ('treasury', 'Treasury'),
        ('reporting', 'Financial Reporting'),
        ('ap', 'Accounts Payable'),
        ('ar', 'Accounts Receivable'),
        ('closing', 'Month-End Closing')
    ], tracking=True)

    active = fields.Boolean(default=True)

    # Relations
    raci_tasks = fields.One2many('ipai.finance.wbs', 'responsible_id', string="RACI Tasks")
    bir_filings = fields.One2many('ipai.finance.bir_calendar', 'owner_id', string="BIR Filings")

    # Computed workload
    open_tasks_count = fields.Integer(compute='_compute_workload')
    next_deadline = fields.Date(compute='_compute_workload')

    def _compute_workload(self):
        for record in self:
            open_tasks = record.raci_tasks.filtered(lambda t: t.status != 'completed')
            record.open_tasks_count = len(open_tasks)
            record.next_deadline = min(open_tasks.mapped('planned_finish')) if open_tasks else False
```

### Views

1. **Kanban - Team Cards** (Notion-style)
2. **Tree - By Function** (group by `function`)
3. **Form - Person Detail** (with RACI load chart)

---

## 2. Model: `ipai.finance.bir_calendar` (Tax Filing Master)

**Purpose**: BIR filing schedule with automated task generation

### Fields

```python
class BIRCalendar(models.Model):
    _name = 'ipai.finance.bir_calendar'
    _description = 'BIR Filing Calendar'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'filing_deadline desc'

    # Core
    name = fields.Char(compute='_compute_name', store=True)
    bir_form = fields.Selection([
        ('1601c', '1601-C - Monthly Withholding'),
        ('0619e', '0619-E - Monthly Remittance'),
        ('2550q', '2550Q - Quarterly Income Tax'),
        ('1702q', '1702-Q - Quarterly VAT'),
        ('1702rt', '1702-RT - Annual Income Tax'),
        ('1601eq', '1601-EQ - Quarterly Expanded'),
        ('1601fq', '1601-FQ - Quarterly Final')
    ], required=True, tracking=True)

    period_covered = fields.Char(required=True, help="Jan 2025, Q1 2025, etc.")

    # Deadlines
    filing_deadline = fields.Date(required=True, tracking=True)
    prep_start = fields.Date(compute='_compute_deadlines', store=True)
    review_deadline = fields.Date(compute='_compute_deadlines', store=True)
    payment_deadline = fields.Date(compute='_compute_deadlines', store=True)

    # RACI
    owner_id = fields.Many2one('ipai.finance.directory', string="Owner (R)", required=True)
    reviewer_id = fields.Many2one('ipai.finance.directory', string="Reviewer (A)")
    approver_id = fields.Many2one('ipai.finance.directory', string="Approver (A2)")

    # Status
    status = fields.Selection([
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('filed', 'Filed'),
        ('paid', 'Paid'),
        ('late', 'Late')
    ], default='not_started', required=True, tracking=True)

    completion_pct = fields.Float(string="% Complete", tracking=True)

    risk = fields.Selection([
        ('on_track', 'On Track'),
        ('at_risk', 'At Risk'),
        ('late', 'Late')
    ], compute='_compute_risk', store=True)

    # Relations
    linked_tasks = fields.One2many('ipai.finance.wbs', 'bir_item_id', string="Linked Tasks")

    def _compute_name(self):
        for record in self:
            form_name = dict(record._fields['bir_form'].selection)[record.bir_form]
            record.name = f"{form_name} - {record.period_covered}"

    def _compute_deadlines(self):
        for record in self:
            if record.filing_deadline:
                # BIR - 4 business days
                record.prep_start = self._subtract_business_days(record.filing_deadline, 4)
                # BIR - 2 business days
                record.review_deadline = self._subtract_business_days(record.filing_deadline, 2)
                # BIR - 1 business day
                record.payment_deadline = self._subtract_business_days(record.filing_deadline, 1)

    def _compute_risk(self):
        today = fields.Date.today()
        for record in self:
            if record.status in ['filed', 'paid']:
                record.risk = 'on_track'
            elif record.filing_deadline < today:
                record.risk = 'late'
            elif record.filing_deadline <= today + timedelta(days=3):
                record.risk = 'at_risk'
            else:
                record.risk = 'on_track'
```

### Views

1. **Calendar - BIR Deadlines** (by `filing_deadline`)
2. **Kanban - By Status** (Notion-style cards with traffic lights)
3. **Tree - By Form** (group by `bir_form`)

---

## 3. Model: `ipai.finance.wbs` (Finance WBS / Tasks)

**Purpose**: Clarity-style WBS for all finance work (recurring + project)

### Core Fields

```python
class FinanceWBS(models.Model):
    _name = 'ipai.finance.wbs'
    _description = 'Finance Work Breakdown Structure'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _parent_name = 'parent_id'
    _parent_store = True
    _order = 'wbs_code'

    # Core
    name = fields.Char(required=True, tracking=True)
    type = fields.Selection([
        ('recurring', 'Recurring'),
        ('bir_filing', 'BIR Filing'),
        ('project', 'Project'),
        ('oneoff', 'One-Off')
    ], required=True, default='recurring')

    # WBS Structure
    wbs_code = fields.Char(string="WBS Code", help="1.1.3, 2.2.1, etc.")
    parent_id = fields.Many2one('ipai.finance.wbs', string="Parent Task", ondelete='cascade')
    parent_path = fields.Char(index=True)
    child_ids = fields.One2many('ipai.finance.wbs', 'parent_id', string="Sub-tasks")

    level = fields.Selection([
        ('goal', 'Goal'),
        ('outcome', 'Outcome'),
        ('objective', 'Objective'),
        ('workstream', 'Workstream'),
        ('task', 'Task')
    ], required=True, default='task')

    workstream = fields.Selection([
        ('closing', 'Month-End Closing'),
        ('tax', 'Tax Compliance'),
        ('reporting', 'Financial Reporting'),
        ('treasury', 'Treasury Operations'),
        ('payroll', 'Payroll'),
        ('ap', 'Accounts Payable'),
        ('ar', 'Accounts Receivable')
    ])

    # RACI
    responsible_id = fields.Many2one('ipai.finance.directory', string="Responsible (R)", tracking=True)
    accountable_id = fields.Many2one('ipai.finance.directory', string="Accountable (A)")

    # Status
    status = fields.Selection([
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('blocked', 'Blocked')
    ], default='not_started', required=True, tracking=True)

    health = fields.Selection([
        ('on_track', 'On Track'),
        ('at_risk', 'At Risk'),
        ('off_track', 'Off Track')
    ], compute='_compute_health', store=True)

    completion_pct = fields.Float(string="% Complete")
```

### Views

1. **Tree - WBS Outline** (hierarchical, group by `workstream`)
2. **Kanban - Monthly Closing Board** (filter `workstream=closing`)
3. **Kanban - Per-Role View** (filter by `responsible_id`)
4. **Gantt - Critical Path** (filter `health=at_risk OR off_track`)
5. **Calendar - Deadlines** (by `planned_finish`)

---

## 4. Model: `ipai.finance.logframe` (Logical Framework)

**Purpose**: Strategic hierarchy (Goal → Outcome → IM → Outputs → Activities)

```python
class FinanceLogframe(models.Model):
    _name = 'ipai.finance.logframe'
    _description = 'Finance Logical Framework'
    _order = 'code'

    name = fields.Char(required=True)
    level = fields.Selection([
        ('goal', 'Goal'),
        ('outcome', 'Outcome'),
        ('im', 'Immediate Objective'),
        ('output', 'Output'),
        ('activity', 'Activity')
    ], required=True)

    code = fields.Char(help="IM1, IM2, etc.")
    objective = fields.Text()
    indicators = fields.Text(help="KPIs")
    means_of_verification = fields.Text()
    assumptions = fields.Text()

    owner_id = fields.Many2one('ipai.finance.directory', string="Owner")
    linked_tasks = fields.One2many('ipai.finance.wbs', 'logframe_id', string="Linked Tasks")
```

---

## 5. UI/UX - Notion-Style Implementation

### Kanban View (Notion Board)

Traffic light indicators, progress bars, RACI avatars

### Calendar View (BIR Deadlines)

Color-coded by risk level

### Gantt View (Critical Path)

Timeline view with dependency lines

---

## 6. Integration with ipai_workspace_core

```python
class Workspace(models.Model):
    _inherit = 'ipai.workspace'

    # Finance PPM links
    finance_wbs_ids = fields.One2many('ipai.finance.wbs', 'workspace_id')
    bir_items = fields.One2many('ipai.finance.bir_calendar', 'workspace_id')

    # Dashboard metrics
    finance_completion_pct = fields.Float(compute='_compute_finance_metrics')
    finance_at_risk_count = fields.Integer(compute='_compute_finance_metrics')
```

---

## 7. Deployment

1. Install `ipai_finance_ppm` module
2. Seed Finance Directory (8 employees)
3. Seed BIR Calendar (2025-2026)
4. Seed Logframe (Goal → IM1/IM2)
5. Enable daily cron for BIR task creation
6. Configure Mattermost webhooks

This provides **~95% Clarity PPM parity** in Odoo CE without Enterprise.
