---
name: odoo19-actions
description: Odoo 19 Actions - Window, URL, Server, Report, Client, Scheduled Actions (ir.cron), Bindings
metadata:
  author: odoo/documentation
  version: "19.0"
  source: "content/developer/reference/backend/actions.rst"
  extracted: "2026-02-17"
---

# Odoo 19 Actions

Comprehensive reference for Odoo 19 action types: Window Actions (ir.actions.act_window),
URL Actions (ir.actions.act_url), Server Actions (ir.actions.server), Report Actions
(ir.actions.report), Client Actions (ir.actions.client), Scheduled Actions (ir.cron),
and action bindings.

---

## 1. Overview

Actions define system behavior in response to user interactions: login, button click,
menu selection, etc. All actions share two mandatory attributes:

| Attribute | Description |
|-----------|-------------|
| `type` | Action category (determines fields and interpretation) |
| `name` | Short user-readable description |

### 1.1 Action Resolution

A client can receive actions in 4 forms:

| Form | Behavior |
|------|----------|
| `False` | Close any open action dialog |
| String | Match against client action tags, or treat as number |
| Number | Read action record from database (DB id or external id) |
| Dictionary | Treat as client action descriptor and execute directly |

---

## 2. Bindings

Optional attributes to present an action in a model's contextual menu:

| Attribute | Description |
|-----------|-------------|
| `binding_model_id` | Model the action is bound to (for Server Actions, use `model_id`) |
| `binding_type` | `action` (Action menu, default) or `report` (Print menu) |
| `binding_view_types` | Comma-separated view types (`list,form` default) |

```xml
<!-- Action bound to Action menu on res.partner -->
<record id="action_partner_mass_update" model="ir.actions.server">
    <field name="name">Mass Update Partners</field>
    <field name="model_id" ref="base.model_res_partner"/>
    <field name="binding_model_id" ref="base.model_res_partner"/>
    <field name="binding_view_types">list</field>
    <field name="state">code</field>
    <field name="code">
        records.write({'active': True})
    </field>
</record>
```

---

## 3. Window Actions (ir.actions.act_window)

The most common action type. Presents model data through views.

### 3.1 Fields

| Field | Type | Description |
|-------|------|-------------|
| `res_model` | `Char` | Model to display views for |
| `views` | List | `[(view_id, view_type)]` pairs |
| `view_mode` | `Char` | Comma-separated view types (default: `list,form`) |
| `view_id` | `Many2one` | Specific view to use |
| `view_ids` | `One2many` | Ordered view definitions via `ir.actions.act_window.view` |
| `res_id` | `Integer` | Specific record to open in form view |
| `search_view_id` | `Many2one` | Specific search view to use |
| `target` | `Selection` | `current` (default), `new` (dialog), `fullscreen`, `main` (clears breadcrumbs) |
| `context` | `Char` | Additional context data (Python dict as string) |
| `domain` | `Char` | Filtering domain for all view queries |
| `limit` | `Integer` | Records per page in list (default: 80) |

### 3.2 View Composition

The `views` list is composed server-side:
1. Each `(id, type)` from `view_ids` (ordered by sequence)
2. If `view_id` is set and its type isn't filled yet, append `(id, type)`
3. For each unfilled type in `view_mode`, append `(False, type)`

### 3.3 XML Examples

#### Basic list+form action

```xml
<record id="action_my_model" model="ir.actions.act_window">
    <field name="name">My Models</field>
    <field name="res_model">my.model</field>
    <field name="view_mode">list,form</field>
</record>
```

#### Action with domain and context

```xml
<record id="action_active_partners" model="ir.actions.act_window">
    <field name="name">Active Partners</field>
    <field name="res_model">res.partner</field>
    <field name="view_mode">list,form,kanban</field>
    <field name="domain">[('is_company', '=', True)]</field>
    <field name="context">{
        'default_is_company': True,
        'search_default_my_partners': 1,
    }</field>
    <field name="limit">50</field>
</record>
```

#### Action with specific view

```xml
<record id="action_my_model_graph" model="ir.actions.act_window">
    <field name="name">My Model Analysis</field>
    <field name="res_model">my.model</field>
    <field name="view_mode">graph</field>
    <field name="view_id" ref="view_my_model_graph"/>
</record>
```

