---
name: studio
description: Low-code/no-code platform for customizing Odoo models, views, reports, approval rules, and automation rules without writing Python
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# Studio -- Odoo 19.0 Skill Reference

## Overview

Odoo Studio is a visual development environment that lets non-technical users and administrators customize existing Odoo applications or build entirely new ones. It provides drag-and-drop editing of models, fields, views, PDF reports, approval rules, and automation rules. Studio generates a `studio_customization` module that can be exported as a ZIP and imported into other databases. It is available exclusively with Odoo Enterprise.

## Key Concepts

- **Model**: A database table representing a business entity (e.g., sales order, contact). Studio can create new models or extend existing ones.
- **Module / App**: A bundle of models, views, data files, and assets. All apps are modules; larger standalone modules are called apps.
- **Field**: A column on a model defining a data type (char, integer, float, boolean, many2one, one2many, many2many, etc.). Studio exposes 20 field types via 15 underlying ORM types.
- **Widget**: Controls how a field's data is presented and formatted in the UI (e.g., Badge, Phone, Progress Bar, Status Bar, Tags).
- **View**: A UI representation of model data. Categories: General (Form, Activity, Search), Multiple Records (Kanban, List, Map), Timeline (Calendar, Cohort, Gantt), Reporting (Pivot, Graph).
- **Approval Rule**: A multi-step approval workflow attached to a button on a form view, requiring designated users or groups to approve before the action executes.
- **Automation Rule (Automated Action)**: A rule that executes one or more actions when a trigger fires (field change, email event, timing condition, webhook, CRUD event).
- **Webhook**: An external trigger that sends a POST payload to an Odoo-generated URL, invoking an automation rule in real-time.
- **PDF Report**: A QWeb-based printable document (invoice, quotation, etc.) that Studio can create or edit visually.
- **Suggested Features**: Pre-built bundles (Contact details, Pipeline stages, Chatter, Tags, Lines, etc.) that accelerate new model creation.
- **studio_customization**: The auto-generated module containing all Studio changes; exportable/importable as a ZIP.
- **Conditional Block**: An if/else section in a PDF report that shows or hides content based on record data.

## Core Workflows

### 1. Create a New Model / App

1. Open Studio from the main dashboard by clicking the Toggle Studio icon.
2. Click **New** to create a new model or app.
3. Enter a name and select up to 14 **Suggested Features** (Contact details, Pipeline stages, Tags, Picture, Lines, Notes, Monetary value, Company, Chatter, Archiving, User assignment, Date & Calendar, Date range & Gantt, Custom Sorting).
4. Studio generates the model with the selected fields, views (Form, List, Kanban, etc.), and configurations.
5. Add additional fields from the **+ Add** tab in Form or List view.

### 2. Customize a View

1. Navigate to the target record/app in Odoo.
2. Click the Toggle Studio icon to enter Studio.
3. Select the view to edit (Form, List, Kanban, Calendar, etc.) from the Views menu.
4. Drag and drop **New Fields** or **Existing Fields** from the **+ Add** tab.
5. Click a field to edit its **Properties** (Label, Widget, Invisible, Required, Readonly, Domain, Default value, visibility groups).
6. Use the **View** tab to access XML editor (developer mode), set default views, or show invisible elements.

### 3. Configure Approval Rules

1. Open Studio on the target model and switch to Form view.
2. Select the button to which the rule should apply.
3. In the Properties tab, click **Add an approval step**.
4. Set **Approvers** (specific users) and/or **Approver Group**.
5. Optionally set **Users to Notify**, **Description**, and conditional filters.
6. For multi-step approvals, set **Approval Order** numbers and optionally enable **Exclusive Approval**.

### 4. Create an Automation Rule

1. Open Studio, click **Automations**, then **New**.
2. Name the rule and select a **Trigger**:
   - **Values Updated**: fires when specific field values change (e.g., tag added, stage set).
   - **Email Events**: fires on email sent/received.
   - **Timing Conditions**: fires relative to a date field, creation, or last update.
   - **Custom**: On create, On create and edit, On deletion, On UI change.
   - **External**: On webhook.
