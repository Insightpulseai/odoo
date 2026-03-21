---
name: odoo19-data-files
description: Odoo 19 Data Files - XML records, fields, external identifiers, CSV data, shortcuts (menuitem, template, asset)
metadata:
  author: odoo/documentation
  version: "19.0"
  source: "content/developer/reference/backend/data.rst"
  extracted: "2026-02-17"
---

# Odoo 19 Data Files

Comprehensive reference for Odoo 19 data file formats: XML data files (record, field,
delete, function operations), external identifiers, shortcut elements (menuitem,
template, asset), CSV data files, and the noupdate flag.

---

## 1. Overview

Odoo is data-driven. Modules define records for UI (menus, views), security
(access rights, record rules), reports, and plain data through data files.

Data files are declared in `__manifest__.py` under the `data` key:

```python
{
    'name': 'My Module',
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/my_views.xml',
        'data/my_data.xml',
    ],
}
```

Files are loaded in order. Operations in a file can only reference results of
previously loaded files/operations.

---

## 2. XML Data File Structure

### 2.1 Basic Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <operation/>
    <operation/>
    ...
</odoo>
```

The root element is `<odoo>`. It contains any number of operation elements
executed sequentially.

### 2.2 The noupdate Flag

Controls whether data is reapplied during module updates:

```xml
<odoo>
    <data noupdate="1">
        <!-- Only loaded when INSTALLING the module (odoo-bin -i module) -->
        <!-- NOT reloaded during updates (odoo-bin -u module) -->
        <operation/>
    </data>

    <!-- (Re)loaded at both install and update (odoo-bin -i/-u) -->
    <operation/>
</odoo>
```

**Use `noupdate="1"` for:**
- Record rules (ir.rule)
- Default data that users may customize
- Demo/seed data
- Sequences, email templates, scheduled actions

**Leave without noupdate for:**
- Views (ir.ui.view) -- always want latest
- Access rights (ir.model.access)
- Menu items
- Actions

---

## 3. Core Operations

### 3.1 record

Creates or updates a database record.

**Attributes:**

| Attribute | Required | Description |
|-----------|----------|-------------|
| `model` | Yes | Model name to create/update (e.g., `ir.ui.view`) |
| `id` | Recommended | External identifier. Required for update, strongly recommended for create |
| `context` | No | Context dict to use when creating the record |
| `forcecreate` | No | In update mode, create if record doesn't exist (default: True). Requires `id` |

```xml
<record id="partner_demo" model="res.partner">
    <field name="name">Demo Partner</field>
    <field name="email">demo@example.com</field>
    <field name="is_company" eval="True"/>
</record>
```

### 3.2 field

Defines values for record fields. Must be inside a `<record>` tag.

**Mandatory attribute:** `name` -- the field name to set.

#### 3.2.1 No Value (False)

```xml
<!-- Sets field to False (clears it or avoids default) -->
<field name="parent_id"/>
```

#### 3.2.2 Text Content (Char, Text, Integer, Float, Selection)

```xml
<field name="name">Partner Name</field>
<field name="sequence">10</field>
<field name="state">draft</field>
```

#### 3.2.3 ref Attribute (Many2one, Reference)

Links to another record by external identifier:

```xml
<field name="partner_id" ref="base.partner_demo"/>
<field name="country_id" ref="base.us"/>
<field name="group_id" ref="base.group_user"/>
```

#### 3.2.4 search Attribute (Relational Fields)

Uses a domain to find and set the record:

```xml
<!-- Many2one: uses first result -->
<field name="country_id" search="[('code', '=', 'US')]" model="res.country"/>

<!-- Many2many: uses all results -->
<field name="tag_ids" search="[('name', 'in', ['Important', 'Urgent'])]" model="project.tags"/>
```

#### 3.2.5 eval Attribute (Python Expression)

Evaluates a Python expression. Available context: `time`, `datetime`,
`timedelta`, `relativedelta`, `ref()` function, `obj` (current model).

```xml
<!-- Boolean -->
<field name="active" eval="True"/>

<!-- Integer/Float -->
<field name="sequence" eval="100"/>
<field name="amount" eval="99.99"/>

