---
name: odoo19-coding-guidelines
description: Odoo 19 coding guidelines for module structure, file naming, XML IDs, Python conventions, JavaScript, and CSS/SCSS naming
metadata:
  author: odoo/documentation
  version: "19.0"
  source: "content/contributing/development/coding_guidelines.rst"
  extracted: "2026-02-17"
---

# Odoo 19 Coding Guidelines

Comprehensive coding standards for Odoo module development. Covers module directory structure, file naming, XML conventions, Python style, JavaScript conventions, and CSS/SCSS naming patterns.

---

## 1. Module Directory Structure

### Required Directories

| Directory | Purpose |
|---|---|
| `data/` | Demo and data XML files |
| `models/` | Python model definitions |
| `controllers/` | HTTP route controllers |
| `views/` | Backend views and portal templates |
| `static/` | Web assets: `css/`, `js/`, `img/`, `lib/` |

### Optional Directories

| Directory | Purpose |
|---|---|
| `wizard/` | Transient models (`models.TransientModel`) and their views |
| `report/` | Printable reports, SQL view reports |
| `tests/` | Python test files |
| `security/` | Access rights, groups, record rules |
| `i18n/` | Translation files (.po, .pot) |
| `migrations/` or `upgrades/` | Upgrade scripts |

### Complete Module Tree Example

```
addons/plant_nursery/
|-- __init__.py
|-- __manifest__.py
|-- controllers/
|   |-- __init__.py
|   |-- plant_nursery.py
|   |-- portal.py
|-- data/
|   |-- plant_nursery_data.xml
|   |-- plant_nursery_demo.xml
|   |-- mail_data.xml
|-- models/
|   |-- __init__.py
|   |-- plant_nursery.py
|   |-- plant_order.py
|   |-- res_partner.py
|-- report/
|   |-- __init__.py
|   |-- plant_order_report.py
|   |-- plant_order_report_views.xml
|   |-- plant_order_reports.xml
|   |-- plant_order_templates.xml
|-- security/
|   |-- ir.model.access.csv
|   |-- plant_nursery_groups.xml
|   |-- plant_nursery_security.xml
|   |-- plant_order_security.xml
|-- static/
|   |-- img/
|   |   |-- my_little_kitten.png
|   |   |-- troll.jpg
|   |-- lib/
|   |   |-- external_lib/
|   |-- src/
|   |   |-- js/
|   |   |   |-- widget_a.js
|   |   |   |-- widget_b.js
|   |   |-- scss/
|   |   |   |-- widget_a.scss
|   |   |   |-- widget_b.scss
|   |   |-- xml/
|   |   |   |-- widget_a.xml
|   |   |   |-- widget_b.xml
|-- views/
|   |-- plant_nursery_menus.xml
|   |-- plant_nursery_views.xml
|   |-- plant_nursery_templates.xml
|   |-- plant_order_views.xml
|   |-- plant_order_templates.xml
|   |-- res_partner_views.xml
|-- wizard/
|   |-- make_plant_order.py
|   |-- make_plant_order_views.xml
```

### File Permissions

- Folders: `755`
- Files: `644`
- Filenames: only `[a-z0-9_]` (lowercase alphanumerics and underscore)

---

## 2. File Naming Conventions

### Models

Split business logic by main model sets. Each file is named after its main model.

```
models/
|-- plant_nursery.py       # plant.nursery model
|-- plant_order.py         # plant.order model
|-- res_partner.py         # inherited res.partner model
```

Rules:
- If there is only one model, name the file the same as the module
- Each inherited model gets its own file
- Group related sub-models with the main model file

### Security

```
security/
|-- ir.model.access.csv           # Access rights
|-- plant_nursery_groups.xml      # User groups: <module>_groups.xml
|-- plant_nursery_security.xml    # Record rules: <model>_security.xml
|-- plant_order_security.xml
```

### Views

Backend views are suffixed `_views.xml`. Templates are suffixed `_templates.xml`.

```
views/
|-- plant_nursery_menus.xml       # Optional: main menus
|-- plant_nursery_views.xml       # Backend views (list, form, kanban, etc.)
|-- plant_nursery_templates.xml   # Portal/website templates
|-- plant_order_views.xml
|-- plant_order_templates.xml
|-- res_partner_views.xml         # Inherited views
```

### Data

```
data/
|-- plant_nursery_data.xml        # <main_model>_data.xml
|-- plant_nursery_demo.xml        # <main_model>_demo.xml
|-- mail_data.xml                 # Related module data
```