3. Optionally add **Before Update Domain** and **Apply on** domain conditions.
4. Click **Add an action** in the Actions To Do tab. Available action types:
   - Update Record (Update / Update with AI / Sequence / Compute)
   - Create Record / Duplicate Record
   - Create Activity
   - Send Email / Send SMS / Send WhatsApp
   - Add Followers / Remove Followers
   - Execute Code
   - Send Webhook Notification
   - Multi Actions
5. Click **Save & Close**.

### 5. Create / Edit a PDF Report

1. Navigate to the target model, open Studio, click **Reports**.
2. Click **New** and select report type: **External** (company header/footer), **Internal** (user info header), or **Blank**.
3. Edit the report body using the visual editor:
   - Type `/` to open the powerbox and insert Fields, Tables, Dynamic Tables, Columns, Images.
   - Edit static text directly; dynamic fields appear highlighted in blue.
   - Use conditional blocks (dashed rectangles) to show/hide content based on conditions.
4. Modify report options in the left pane: Report name, Paper format (A4/US Letter), Show in print menu, Limit visibility to groups.
5. For advanced changes, click **Edit sources** to modify the QWeb XML directly.
6. Duplicate standard reports before editing to preserve originals during upgrades.

### 6. Export / Import Studio Customizations

1. **Export**: Click Toggle Studio on the dashboard, then **Export**. Optionally click **Configure data and demo data to export** to select specific models.
2. Download the ZIP file containing the `studio_customization` module.
3. **Import**: On the destination database (same Odoo version + same apps), click Toggle Studio, then **Import**. Upload the ZIP and click **Install**.

## Technical Reference

### Models

| Model (technical) | Purpose |
|---|---|
| `ir.actions.server` | Server actions used by automation rules |
| `base.automation` | Automation rules |
| `studio.approval.rule` | Approval rule definitions |
| `studio.approval.entry` | Approval tracking entries |
| `ir.actions.report` | Report action definitions |
| `ir.ui.view` | View definitions (including Studio XPath overrides) |
| `ir.model` | Model metadata |
| `ir.model.fields` | Field metadata |

### Key Field Types and ORM Mapping

| Studio Field | ORM Type | Notes |
|---|---|---|
| Text | `char` | Widgets: Badge, Copy to Clipboard, Email, Image (URL), Phone, URL |
| Multiline Text | `text` | Widget: Copy to Clipboard |
| Integer | `integer` | Widgets: Percentage Pie, Progress Bar, Handle |
| Decimal | `float` | Widgets: Monetary, Percentage, Percentage Pie, Progress Bar, Time |
| Monetary | `monetary` | Requires a Currency field on the model |
| Html | `html` | Widget: Multiline Text (raw HTML) |
| Date | `date` | Widget: Remaining Days |
| Date & Time | `datetime` | Widgets: Date Range (`daterange`), Remaining Days |
| Checkbox | `boolean` | Widgets: Button, Toggle |
| Selection | `selection` | Widgets: Badge, Badges, Priority, Radio, Status Bar |
| Priority | `selection` | Pre-configured 3-star rating |
| File | `binary` | Widgets: Image, PDF Viewer, Sign |
| Image | `binary` | Image widget by default; sizes: Small, Medium, Large |
| Sign | `binary` | Electronic signature widget |
| Many2One | `many2one` | Widgets: Badge, Radio. Properties: Disable creation, Disable opening, Domain, Typeahead search |
| One2Many | `one2many` | Requires existing Many2One on related model |
| Lines | `one2many` | Table layout for order lines etc. |
| Many2Many | `many2many` | Widgets: Checkboxes, Tags |
| Tags | `many2many` | Tags widget by default; option: Use colors |
| Related Field | `related` | Fetches data via existing relation (no new relationship) |

### Field Properties

- **General**: Invisible, Required, Readonly (all support Conditional filters), Label, Help Tooltip, Widget, Placeholder, Default value, Allow/Forbid visibility to groups.
- **Date & Time specific**: Minimal precision, Maximal precision, Warning for future dates, Date format, Show date/time/seconds, Time interval, Earliest/Latest accepted date.