<!-- Date/Datetime -->
<field name="date_start" eval="time.strftime('%Y-01-01')"/>
<field name="deadline" eval="(datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')"/>

<!-- Many2one by ID -->
<field name="partner_id" eval="ref('base.partner_demo')"/>

<!-- Many2many with Command -->
<field name="group_ids" eval="[(4, ref('base.group_user')), (4, ref('base.group_system'))]"/>

<!-- One2many with Command -->
<field name="line_ids" eval="[
    (0, 0, {'name': 'Line 1', 'qty': 5}),
    (0, 0, {'name': 'Line 2', 'qty': 10}),
]"/>

<!-- Selection -->
<field name="state" eval="'confirmed'"/>

<!-- None/False explicitly -->
<field name="parent_id" eval="False"/>
```

#### 3.2.6 type Attribute

Specifies how to interpret field content:

| Type | Description |
|------|-------------|
| `xml`, `html` | Extract children as document; evaluate `%(external_id)s` patterns |
| `file` | Validate as file path, store as `module,path` |
| `char` | Set content directly without alteration |
| `base64` | Base64-encode content (useful with `file` attribute for images) |
| `int` | Convert to integer |
| `float` | Convert to float |
| `list`, `tuple` | Contains `<value>` elements, produces list/tuple |

```xml
<!-- XML/HTML content -->
<field name="arch" type="xml">
    <form>
        <field name="name"/>
    </form>
</field>

<!-- Base64 image from file -->
<field name="image_1920" type="base64" file="my_module/static/img/logo.png"/>

<!-- File reference -->
<field name="report_file" type="char">my_module/report/template.xml</field>

<!-- List of values -->
<field name="domain" type="list">
    <value type="tuple">
        <value>state</value>
        <value>=</value>
        <value>draft</value>
    </value>
</field>
```

#### 3.2.7 file Attribute (with type="base64")

Load a binary file and base64-encode it:

```xml
<record id="attachment_logo" model="ir.attachment">
    <field name="name">Company Logo</field>
    <field name="datas" type="base64" file="my_module/static/img/logo.png"/>
    <field name="res_model">res.company</field>
</record>
```

#### 3.2.8 External ID References in HTML/XML Content

Use `%(external_id)s` syntax inside `type="html"` or `type="xml"` fields:

```xml
<field name="body_html" type="html">
    <p>Click <a href="/web#id=%(base.partner_admin)d">here</a></p>
</field>
```

Use `%%` to output a literal `%` sign.

---

## 4. delete Operation

Removes previously defined records.

**Attributes:**

| Attribute | Description |
|-----------|-------------|
| `model` | (Required) Model to delete from |
| `id` | External identifier of record to remove |
| `search` | Domain to find records to remove |

`id` and `search` are mutually exclusive.

```xml
<!-- Delete by external ID -->
<delete model="res.partner" id="partner_demo"/>

<!-- Delete by domain search -->
<delete model="res.partner" search="[('name', '=', 'Old Partner')]"/>
```

---

## 5. function Operation

Calls a method on a model with provided parameters.

**Attributes:**

| Attribute | Description |
|-----------|-------------|
| `model` | (Required) Model to call the method on |
| `name` | (Required) Method name to call |
| `eval` | Python expression evaluating to method parameters |

```xml
<odoo>
    <data noupdate="1">
        <!-- Create a record first -->
        <record id="partner_1" model="res.partner">
            <field name="name">Odude</field>
        </record>

        <!-- Call method with eval parameters -->
        <function
            model="res.partner"
            name="send_inscription_notice"
            eval="[[ref('partner_1'), ref('partner_2')]]"/>

        <!-- Nested function: result of inner function becomes parameter -->
        <function model="res.users" name="send_vip_inscription_notice">
            <function
                eval="[[('vip', '=', True)]]"
                model="res.partner"
                name="search"/>
        </function>
    </data>
</odoo>
```

Using `<value>` elements instead of eval:

```xml
<function model="res.partner" name="write">
    <value eval="[ref('partner_1')]"/>
    <value eval="{'name': 'Updated Name'}"/>
</function>
```

---

## 6. External Identifiers

### 6.1 Concept

External identifiers (XML IDs) provide stable, module-scoped references to records.
Format: `module_name.identifier`

```xml
<!-- Defining an external ID -->
<record id="my_partner" model="res.partner">
    <field name="name">My Partner</field>