### Controllers

```
controllers/
|-- plant_nursery.py              # Main controller: <module_name>.py
|-- portal.py                     # Inherited controller: <inherited_module>.py
```

Note: `main.py` is the old convention -- use `<module_name>.py` instead.

### Wizards

```
wizard/
|-- make_plant_order.py           # <transient>.py
|-- make_plant_order_views.xml    # <transient>_views.xml
```

### Reports

```
report/
|-- plant_order_report.py              # SQL view report model
|-- plant_order_report_views.xml       # Report views
|-- plant_order_reports.xml            # Report actions, paperformat
|-- plant_order_templates.xml          # QWeb report templates
```

### Static Files

```
static/
|-- lib/               # External JS libraries (in subfolders)
|-- src/
|   |-- css/           # CSS files
|   |-- js/            # JavaScript components
|   |   |-- tours/     # End-user tours (tutorials, not tests)
|   |-- scss/          # SCSS files
|   |-- xml/           # QWeb templates rendered in JS
|-- tests/             # Test-related static files
|   |-- tours/         # Tour test files (not tutorials)
```

Each JS component should be in its own file with a meaningful name. Do not link external resources via URL -- copy assets into the codebase.

---

## 3. XML File Conventions

### Record Notation

Use `<record>` notation. Place `id` before `model`. For fields, `name` attribute comes first.

```xml
<record id="view_id" model="ir.ui.view">
    <field name="name">view.name</field>
    <field name="model">object_name</field>
    <field name="priority" eval="16"/>
    <field name="arch" type="xml">
        <list>
            <field name="my_field_1"/>
            <field name="my_field_2"
                   string="My Label"
                   widget="statusbar"
                   statusbar_visible="draft,sent,progress,done"/>
        </list>
    </field>
</record>
```

### Syntactic Sugar Tags

Use these shortcut tags when available (preferred over `<record>`):

- `<menuitem>` -- shortcut for `ir.ui.menu`
- `<template>` -- shortcut for QWeb views (only `arch` section needed)

### noupdate Data

Use `<data noupdate="1">` wrapper, or set `noupdate=1` on the `<odoo>` tag if the entire file is noupdate:

```xml
<odoo noupdate="1">
    <record id="..." model="...">
        ...
    </record>
</odoo>
```

---

## 4. XML ID Naming Conventions

### Views

Pattern: `<model_name>_view_<view_type>`

```xml
<!-- Form view -->
<record id="model_name_view_form" model="ir.ui.view">
    <field name="name">model.name.view.form</field>
    ...
</record>

<!-- Kanban view -->
<record id="model_name_view_kanban" model="ir.ui.view">
    <field name="name">model.name.view.kanban</field>
    ...
</record>

<!-- List view -->
<record id="model_name_view_list" model="ir.ui.view">
    <field name="name">model.name.view.list</field>
    ...
</record>

<!-- Search view -->
<record id="model_name_view_search" model="ir.ui.view">
    <field name="name">model.name.view.search</field>
    ...
</record>
```

### Actions

Pattern: `<model_name>_action` (main), `<model_name>_action_<detail>` (others)

```xml
<!-- Main action -->
<record id="model_name_action" model="ir.actions.act_window">
    <field name="name">Model Main Action</field>
    ...
</record>

<!-- Secondary action with detail -->
<record id="model_name_action_child_list" model="ir.actions.act_window">
    <field name="name">Model Access Children</field>
    ...
</record>

<!-- Window action with view type -->
<record id="model_name_action_view_kanban" model="ir.actions.act_window">
    ...
</record>
```

### Menus

Pattern: `<model_name>_menu`, `<model_name>_menu_<detail>`

```xml
<menuitem
    id="model_name_menu_root"
    name="Main Menu"
    sequence="5"
/>
<menuitem
    id="model_name_menu_action"
    name="Sub Menu 1"
    parent="module_name.module_name_menu_root"
    action="model_name_action"
    sequence="10"
/>
```

### Security Groups

Pattern: `<module_name>_group_<group_name>`

```xml
<record id="module_name_group_user" model="res.groups">
    ...
</record>

<record id="module_name_group_manager" model="res.groups">
    ...
</record>
```

### Record Rules

Pattern: `<model_name>_rule_<concerned_group>`

```xml
<record id="model_name_rule_public" model="ir.rule">
    ...
</record>

<record id="model_name_rule_company" model="ir.rule">
    ...
</record>

<record id="model_name_rule_user" model="ir.rule">
    ...
</record>
```