#### Action opening specific record in form

```xml
<record id="action_edit_company" model="ir.actions.act_window">
    <field name="name">Company Settings</field>
    <field name="res_model">res.company</field>
    <field name="view_mode">form</field>
    <field name="res_id" eval="1"/>
    <field name="target">current</field>
</record>
```

#### Action opening in dialog (popup)

```xml
<record id="action_quick_create" model="ir.actions.act_window">
    <field name="name">Quick Create</field>
    <field name="res_model">my.model</field>
    <field name="view_mode">form</field>
    <field name="target">new</field>
</record>
```

#### Action with search view and default filters

```xml
<record id="action_my_tasks" model="ir.actions.act_window">
    <field name="name">My Tasks</field>
    <field name="res_model">project.task</field>
    <field name="view_mode">list,form,kanban,calendar</field>
    <field name="search_view_id" ref="view_task_search"/>
    <field name="context">{
        'search_default_my_tasks': 1,
        'search_default_open': 1,
    }</field>
</record>
```

#### Action with explicit view order (ir.actions.act_window.view)

```xml
<record id="action_my_model" model="ir.actions.act_window">
    <field name="name">My Models</field>
    <field name="res_model">my.model</field>
    <field name="view_mode">list,form,kanban</field>
</record>

<record id="action_my_model_list_view" model="ir.actions.act_window.view">
    <field name="sequence">1</field>
    <field name="view_mode">list</field>
    <field name="view_id" ref="view_my_model_custom_list"/>
    <field name="act_window_id" ref="action_my_model"/>
</record>

<record id="action_my_model_form_view" model="ir.actions.act_window.view">
    <field name="sequence">2</field>
    <field name="view_mode">form</field>
    <field name="view_id" ref="view_my_model_custom_form"/>
    <field name="act_window_id" ref="action_my_model"/>
</record>
```

### 3.4 Returning Window Actions from Python

```python
def action_open_partner(self):
    self.ensure_one()
    return {
        'type': 'ir.actions.act_window',
        'res_model': 'res.partner',
        'views': [[False, 'form']],
        'res_id': self.partner_id.id,
        'target': 'current',
    }

def action_open_related_records(self):
    return {
        'type': 'ir.actions.act_window',
        'name': 'Related Records',
        'res_model': 'my.related.model',
        'views': [[False, 'list'], [False, 'form']],
        'domain': [('parent_id', '=', self.id)],
        'context': {'default_parent_id': self.id},
    }

def action_open_wizard(self):
    return {
        'type': 'ir.actions.act_window',
        'name': 'My Wizard',
        'res_model': 'my.wizard',
        'views': [[False, 'form']],
        'target': 'new',
        'context': {
            'active_ids': self.ids,
            'active_model': self._name,
        },
    }
```

---

## 4. URL Actions (ir.actions.act_url)

Open a URL in the browser.

### 4.1 Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `url` | `Char` | | Address to open |
| `target` | `Selection` | `new` | `new` (new window), `self` (replace current), `download` (redirect to download) |

### 4.2 XML Example

```xml
<record id="action_open_website" model="ir.actions.act_url">
    <field name="name">Open Website</field>
    <field name="url">https://odoo.com</field>
    <field name="target">new</field>
</record>

<!-- Open in same window -->
<record id="action_redirect" model="ir.actions.act_url">
    <field name="name">Redirect</field>
    <field name="url">https://insightpulseai.com</field>
    <field name="target">self</field>
</record>
```

### 4.3 Returning URL Actions from Python

```python
def action_open_external(self):
    return {
        'type': 'ir.actions.act_url',
        'url': 'https://odoo.com',
        'target': 'new',
    }

def action_download_report(self):
    return {
        'type': 'ir.actions.act_url',
        'url': f'/web/content/{attachment_id}?download=true',
        'target': 'download',
    }

def action_open_map(self):
    return {
        'type': 'ir.actions.act_url',
        'url': f'https://www.google.com/maps/search/{self.partner_id.contact_address}',
        'target': 'new',
    }
```

---

## 5. Server Actions (ir.actions.server)

Execute server-side logic. Versatile action type with multiple states.