</record>
<!-- This creates external ID: current_module.my_partner -->

<!-- Referencing from same module -->
<field name="partner_id" ref="my_partner"/>

<!-- Referencing from another module -->
<field name="partner_id" ref="other_module.their_partner"/>
```

### 6.2 Model External ID Convention

For `ir.model.access` CSV, model external IDs follow this pattern:
`model_` + model technical name with `.` replaced by `_`

| Model | External ID |
|-------|-------------|
| `res.partner` | `model_res_partner` |
| `sale.order` | `model_sale_order` |
| `project.task` | `model_project_task` |
| `ipai.project.task` | `model_ipai_project_task` |

### 6.3 Resolving External IDs in Python

```python
# Get record from external ID
record = self.env.ref('module.external_id')

# Get ID only
record_id = self.env.ref('module.external_id').id

# Safe resolution (returns False if not found)
record = self.env.ref('module.external_id', raise_if_not_found=False)
```

---

## 7. Shortcut Elements

### 7.1 menuitem

Shortcut for creating `ir.ui.menu` records:

```xml
<!-- Top-level menu -->
<menuitem
    id="menu_my_module_root"
    name="My Module"
    sequence="10"
/>

<!-- Sub-menu with action -->
<menuitem
    id="menu_my_model_list"
    name="My Models"
    parent="menu_my_module_root"
    action="action_my_model"
    sequence="10"
/>

<!-- Menu with group restriction -->
<menuitem
    id="menu_settings"
    name="Configuration"
    parent="menu_my_module_root"
    groups="base.group_system"
    sequence="100"
/>

<!-- Remove group from menu (prefix with minus) -->
<menuitem
    id="menu_public_page"
    name="Public"
    parent="menu_my_module_root"
    groups="-base.group_no_one"
    sequence="20"
/>
```

**Attributes:**

| Attribute | Description |
|-----------|-------------|
| `id` | External identifier |
| `name` | Menu label. If not set, uses linked action name or record id |
| `parent` | External ID of parent menu item |
| `action` | External ID of action to execute on click |
| `groups` | Comma-separated external IDs of groups. Prefix `-` to remove |
| `sequence` | Display order (lower = first) |

**Name resolution:** If no `name` and no `parent`, tries to parse `name` as
`/`-separated path and finds/creates intermediate menus.

### 7.2 template

Shortcut for creating QWeb views (`ir.ui.view`), requiring only the arch section:

```xml
<!-- Basic QWeb template -->
<template id="my_template" name="My Template">
    <div class="container">
        <h1><t t-esc="title"/></h1>
        <t t-foreach="items" t-as="item">
            <p><t t-esc="item.name"/></p>
        </t>
    </div>
</template>

<!-- Inherited template -->
<template id="my_template_ext" inherit_id="website.layout" name="My Extension">
    <xpath expr="//footer" position="before">
        <div class="custom-banner">Custom content</div>
    </xpath>
</template>

<!-- Primary inherited template -->
<template id="my_primary" inherit_id="website.layout" primary="True" name="My Primary">
    <xpath expr="//head" position="inside">
        <link rel="stylesheet" href="/my_module/static/src/css/style.css"/>
    </xpath>
</template>