### Name Field Convention

The `name` field value should be identical to the XML ID with dots replacing underscores:

| XML ID | Name Field |
|---|---|
| `model_name_view_form` | `model.name.view.form` |
| `model_name_view_kanban` | `model.name.view.kanban` |

Exception: Actions should have a human-readable name (used as display name).

### Inheriting Views

Use the **same ID** as the original record. Add `.inherit.<detail>` to the name:

```xml
<record id="model_view_form" model="ir.ui.view">
    <field name="name">model.view.form.inherit.module2</field>
    <field name="inherit_id" ref="module1.model_view_form"/>
    ...
</record>
```

New primary views based on an existing view do **not** need the inherit suffix:

```xml
<record id="module2.model_view_form" model="ir.ui.view">
    <field name="name">model.view.form.module2</field>
    <field name="inherit_id" ref="module1.model_view_form"/>
    <field name="mode">primary</field>
    ...
</record>
```

---

## 5. Python Guidelines

### PEP8 Notes

Odoo follows PEP8 with these **ignored** rules:

| Rule | Description |
|---|---|
| E501 | Line too long |
| E301 | Expected 1 blank line, found 0 |
| E302 | Expected 2 blank lines, found 1 |

### Import Order

Three groups, alphabetically sorted within each:

```python
# 1: Python standard library
import base64
import re
import time
from datetime import datetime

# 2: Odoo submodules
from odoo import Command, _, api, fields, models  # ASCIIbetically ordered
from odoo.fields import Domain
from odoo.tools.safe_eval import safe_eval as eval

# 3: Odoo addons (rarely, only if necessary)
from odoo.addons.web.controllers.main import login_redirect
from odoo.addons.website.models.website import slug
```

### Python Idioms

**Dictionary creation:**

```python
# BAD
my_dict = {}
my_dict['foo'] = 3
my_dict['bar'] = 4

# GOOD
my_dict = {'foo': 3, 'bar': 4}
```

**Dictionary update:**

```python
# BAD
my_dict['foo'] = 3
my_dict['bar'] = 4
my_dict['baz'] = 5

# GOOD
my_dict.update(foo=3, bar=4, baz=5)
my_dict = dict(my_dict, **my_dict2)
```

**Cloning:**

```python
# BAD
new_dict = my_dict.clone()
new_list = old_list.clone()

# GOOD
new_dict = dict(my_dict)
new_list = list(old_list)
```

**Avoid useless temp variables:**

```python
# POINTLESS
schema = kw['schema']
params = {'schema': schema}

# SIMPLER
params = {'schema': kw['schema']}
```

**Multiple return points are OK:**

```python
# GOOD -- clearer
def axes(self, axis):
    if type(axis) == type([]):
        return list(axis)
    else:
        return [axis]
```

**Use builtins properly:**

```python
value = my_dict.get('key', None)  # REDUNDANT
value = my_dict.get('key')         # GOOD
```

**List comprehensions:**

```python
# BAD
cube = []
for i in res:
    cube.append((i['id'], i['name']))

# GOOD
cube = [(i['id'], i['name']) for i in res]
```

**Collections are booleans:**

```python
# BAD
if len(some_collection):

# GOOD
if some_collection:
```

**Iterate properly:**

```python
# BAD
for key in my_dict.keys():
    ...

# GOOD
for key in my_dict:
    ...

# Access key-value pairs
for key, value in my_dict.items():
    ...
```

**Use setdefault:**

```python
# BAD
values = {}
for element in iterable:
    if element not in values:
        values[element] = []
    values[element].append(other_value)

# GOOD
values = {}
for element in iterable:
    values.setdefault(element, []).append(other_value)
```

---

## 6. ORM Programming Conventions

### Use filtered, mapped, sorted

```python
# Prefer these ORM methods for readability and performance
partners = self.env['res.partner'].search([])
emails = partners.filtered(lambda r: r.is_company).mapped('email')
sorted_partners = partners.sorted(key=lambda r: r.name)
```

### Context Propagation

```python
# Replace entire context
records.with_context(new_context).do_stuff()

# Add to existing context
records.with_context(**additional_context).do_other_stuff()
```

**Warning**: Context keys propagate automatically. A `default_my_field` key will set defaults on any model that has a `my_field` during that call chain. Prefix context keys with module name:

```python
# GOOD -- namespaced context keys
records.with_context(mail_create_nosubscribe=True)
records.with_context(sale_default_warehouse_id=warehouse.id)
```

### Extendable Code Pattern