### 5.1 Common Fields

| Field | Type | Description |
|-------|------|-------------|
| `model_id` | `Many2one(ir.model)` | Linked Odoo model |
| `state` | `Selection` | Action type: `code`, `object_create`, `object_write`, `multi` |

### 5.2 State: code

Execute Python code.

**Evaluation context variables:**

| Variable | Description |
|----------|-------------|
| `model` | Model object linked via `model_id` |
| `record` / `records` | Record(s) the action is triggered on (can be void) |
| `env` | Odoo Environment |
| `datetime`, `dateutil`, `time`, `timezone` | Python modules |
| `log(message, level='info')` | Log to ir.logging table |
| `Warning` | Warning exception constructor |
| `action` | Variable to set for returning next action to client |

```xml
<!-- Simple server action -->
<record id="action_confirm_records" model="ir.actions.server">
    <field name="name">Confirm Records</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="state">code</field>
    <field name="code">
        records.filtered(lambda r: r.state == 'draft').write({'state': 'confirmed'})
    </field>
</record>

<!-- Server action that returns a next action -->
<record id="action_open_confirmed" model="ir.actions.server">
    <field name="name">Open Confirmed Form</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="state">code</field>
    <field name="code">
        if record.some_condition():
            action = {
                "type": "ir.actions.act_window",
                "view_mode": "form",
                "res_model": record._name,
                "res_id": record.id,
            }
    </field>
</record>

<!-- Server action with logging -->
<record id="action_log_records" model="ir.actions.server">
    <field name="name">Log Record Info</field>
    <field name="model_id" ref="model_res_partner"/>
    <field name="state">code</field>
    <field name="code">
        for rec in records:
            log("Processing partner: %s" % rec.name)
            rec.write({'comment': 'Processed on %s' % datetime.now()})
    </field>
</record>
```

### 5.3 State: object_create

Create a new record in a specified model.

| Field | Description |
|-------|-------------|
| `crud_model_id` | (Required) Model to create the new record in |
| `link_field_id` | M2O to `ir.model.fields`; sets newly created record on current record's field |
| `fields_lines` | Field overrides (One2many) |

**fields_lines attributes:**

| Column | Description |
|--------|-------------|
| `col1` | `ir.model.fields` -- field to set on `crud_model_id` |
| `value` | Value for the field |
| `type` | `value` (literal), `reference` (external ID), `equation` (Python expr) |

```xml
<record id="action_create_task" model="ir.actions.server">
    <field name="name">Create Follow-up Task</field>
    <field name="model_id" ref="model_project_task"/>
    <field name="state">object_create</field>
    <field name="crud_model_id" ref="model_project_task"/>
    <field name="link_field_id" ref="project.field_project_task__parent_id"/>
    <field name="fields_lines">
        <record model="ir.server.object.lines">
            <field name="col1" ref="field_project_task__name"/>
            <field name="value">Follow-up</field>
            <field name="type">value</field>
        </record>
        <record model="ir.server.object.lines">
            <field name="col1" ref="field_project_task__user_id"/>
            <field name="value">record.user_id.id</field>
            <field name="type">equation</field>
        </record>
    </field>
</record>
```

### 5.4 State: object_write

Update the current record(s).

```xml
<record id="action_archive_records" model="ir.actions.server">
    <field name="name">Archive Records</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="state">object_write</field>
    <field name="fields_lines">
        <record model="ir.server.object.lines">
            <field name="col1" ref="field_my_model__active"/>
            <field name="value">False</field>
            <field name="type">value</field>
        </record>
    </field>
</record>
```

### 5.5 State: multi

Execute multiple sub-actions in sequence.

```xml
<record id="action_multi_step" model="ir.actions.server">
    <field name="name">Multi-Step Action</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="state">multi</field>
    <field name="child_ids" eval="[
        (4, ref('action_confirm_records')),
        (4, ref('action_create_task')),
        (4, ref('action_log_records')),
    ]"/>
</record>
```

If sub-actions return actions, the last returned action is sent to the client.

### 5.6 Server Action Bound to Action Menu