<!-- Inactive template (XPath won't apply) -->
<template id="optional_feature" inherit_id="website.layout" active="False">
    <xpath expr="//nav" position="replace">
        <nav class="custom-nav"/>
    </xpath>
</template>

<!-- Template with group restriction -->
<template id="admin_panel" groups="base.group_system">
    <div class="admin-panel">Admin only content</div>
</template>
```

**Attributes:**

| Attribute | Description |
|-----------|-------------|
| `id` | External identifier |
| `name` | View name |
| `inherit_id` | External ID of parent view to extend |
| `primary` | If `True` with `inherit_id`, creates a primary view |
| `groups` | Comma-separated group external IDs |
| `active` | `True`/`False` (only applied on creation, not updates) |
| `priority` | View priority (lower = higher priority) |

### 7.3 asset

Shortcut for creating `ir.asset` records:

```xml
<!-- Basic asset -->
<asset id="my_style_asset" name="My Style Asset">
    <bundle>web.assets_frontend</bundle>
    <path>my_module/static/src/css/style.scss</path>
</asset>

<!-- Inactive asset -->
<asset id="optional_style" name="Optional Style" active="False">
    <bundle>web.assets_frontend</bundle>
    <path>my_module/static/src/css/optional.scss</path>
</asset>

<!-- Asset with directive -->
<asset id="my_prepend_asset" name="Prepend Asset">
    <bundle directive="prepend">web.assets_backend</bundle>
    <path>my_module/static/src/css/priority.css</path>
</asset>

<!-- Asset with additional fields -->
<asset id="my_complex_asset" name="Complex Asset">
    <bundle>web.assets_backend</bundle>
    <path>my_module/static/src/js/widget.js</path>
    <field name="sequence" eval="5"/>
</asset>
```

**Attributes:**

| Attribute | Description |
|-----------|-------------|
| `id` | External identifier |
| `name` | Asset name (same as `ir.asset` name field) |
| `active` | Whether asset is active (only on creation) |

**Child elements:**

| Element | Description |
|---------|-------------|
| `<bundle>` | Target asset bundle name. Optional `directive` attribute |
| `<path>` | File path for the asset |
| `<field>` | Additional field values (like in `<record>`) |

---

## 8. CSV Data Files

### 8.1 Overview

CSV files provide a compact way to define many records of the same model.
The filename must be `model_name.csv` (with dots in model name).

### 8.2 Format

```csv
id,field1,field2:id,field3
external_id_1,value1,reference_external_id,value3
external_id_2,value2,reference_external_id,value4
```

- First row: field names. Special column `id` for external identifiers.
- Use `:id` suffix for relational fields referencing external IDs.
- Each subsequent row creates/updates one record.

### 8.3 Access Rights CSV (Most Common Use)

File: `security/ir.model.access.csv`

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model user,model_my_model,base.group_user,1,1,1,0
access_my_model_manager,my.model manager,model_my_model,base.group_system,1,1,1,1
```

### 8.4 Country States CSV Example

File: `data/res.country.state.csv`

```csv
id,country_id:id,name,code
state_us_al,base.us,Alabama,AL
state_us_ak,base.us,Alaska,AK
state_us_az,base.us,Arizona,AZ
state_us_ar,base.us,Arkansas,AR
```

**Columns explained:**
1. `id` -- External identifier for the state record
2. `country_id:id` -- External ID of the related country (Many2one ref)
3. `name` -- State name (Char field)
4. `code` -- State code (Char field)

### 8.5 CSV with Various Field Types

```csv
id,name,sequence,active,partner_id:id,tag_ids:id
record_1,First Record,10,1,base.partner_admin,"tag_a,tag_b"
record_2,Second Record,20,1,base.partner_demo,tag_c
record_3,Third Record,30,0,,
```

**Notes:**
- Boolean: `1` for True, `0` for False
- Empty field: leaves as default/False
- Many2many: comma-separated external IDs in quotes

---

## 9. Complete Data File Examples

### 9.1 Views Definition

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <!-- List View -->
    <record id="view_my_model_list" model="ir.ui.view">
        <field name="name">my.model.list</field>
        <field name="model">my.model</field>
        <field name="arch" type="xml">
            <list>
                <field name="name"/>
                <field name="state" widget="badge"
                       decoration-success="state == 'done'"
                       decoration-info="state == 'draft'"/>
                <field name="user_id" widget="many2one_avatar_user"/>
                <field name="date_deadline"/>
            </list>
        </field>
    </record>

    <!-- Form View -->
    <record id="view_my_model_form" model="ir.ui.view">
        <field name="name">my.model.form</field>
        <field name="model">my.model</field>
        <field name="arch" type="xml">
            <form>
                <header>
                    <button name="action_confirm" string="Confirm"
                            type="object" class="btn-primary"
                            invisible="state != 'draft'"/>
                    <field name="state" widget="statusbar"
                           statusbar_visible="draft,confirmed,done"/>
                </header>
                <sheet>
                    <group>
                        <group>
                            <field name="name"/>
                            <field name="partner_id"/>
                        </group>
                        <group>
                            <field name="date_deadline"/>
                            <field name="user_id"/>
                        </group>
                    </group>
                    <notebook>
                        <page string="Lines">
                            <field name="line_ids">
                                <list editable="bottom">
                                    <field name="product_id"/>
                                    <field name="quantity"/>
                                    <field name="price"/>
                                </list>
                            </field>
                        </page>
                        <page string="Notes">
                            <field name="notes"/>
                        </page>
                    </notebook>
                </sheet>
                <chatter/>
            </form>
        </field>
    </record>

    <!-- Search View -->
    <record id="view_my_model_search" model="ir.ui.view">
        <field name="name">my.model.search</field>
        <field name="model">my.model</field>
        <field name="arch" type="xml">
            <search>
                <field name="name"/>
                <field name="partner_id"/>
                <filter string="Draft" name="draft"
                        domain="[('state', '=', 'draft')]"/>
                <filter string="My Records" name="my_records"
                        domain="[('user_id', '=', uid)]"/>
                <separator/>
                <filter string="Late" name="late"
                        domain="[('date_deadline', '&lt;', context_today().strftime('%Y-%m-%d'))]"/>
                <group expand="0" string="Group By">
                    <filter string="State" name="group_state"
                            context="{'group_by': 'state'}"/>
                    <filter string="Partner" name="group_partner"
                            context="{'group_by': 'partner_id'}"/>
                </group>
            </search>
        </field>
    </record>
</odoo>
```

### 9.2 Actions and Menus

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <!-- Window Action -->
    <record id="action_my_model" model="ir.actions.act_window">
        <field name="name">My Models</field>
        <field name="res_model">my.model</field>
        <field name="view_mode">list,form,kanban</field>
        <field name="search_view_id" ref="view_my_model_search"/>
        <field name="context">{'search_default_my_records': 1}</field>
        <field name="help" type="html">
            <p class="o_view_nocontent_smiling_face">
                Create your first record!
            </p>
        </field>
    </record>

    <!-- Menu Items -->
    <menuitem id="menu_my_module_root"
              name="My Module"
              sequence="10"/>

    <menuitem id="menu_my_model"
              name="My Models"
              parent="menu_my_module_root"
              action="action_my_model"
              sequence="10"/>
</odoo>
```

### 9.3 Seed/Demo Data

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <data noupdate="1">
        <!-- Sequence -->
        <record id="seq_my_model" model="ir.sequence">
            <field name="name">My Model Sequence</field>
            <field name="code">my.model</field>
            <field name="prefix">MM/%(year)s/</field>
            <field name="padding">5</field>
        </record>

        <!-- Email Template -->
        <record id="email_template_my_model" model="mail.template">
            <field name="name">My Model: Notification</field>
            <field name="model_id" ref="model_my_model"/>
            <field name="subject">{{ object.name }} - Notification</field>
            <field name="body_html" type="html">
                <p>Dear {{ object.partner_id.name }},</p>
                <p>Record <strong>{{ object.name }}</strong> has been updated.</p>
            </field>
            <field name="email_from">{{ (object.company_id.email or user.email) }}</field>
            <field name="email_to">{{ object.partner_id.email }}</field>
        </record>

        <!-- Default records -->
        <record id="default_tag_urgent" model="my.model.tag">
            <field name="name">Urgent</field>
            <field name="color">1</field>
        </record>

        <record id="default_tag_important" model="my.model.tag">
            <field name="name">Important</field>
            <field name="color">4</field>
        </record>
    </data>
</odoo>
```

### 9.4 View Inheritance

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <!-- Extend an existing form view -->
    <record id="view_partner_form_inherit" model="ir.ui.view">
        <field name="name">res.partner.form.inherit.my_module</field>
        <field name="model">res.partner</field>
        <field name="inherit_id" ref="base.view_partner_form"/>
        <field name="arch" type="xml">
            <!-- Add field after existing field -->
            <field name="website" position="after">
                <field name="my_custom_field"/>
            </field>

            <!-- Add a page to notebook -->
            <xpath expr="//notebook" position="inside">
                <page string="My Custom Tab">
                    <group>
                        <field name="custom_field_1"/>
                        <field name="custom_field_2"/>
                    </group>
                </page>
            </xpath>

            <!-- Replace an element -->
            <field name="phone" position="replace">
                <field name="phone" widget="phone"/>
            </field>

            <!-- Add attributes -->
            <field name="email" position="attributes">
                <attribute name="required">1</attribute>
            </field>

            <!-- Hide element -->
            <field name="fax" position="attributes">
                <attribute name="invisible">1</attribute>
            </field>
        </field>
    </record>
</odoo>
```

---

## 10. Asset Bundles in __manifest__.py

While the `<asset>` XML shortcut exists, assets are more commonly defined in
the manifest:

```python
{
    'name': 'My Module',
    'assets': {
        # Backend assets
        'web.assets_backend': [
            'my_module/static/src/**/*.js',
            'my_module/static/src/**/*.xml',
            'my_module/static/src/**/*.scss',
        ],
        # Frontend assets
        'web.assets_frontend': [
            'my_module/static/src/frontend/**/*',
        ],
        # Unit test assets
        'web.assets_unit_tests': [
            'my_module/static/tests/**/*',
        ],
        # Tour test assets
        'web.assets_tests': [
            'my_module/static/tests/tours/**/*.js',
        ],
        # Prepend (higher priority)
        'web.assets_backend': [
            ('prepend', 'my_module/static/src/priority.css'),
        ],
        # Replace
        'web.assets_backend': [
            ('replace', 'other_module/static/src/old.js', 'my_module/static/src/new.js'),
        ],
        # Remove
        'web.assets_backend': [
            ('remove', 'other_module/static/src/unwanted.js'),
        ],
    },
}
```

---

## 11. Common Patterns

### 11.1 Record with Conditional Creation

```xml
<!-- Only create if record doesn't exist (useful for updates) -->
<record id="my_record" model="my.model" forcecreate="False">
    <field name="name">Default Name</field>
</record>
```

### 11.2 Record with Context

```xml
<record id="my_record" model="my.model" context="{'default_type': 'special'}">
    <field name="name">Special Record</field>
</record>
```

### 11.3 Updating Existing Records from Other Modules

```xml
<!-- Add a field value to an existing record -->
<record id="base.partner_admin" model="res.partner">
    <field name="my_custom_field">Custom Value</field>
</record>

<!-- Add groups to existing menu -->
<record id="sale.menu_sale_order" model="ir.ui.menu">
    <field name="groups_id" eval="[(4, ref('my_module.group_custom'))]"/>
</record>
```

### 11.4 Sequence Definition

```xml
<record id="seq_order" model="ir.sequence">
    <field name="name">Order Sequence</field>
    <field name="code">my.order</field>
    <field name="prefix">ORD/%(year)s/</field>
    <field name="padding">5</field>
    <field name="number_increment">1</field>
    <field name="number_next">1</field>
</record>
```

### 11.5 Cron Job Definition

```xml
<record id="cron_cleanup" model="ir.cron">
    <field name="name">My Module: Cleanup Old Records</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="interval_number">1</field>
    <field name="interval_type">days</field>
    <field name="numbercall">-1</field>
    <field name="code">model._cron_cleanup()</field>
</record>
```

---

## 12. File Loading Order and Best Practices

### 12.1 Recommended __manifest__.py data Order

```python
'data': [
    # 1. Security groups first (referenced by access rights and rules)
    'security/security.xml',
    # 2. Access rights (reference groups and models)
    'security/ir.model.access.csv',
    # 3. Data (sequences, defaults, templates)
    'data/data.xml',
    # 4. Views (reference actions)
    'views/my_model_views.xml',
    # 5. Reports
    'report/my_report.xml',
    # 6. Wizards
    'wizard/my_wizard_views.xml',
],
'demo': [
    'demo/demo_data.xml',
],
```

### 12.2 Best Practices

1. Always provide external IDs on records
2. Use `noupdate="1"` for data users may customize
3. Keep views (without noupdate) and data (with noupdate) in separate files
4. Use CSV for bulk simple data (access rights, country states)
5. Use XML for complex records (views, actions, templates)
6. Reference order matters: define dependencies before dependents
7. Use meaningful external ID names: `view_model_form`, `action_model`, `menu_model_root`