```python
# BAD -- hard to extend
def action(self):
    ...
    partners = self.env['res.partner'].search(complex_domain)
    emails = partners.filtered(lambda r: arbitrary_criteria).mapped('email')

# BETTER -- but still duplicates code on override
def action(self):
    ...
    partners = self._get_partners()
    emails = partners._get_emails()

# BEST -- minimal override needed
def action(self):
    ...
    partners = self.env['res.partner'].search(self._get_partner_domain())
    emails = partners.filtered(lambda r: r._filter_partners()).mapped('email')
```

### Never Commit the Transaction

```python
# NEVER do this (unless you created your own cursor with explicit justification)
cr.commit()
cr.rollback()
```

The framework handles transactions. Manual commits cause:
- Inconsistent business data / data loss
- Workflow desynchronization
- Broken test rollback

### Exception Handling

```python
# BAD -- too broad, may leave ORM in undefined state
try:
    do_something()
except Exception as e:
    _logger.warning(e)

# GOOD -- use savepoints for isolation
try:
    with self.env.cr.savepoint():
        do_stuff()
except SpecificException:
    ...
```

**Warning**: More than 64 savepoints per transaction degrades PostgreSQL performance. Limit batch sizes when using savepoints in loops.

### Translation Method `_()`

```python
_ = self.env._

# GOOD: plain strings
error = _('This record is locked!')

# GOOD: strings with formatting patterns
error = _('Record %s cannot be modified!', record)

# GOOD: multi-line
error = _("Answer to question %(title)s is not valid.\n"
          "Please enter an integer value.", title=question)

# BAD: formatting BEFORE translation (does NOT work)
error = _('Record %s cannot be modified!' % record)

# BAD: formatting OUTSIDE translation (loses fallback mechanism)
error = _('Record %s cannot be modified!') % record

# BAD: dynamic string (does NOT work)
error = _("'" + que_rec['question'] + "' \n")

# BAD: translating field values (useless, framework does this)
error = _("Product %s is out of stock!") % _(product.name)

# GOOD: field values are auto-translated by framework
error = _("Product %s is not available!", product.name)
```

Prefer `%` over `.format()` for single variables. Prefer `%(varname)s` for multiple variables.

---

## 7. Naming Conventions for Python

### Model Names (dot notation)

| Type | Convention | Example |
|---|---|---|
| Regular model | Singular form | `res.partner`, `sale.order` |
| Transient (wizard) | `<base_model>.<action>` | `account.invoice.make`, `project.task.delegate.batch` |
| Report (SQL view) | `<base_model>.report.<action>` | `sale.order.report.summary` |

### Python Class Names

Use **PascalCase**:

```python
class AccountInvoice(models.Model):
    ...
```

### Variable Names

```python
# PascalCase for model variables
Partner = self.env['res.partner']

# Underscore lowercase for regular variables
partners = Partner.browse(ids)
partner_id = partners[0].id  # ID value, not a record
```

### Field Name Suffixes

| Field Type | Suffix | Example |
|---|---|---|
| `Many2One` | `_id` | `partner_id`, `user_id` |
| `One2Many` | `_ids` | `sale_order_line_ids` |
| `Many2Many` | `_ids` | `tag_ids` |

**Important**: `partner_id` should contain an integer ID, not a record. Use `partner` for the record variable.

### Method Naming Conventions

| Method Type | Pattern | Example |
|---|---|---|
| Compute | `_compute_<field_name>` | `_compute_amount_total` |
| Search | `_search_<field_name>` | `_search_partner_name` |
| Default | `_default_<field_name>` | `_default_company_id` |
| Selection | `_selection_<field_name>` | `_selection_state` |
| Onchange | `_onchange_<field_name>` | `_onchange_partner_id` |
| Constraint | `_check_<constraint_name>` | `_check_seats_limit` |
| Action | `action_<name>` | `action_validate`, `action_confirm` |

---

## 8. Model Attribute Order

Within a model class, attributes and methods should follow this order:

```python
class Event(models.Model):
    # 1. Private attributes
    _name = 'event.event'
    _description = 'Event'
    _inherit = ['mail.thread']
    _order = 'date_begin DESC'

    # 2. Default methods
    def _default_name(self):
        ...

    # 3. Field declarations
    name = fields.Char(string='Name', default=_default_name)
    seats_reserved = fields.Integer(
        string='Reserved Seats',
        store=True,
        readonly=True,
        compute='_compute_seats',
    )
    seats_available = fields.Integer(
        string='Available Seats',
        store=True,
        readonly=True,
        compute='_compute_seats',
    )
    price = fields.Integer(string='Price')
    event_type = fields.Selection(
        string="Type",
        selection='_selection_type',
    )

    # 4. SQL constraints and indexes
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Event name must be unique!'),
    ]

    # 5. Compute, inverse, search methods (same order as field declaration)
    @api.depends('seats_max', 'registration_ids.state', 'registration_ids.nb_register')
    def _compute_seats(self):
        ...

    # 6. Selection methods
    @api.model
    def _selection_type(self):
        return []

    # 7. Constraints and onchanges
    @api.constrains('seats_max', 'seats_available')
    def _check_seats_limit(self):
        ...

    @api.onchange('date_begin')
    def _onchange_date_begin(self):
        ...

    # 8. CRUD methods (and name_search, _search, ...) overrides
    @api.model
    def create(self, vals_list):
        ...

    # 9. Action methods
    def action_validate(self):
        self.ensure_one()
        ...

    # 10. Business methods
    def mail_user_confirm(self):
        ...
```

---

## 9. JavaScript Guidelines

### Static File Organization

```
static/
|-- lib/                    # External libraries (in subfolders)
|-- src/                    # Source code
|   |-- css/                # CSS files
|   |-- js/                 # JavaScript files
|   |   |-- tours/          # End-user tours (tutorials)
|   |-- scss/               # SCSS files
|   |-- xml/                # QWeb templates for JS rendering
|-- tests/                  # Test files
|   |-- tours/              # Tour tests
```

Files are served statically at: `your-server.com/<addon>/static/...`

### JavaScript Coding Rules

- Use `"use strict";` in all JavaScript files
- Use a linter (jshint, eslint)
- Never add minified libraries
- Use **PascalCase** for class declarations
- Each component in its own file with a meaningful name
- Do not link external data (images, libs) via URL -- copy into codebase

---

## 10. CSS and SCSS Guidelines

### Formatting Rules

```scss
.o_foo, .o_foo_bar, .o_baz {
    height: $o-statusbar-height;

    .o_qux {
        height: $o-statusbar-height * 0.5;
    }
}

.o_corge {
    background: $o-list-footer-bg-color;
}
```

| Rule | Standard |
|---|---|
| Indentation | 4 spaces, no tabs |
| Max line width | 80 characters |
| Opening brace `{` | Space after last selector |
| Closing brace `}` | Own new line |
| Declarations | One per line |
| Whitespace | Meaningful use |

### CSS Class Naming

Prefix classes with `o_<module_name>`:

| Module | Prefix | Example |
|---|---|---|
| `sale` | `o_sale_` | `.o_sale_order_form` |
| `im_chat` | `o_im_chat_` | `.o_im_chat_window` |
| `website_forum` | `o_forum_` | `.o_forum_post` (uses main route) |
| Webclient | `o_` | `.o_main_navbar` |

Avoid `id` selectors. Avoid hyper-specific class nesting:

```html
<!-- BAD: too deeply nested names -->
<div class="o_element_wrapper">
    <div class="o_element_wrapper_entries">
        <span class="o_element_wrapper_entries_entry">
            <a class="o_element_wrapper_entries_entry_link">Entry</a>
        </span>
    </div>
</div>

<!-- GOOD: "Grandchild" approach -->
<div class="o_element_wrapper">
    <div class="o_element_entries">
        <span class="o_element_entry">
            <a class="o_element_link">Entry</a>
        </span>
    </div>
</div>
```

### Properties Order

Order from "outside" in:

```scss
.o_element {
    // 1. Scoped SCSS variables
    $-inner-gap: $border-width + $legend-margin-bottom;

    // 2. CSS variables
    --element-margin: 1rem;
    --element-size: 3rem;

    // 3. Position
    @include o-position-absolute(1rem);

    // 4. Display/layout
    display: block;

    // 5. Box model (margin -> border -> padding)
    margin: var(--element-margin);
    width: calc(var(--element-size) + #{$-inner-gap});
    border: 0;
    padding: 1rem;

    // 6. Background
    background: blue;

    // 7. Typography
    font-size: 1rem;

    // 8. Decorative
    filter: blur(2px);
}
```

### SCSS Variable Naming

Convention: `$o-[root]-[element]-[property]-[modifier]`

| Component | Description |
|---|---|
| `$o-` | Required prefix |
| `[root]` | Component or module name |
| `[element]` | Optional inner element identifier |
| `[property]` | The property/behavior |
| `[modifier]` | Optional modifier (hover, active, etc.) |