```xml
<record id="action_mass_confirm" model="ir.actions.server">
    <field name="name">Mass Confirm</field>
    <field name="model_id" ref="model_sale_order"/>
    <field name="binding_model_id" ref="model_sale_order"/>
    <field name="binding_view_types">list</field>
    <field name="state">code</field>
    <field name="code">
        records.filtered(lambda o: o.state == 'draft').action_confirm()
    </field>
</record>
```

---

## 6. Report Actions (ir.actions.report)

Trigger report printing/generation.

### 6.1 Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | `Char` | | Report name (used as filename if no `print_report_name`) |
| `model` | `Char` | | Model the report is about |
| `report_type` | `Selection` | `qweb-pdf` | `qweb-pdf` or `qweb-html` |
| `report_name` | `Char` | | External ID of the QWeb template |
| `print_report_name` | `Char` | | Python expression for the report filename |
| `groups_id` | `Many2many` | | Groups allowed to use the report |
| `multi` | `Boolean` | `False` | If True, not shown on form view |
| `paperformat_id` | `Many2one` | | Paper format (defaults to company format) |
| `attachment_use` | `Boolean` | `False` | Store and reuse generated report |
| `attachment` | `Char` | | Python expression for attachment name |
| `binding_model_id` | `Many2one` | | Model to show report in Print menu |
| `binding_type` | `Selection` | `report` | Implicit default for ir.actions.report |

### 6.2 XML Examples

#### Basic PDF Report

```xml
<record id="action_report_invoice" model="ir.actions.report">
    <field name="name">Invoice Report</field>
    <field name="model">account.move</field>
    <field name="report_type">qweb-pdf</field>
    <field name="report_name">my_module.report_invoice_template</field>
    <field name="print_report_name">'Invoice - %s' % (object.name)</field>
    <field name="binding_model_id" ref="account.model_account_move"/>
</record>
```

#### Report with Attachment Storage

```xml
<record id="action_report_contract" model="ir.actions.report">
    <field name="name">Contract</field>
    <field name="model">my.contract</field>
    <field name="report_type">qweb-pdf</field>
    <field name="report_name">my_module.report_contract_template</field>
    <field name="print_report_name">'Contract - %s' % (object.name)</field>
    <field name="attachment_use" eval="True"/>
    <field name="attachment">'Contract - %s.pdf' % (object.name)</field>
    <field name="binding_model_id" ref="model_my_contract"/>
</record>
```

#### HTML Report

```xml
<record id="action_report_summary" model="ir.actions.report">
    <field name="name">Summary Report</field>
    <field name="model">my.model</field>
    <field name="report_type">qweb-html</field>
    <field name="report_name">my_module.report_summary_template</field>
    <field name="binding_model_id" ref="model_my_model"/>
</record>
```

#### Report with Group Restriction

```xml
<record id="action_report_confidential" model="ir.actions.report">
    <field name="name">Confidential Report</field>
    <field name="model">my.model</field>
    <field name="report_type">qweb-pdf</field>
    <field name="report_name">my_module.report_confidential</field>
    <field name="groups_id" eval="[(4, ref('base.group_system'))]"/>
    <field name="binding_model_id" ref="model_my_model"/>
</record>
```

### 6.3 Using <report> Shortcut Tag

Note: The `<record>` approach is preferred. If using `<report>`, `binding_model_id`
must be set explicitly for it to appear in the Print menu.

### 6.4 Returning Report Actions from Python

```python
def action_print_report(self):
    return self.env.ref('my_module.action_report_invoice').report_action(self)

def action_print_custom(self):
    return {
        'type': 'ir.actions.report',
        'report_name': 'my_module.report_template',
        'report_type': 'qweb-pdf',
        'data': {'custom_key': 'custom_value'},
    }
```

---

## 7. Client Actions (ir.actions.client)

Trigger an action implemented entirely in the client (JavaScript).

### 7.1 Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `tag` | `Char` | | Client-side identifier string |
| `params` | `Text` | | Python dict of additional data for the client |
| `target` | `Selection` | `current` | `current`, `fullscreen`, `new`, `main` |

### 7.2 XML Example