### PDF Report XML Directives

| Directive | Purpose |
|---|---|
| `t-field="doc.field_name"` | Render a field value |
| `t-options="{'widget': 'date'}"` | Override field widget |
| `t-options-widget="'image'"` | Image widget for binary fields |
| `t-options-width="'64px'"` | Image width |
| `t-if="condition"` | Conditional rendering |
| `t-elif="condition"` | Else-if block |
| `t-else=""` | Else block |
| `t-foreach="doc.line_ids" t-as="line"` | Loop over records |
| `t-out="line.name"` | Output value (escaped) |

### Automation Rule Variables (Execute Code action)

- `env`: ORM environment
- `model`: model of the triggering record (void recordset)
- `record`: record on which the action triggers (may be void)
- `records`: recordset of all triggering records in multi-mode
- `time`, `datetime`, `dateutil`, `timezone`: Python standard libraries
- `float_compare`: precision-aware float comparison
- `log(message, level='info')`: log to `ir.logging`
- `_logger.info(message)`: emit to server logs
- `UserError`: exception class for user-facing warnings
- `Command`: x2many commands namespace
- `action = {...}`: return an action dict

### Webhook Payload (Execute Code action)

- `payload`: parsed JSON body of the incoming POST request
- `payload.get('_model')`: retrieve model technical name
- `payload.get('_id')`: retrieve record ID

## API / RPC Patterns

### Webhook: Update a Sales Order (POST)

```json
POST <webhook_url>
Content-Type: application/json

{
    "_model": "sale.order",
    "_id": "7"
}
```

Target Record expression: `model.env[payload.get('_model')].browse(int(payload.get('_id')))`

### Webhook: Create a Contact (POST with Execute Code)

```json
POST <webhook_url>
Content-Type: application/json

{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890"
}
```

Execute Code action:
```python
contact_name = payload.get('name')
contact_email = payload.get('email')
contact_phone = payload.get('phone')

if contact_name and contact_email:
    new_partner = env['res.partner'].create({
        'name': contact_name,
        'email': contact_email,
        'phone': contact_phone,
        'company_type': 'person',
        'customer_rank': 1,
    })
else:
    raise ValueError("Missing required fields: 'name' and 'email'")
```

### Send Webhook Notification (Outbound)

Automation action type **Send Webhook Notification** sends a POST request to a specified URL with selected field values as JSON payload. Sample Payload preview available in the action configuration.

## Version Notes (19.0)

- **Update with AI** action type added to automation rules (requires Odoo AI app).
- **Date Range** widget now supports optional start/end dates (not just mandatory ranges).
- **Date & Time** fields have expanded properties: Minimal/Maximal precision, Warning for future dates, Date format toggle, Show seconds, Time interval, Earliest/Latest accepted date.
- **Typeahead search** property added to Many2One and Many2Many fields for performance with large datasets.
- **Send WhatsApp** added as an automation action type.
- **Sequence** option added to Update Record action for auto-generating sequential references.
- Seven PDF report layouts available: Light, Boxed, Bold, Striped, Bubble, Wave, Folder.
- **Can Duplicate** option added to Form and List view settings.
- **Column Width (px)** property added to List view fields.

<!-- TODO: Specific breaking changes vs 18.0 not fully enumerated in docs -->

## Common Pitfalls

- **One2Many requires existing Many2One**: You cannot add a One2Many field unless the target model already has a Many2One pointing back. Studio cannot create the reverse relation automatically.
- **Monetary field requires Currency field**: When adding a Monetary field to a model that lacks a Currency field, Studio prompts you to add one first. The Monetary field must be added again after.
- **XML edits in standard views are lost on upgrade**: Always edit Studio-generated inherited views (XPath), never the standard or inherited views directly.
- **Webhook URL is confidential**: Treat it like a secret. If rotated, update all external systems. Misconfigured webhooks can disrupt the database.
- **Timing-based automation rules require manual initialization**: After configuring a time-based trigger, you must navigate to the scheduled action and click **Run manually** to set the initial timestamp; otherwise the rule may fire retroactively on historical records.