```scss
$o-block-color: value;
$o-block-title-color: value;
$o-block-title-color-hover: value;
```

### Scoped SCSS Variables

Convention: `$-[variable-name]` (declared within blocks, not accessible outside)

```scss
.o_element {
    $-inner-gap: compute-something;

    margin-right: $-inner-gap;

    .o_element_child {
        margin-right: $-inner-gap * 0.5;
    }
}
```

### SCSS Mixins and Functions

Convention: `o-[name]`

- Use descriptive names
- Functions: use imperative verbs (`get`, `make`, `apply`)
- Optional arguments: use scoped variable form `$-[argument]`

```scss
@mixin o-avatar($-size: 1.5em, $-radius: 100%) {
    width: $-size;
    height: $-size;
    border-radius: $-radius;
}

@function o-invert-color($-color, $-amount: 100%) {
    $-inverse: change-color($-color, $-hue: hue($-color) + 180);
    @return mix($-inverse, $-color, $-amount);
}
```

### CSS Variables

Convention: BEM style `--[root]__[element]-[property]--[modifier]`

| Component | Description |
|---|---|
| `[root]` | Component or module name (PascalCase) |
| `[element]` | Optional inner element |
| `[property]` | The property/behavior |
| `[modifier]` | Optional modifier |

```scss
.o_kanban_record {
    --KanbanRecord-width: value;
    --KanbanRecord__picture-border: value;
    --KanbanRecord__picture-border--active: value;
}

// Contextual adaptation
.o_form_view {
    --KanbanRecord-width: another-value;
    --KanbanRecord__picture-border: another-value;
}
```

### CSS Variables Usage Pattern

Define CSS variables inside the component's main block with default fallbacks:

```scss
// component.scss
.o_MyComponent {
    color: var(--MyComponent-color, #313131);
}

// dashboard.scss -- contextual override
.o_MyDashboard {
    --MyComponent-color: #017e84;
}
```

### CSS vs SCSS Variables

| Feature | SCSS Variables | CSS Variables |
|---|---|---|
| Nature | Imperative, compiled away | Declarative, in final output |
| Scope | Lexical | DOM (cascade) |
| Use in Odoo | Design system globals | Contextual DOM adaptations |

Combine both:

```scss
// secondary_variables.scss -- SCSS for global design system
$o-component-color: $o-main-text-color;
$o-dashboard-color: $o-info;

// component.scss -- CSS variable with SCSS fallback
.o_component {
    color: var(--MyComponent-color, #{$o-component-color});
}

// dashboard.scss -- contextual override
.o_dashboard {
    --MyComponent-color: #{$o-dashboard-color};
}
```

### The `:root` Pseudo-class

Defining CSS variables on `:root` is **not used** in Odoo UI. Global design tokens are managed via SCSS. Exception: templates shared across bundles that need contextual awareness.

---

## 11. Existing Code Modification Rules

### Stable Version

When modifying files in a stable version:
- **Never** reformat existing code to match these guidelines
- Keep diffs minimal
- Follow the file's existing style

### Development Version (master)

When modifying files in development:
- Apply guidelines to **modified code only**
- If most of the file is under revision, apply guidelines to the whole file
- For major restructuring: first a **move** commit, then feature changes

---

## 12. Quick Reference Checklist

### New Module Checklist

- [ ] Directory structure follows conventions
- [ ] File names use `[a-z0-9_]` only
- [ ] `__manifest__.py` present with proper metadata
- [ ] `__init__.py` files in all Python directories
- [ ] Models follow attribute ordering
- [ ] XML IDs follow naming conventions
- [ ] Security files present (access rights, groups, rules)
- [ ] Views suffixed with `_views.xml`
- [ ] Data files suffixed with `_data.xml` / `_demo.xml`
- [ ] CSS classes prefixed with `o_<module>_`
- [ ] SCSS variables prefixed with `$o-`
- [ ] JavaScript uses strict mode
- [ ] Imports properly ordered

### Code Review Checklist

- [ ] No `cr.commit()` / `cr.rollback()` without explicit justification
- [ ] Exception handling uses savepoints
- [ ] `_()` translation calls use literal strings only
- [ ] Action methods include `self.ensure_one()`
- [ ] Field names use proper `_id` / `_ids` suffixes
- [ ] Method names follow `_compute_*`, `_search_*`, `action_*` patterns
- [ ] No hardcoded business logic (use helper methods for extensibility)
- [ ] Context keys are namespaced