```xml
<record id="action_pos_ui" model="ir.actions.client">
    <field name="name">Point of Sale</field>
    <field name="tag">pos.ui</field>
    <field name="target">fullscreen</field>
</record>

<record id="action_custom_dashboard" model="ir.actions.client">
    <field name="name">Custom Dashboard</field>
    <field name="tag">my_module.dashboard</field>
    <field name="target">current</field>
    <field name="params" eval="{'default_period': 'month'}"/>
</record>
```

### 7.3 Returning Client Actions from Python

```python
def action_open_dashboard(self):
    return {
        'type': 'ir.actions.client',
        'tag': 'my_module.dashboard',
        'params': {'model': self._name, 'ids': self.ids},
    }

def action_reload(self):
    return {
        'type': 'ir.actions.client',
        'tag': 'reload',
    }

def action_display_notification(self):
    return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
            'title': 'Success',
            'message': 'Operation completed.',
            'type': 'success',
            'sticky': False,
        },
    }
```

---

## 8. Scheduled Actions (ir.cron)

Automatically triggered actions on a predefined frequency.

### 8.1 Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | `Char` | Name (used in log display) |
| `model_id` | `Many2one(ir.model)` | Model to call the method on |
| `code` | `Text` | Python code to execute (typically `model.method()`) |
| `interval_number` | `Integer` | Number of interval units between executions |
| `interval_type` | `Selection` | `minutes`, `hours`, `days`, `weeks`, `months` |
| `nextcall` | `Datetime` | Next planned execution date/time |
| `priority` | `Integer` | Execution priority (lower = higher priority) |

### 8.2 XML Example

```xml
<odoo>
    <data noupdate="1">
        <!-- Run daily -->
        <record id="cron_cleanup_records" model="ir.cron">
            <field name="name">My Module: Cleanup Old Records</field>
            <field name="model_id" ref="model_my_model"/>
            <field name="interval_number">1</field>
            <field name="interval_type">days</field>
            <field name="numbercall">-1</field>
            <field name="code">model._cron_cleanup()</field>
        </record>

        <!-- Run every 15 minutes -->
        <record id="cron_sync_data" model="ir.cron">
            <field name="name">My Module: Sync External Data</field>
            <field name="model_id" ref="model_my_model"/>
            <field name="interval_number">15</field>
            <field name="interval_type">minutes</field>
            <field name="numbercall">-1</field>
            <field name="code">model._cron_sync_external()</field>
            <field name="priority">5</field>
        </record>

        <!-- Run weekly -->
        <record id="cron_weekly_report" model="ir.cron">
            <field name="name">My Module: Weekly Summary</field>
            <field name="model_id" ref="model_my_model"/>
            <field name="interval_number">1</field>
            <field name="interval_type">weeks</field>
            <field name="numbercall">-1</field>
            <field name="code">model._cron_weekly_summary()</field>
        </record>
    </data>
</odoo>
```

### 8.3 Writing Cron Functions (Batch Processing)

Cron functions should process work in batches. Each call processes some records
and the framework calls the function again until all work is done.

**Basic batch pattern:**

```python
def _cron_do_something(self, *, limit=300):
    domain = [('state', '=', 'ready')]
    records = self.search(domain, limit=limit)
    records.do_something()
    # Notify progression
    remaining = 0 if len(records) < limit else self.search_count(domain)
    self.env['ir.cron']._commit_progress(len(records), remaining=remaining)
```

**Advanced pattern with loop control and error handling:**

```python
def _cron_do_something(self):
    assert self.env.context.get('cron_id'), "Run only inside cron jobs"
    domain = [('state', '=', 'ready')]
    records = self.search(domain)
    self.env['ir.cron']._commit_progress(remaining=len(records))

    with open_some_connection() as conn:
        for record in records:
            # Lock record, check existence, verify domain still matches
            record = record.try_lock_for_update().filtered_domain(domain)
            if not record:
                continue
            try:
                record.do_something(conn)
                if not self.env['ir.cron']._commit_progress(1):
                    break  # time is up, stop processing
            except Exception:
                self.env.cr.rollback()
                _logger.warning("Error processing record %s", record.id)
```

### 8.4 _commit_progress

`ir.cron._commit_progress(done=0, remaining=0)` commits the current batch work
and returns the number of seconds remaining for the cron execution. If it returns
`0`, the function must return as soon as possible.

### 8.5 Running Cron Functions

Do not call cron functions directly. Use these methods:

```python
# Manual trigger (from UI or tests)
cron_record.method_direct_trigger()

# Programmatic trigger (schedule next run)
self.env['ir.cron']._trigger(cron_xmlid='my_module.cron_sync_data')
```

### 8.6 Cron Security

- If a cron fails 3 consecutive times: skips current execution
- If a cron fails 5 consecutive times over 7+ days: deactivated, DB admin notified
- Hard time limit exists at database level (process killed if exceeded)

### 8.7 Testing Cron Functions

```python
from odoo.tests import TransactionCase

class TestCron(TransactionCase):
    def test_cron_cleanup(self):
        # Create test data
        self.env['my.model'].create([
            {'name': 'Old', 'state': 'ready'},
            {'name': 'New', 'state': 'draft'},
        ])
        # Run cron via method_direct_trigger
        cron = self.env.ref('my_module.cron_cleanup_records')
        cron.method_direct_trigger()
        # Verify results
        remaining = self.env['my.model'].search_count([('state', '=', 'ready')])
        self.assertEqual(remaining, 0)
```

---

## 9. Common Action Patterns

### 9.1 Action Returning from Button Method

```python
# In your model:
def action_view_deliveries(self):
    """Open deliveries related to this sales order."""
    self.ensure_one()
    deliveries = self.env['stock.picking'].search([
        ('origin', '=', self.name),
    ])
    if len(deliveries) == 1:
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'views': [[False, 'form']],
            'res_id': deliveries.id,
        }
    return {
        'type': 'ir.actions.act_window',
        'name': 'Deliveries',
        'res_model': 'stock.picking',
        'views': [[False, 'list'], [False, 'form']],
        'domain': [('id', 'in', deliveries.ids)],
    }
```

### 9.2 Wizard Action Pattern

```xml
<!-- Wizard action (opens in dialog) -->
<record id="action_my_wizard" model="ir.actions.act_window">
    <field name="name">My Wizard</field>
    <field name="res_model">my.wizard</field>
    <field name="view_mode">form</field>
    <field name="target">new</field>
    <field name="binding_model_id" ref="model_my_model"/>
    <field name="binding_view_types">list,form</field>
</record>
```

### 9.3 Homepage/Dashboard Action

```xml
<!-- Set as module homepage action -->
<record id="action_my_module_homepage" model="ir.actions.client">
    <field name="name">My Module Dashboard</field>
    <field name="tag">my_module.homepage</field>
</record>

<menuitem id="menu_my_module_root"
          name="My Module"
          action="action_my_module_homepage"
          sequence="10"/>
```

### 9.4 Close Dialog Action

```python
def action_done(self):
    """Close the wizard and return."""
    return {'type': 'ir.actions.act_window_close'}
```

### 9.5 Smart Button Pattern

```xml
<!-- In form view -->
<button class="oe_stat_button" type="object"
        name="action_view_deliveries"
        icon="fa-truck">
    <field string="Deliveries" name="delivery_count" widget="statinfo"/>
</button>
```

```python
delivery_count = fields.Integer(compute='_compute_delivery_count')

def _compute_delivery_count(self):
    for record in self:
        record.delivery_count = self.env['stock.picking'].search_count([
            ('origin', '=', record.name),
        ])

def action_view_deliveries(self):
    self.ensure_one()
    return {
        'type': 'ir.actions.act_window',
        'name': 'Deliveries',
        'res_model': 'stock.picking',
        'views': [[False, 'list'], [False, 'form']],
        'domain': [('origin', '=', self.name)],
        'context': {'create': False},
    }
```

---

## 10. Action Type Summary

| Action Type | Model | Primary Use |
|-------------|-------|-------------|
| Window Action | `ir.actions.act_window` | Open model views (list, form, kanban, etc.) |
| URL Action | `ir.actions.act_url` | Open external/internal URLs |
| Server Action | `ir.actions.server` | Execute Python code, create/write records, multi-actions |
| Report Action | `ir.actions.report` | Generate PDF/HTML reports |
| Client Action | `ir.actions.client` | Trigger client-side JavaScript actions |
| Scheduled Action | `ir.cron` | Automated periodic background tasks |
