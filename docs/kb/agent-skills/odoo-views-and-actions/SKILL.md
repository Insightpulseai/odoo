---
name: odoo_views_and_actions
description: Define Odoo 18 views, actions, and menus
category: backend
priority: high
version: "1.0"
---

# Views and Actions

## View Types

| Type | Tag | Notes |
|------|-----|-------|
| Form | `<form>` | Detail/edit view for single record |
| List | `<list>` | Tabular view. **Odoo 18 uses `list`, NOT `tree`** |
| Kanban | `<kanban>` | Card-based view |
| Search | `<search>` | Filter/group/search panel |
| Pivot | `<pivot>` | Pivot table analysis |
| Graph | `<graph>` | Chart visualization |
| Calendar | `<calendar>` | Date-based view |
| Gantt | `<gantt>` | Timeline view (EE in some versions, CE in 19) |

**Critical**: Odoo 18 renamed `tree` to `list`. Always use `<list>` in view definitions and `list` in `view_mode`.

## XML ID Naming Convention

| Element | Pattern | Example |
|---------|---------|---------|
| Form view | `<model>_view_form` | `ipai_example_model_view_form` |
| List view | `<model>_view_list` | `ipai_example_model_view_list` |
| Kanban view | `<model>_view_kanban` | `ipai_example_model_view_kanban` |
| Search view | `<model>_view_search` | `ipai_example_model_view_search` |
| Action | `<model>_action` | `ipai_example_model_action` |
| Root menu | `<module>_menu_root` | `ipai_example_menu_root` |
| Sub menu | `<model>_menu` | `ipai_example_model_menu` |

Use underscores in XML IDs, matching the model's dotted name with dots replaced by underscores.

## Form View Pattern

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="ipai_example_model_view_form" model="ir.ui.view">
        <field name="name">ipai.example.model.form</field>
        <field name="model">ipai.example.model</field>
        <field name="arch" type="xml">
            <form string="Example">
                <header>
                    <button name="action_confirm"
                            type="object"
                            string="Confirm"
                            class="btn-primary"
                            invisible="state != 'draft'"/>
                    <button name="action_done"
                            type="object"
                            string="Done"
                            invisible="state != 'confirmed'"/>
                    <button name="action_cancel"
                            type="object"
                            string="Cancel"
                            invisible="state in ('done', 'cancelled')"/>
                    <button name="action_draft"
                            type="object"
                            string="Reset to Draft"
                            invisible="state != 'cancelled'"/>
                    <field name="state"
                           widget="statusbar"
                           statusbar_visible="draft,confirmed,done"/>
                </header>
                <sheet>
                    <div class="oe_button_box" name="button_box">
                        <button name="action_view_lines"
                                type="object"
                                class="oe_stat_button"
                                icon="fa-list">
                            <field name="line_count"
                                   widget="statinfo"
                                   string="Lines"/>
                        </button>
                    </div>
                    <widget name="web_ribbon"
                            title="Archived"
                            bg_color="text-bg-danger"
                            invisible="active"/>
                    <div class="oe_title">
                        <label for="name"/>
                        <h1>
                            <field name="name"
                                   placeholder="e.g. Example Record"/>
                        </h1>
                    </div>
                    <group>
                        <group>
                            <field name="company_id"
                                   groups="base.group_multi_company"/>
                            <field name="currency_id" invisible="1"/>
                        </group>
                        <group>
                            <field name="total_amount"/>
                            <field name="tag_ids" widget="many2many_tags"/>
                        </group>
                    </group>
                    <notebook>
                        <page string="Lines" name="lines">
                            <field name="line_ids">
                                <list editable="bottom">
                                    <field name="sequence"
                                           widget="handle"/>
                                    <field name="name"/>
                                    <field name="amount"/>
                                </list>
                            </field>
                        </page>
                        <page string="Notes" name="notes">
                            <field name="notes"
                                   placeholder="Internal notes..."/>
                        </page>
                    </notebook>
                </sheet>
                <chatter/>
            </form>
        </field>
    </record>
</odoo>
```

### Form View Rules

- Always wrap content in `<sheet>` (except `<header>` and `<chatter>`)
- Use `<group>` to create columns (two `<group>` inside a `<group>` = two-column layout)
- Use `<notebook>/<page>` for tabbed sections
- Add `name` attribute to `<page>` and `<group>` for inheritance targets
- Place `<chatter/>` after `</sheet>` for mail thread integration
- **Odoo 18**: Use `invisible="expression"` directly, NOT `attrs="{'invisible': [...]}"` (attrs is deprecated)

## List View Pattern

```xml
<record id="ipai_example_model_view_list" model="ir.ui.view">
    <field name="name">ipai.example.model.list</field>
    <field name="model">ipai.example.model</field>
    <field name="arch" type="xml">
        <list string="Examples"
              decoration-danger="state == 'cancelled'"
              decoration-success="state == 'done'"
              decoration-info="state == 'draft'"
              default_order="sequence, name">
            <field name="sequence" widget="handle"/>
            <field name="name"/>
            <field name="company_id"
                   groups="base.group_multi_company"
                   optional="show"/>
            <field name="total_amount" sum="Total"/>
            <field name="tag_ids" widget="many2many_tags"
                   optional="hide"/>
            <field name="state"
                   widget="badge"
                   decoration-success="state == 'done'"
                   decoration-info="state == 'draft'"
                   decoration-danger="state == 'cancelled'"/>
        </list>
    </field>
</record>
```

### List View Options

| Attribute | Values | Purpose |
|-----------|--------|---------|
| `optional` | `show`, `hide` | Column visibility toggle (default shown or hidden) |
| `decoration-*` | `danger`, `success`, `info`, `warning`, `muted`, `bf`, `it` | Row/cell styling |
| `editable` | `top`, `bottom` | Inline editing position |
| `default_order` | field list | Default sort order |
| `sum`, `avg` | label string | Column aggregation in footer |

## Kanban View Pattern

```xml
<record id="ipai_example_model_view_kanban" model="ir.ui.view">
    <field name="name">ipai.example.model.kanban</field>
    <field name="model">ipai.example.model</field>
    <field name="arch" type="xml">
        <kanban default_group_by="state"
                class="o_kanban_small_column"
                quick_create="false">
            <progressbar field="state"
                         colors='{"draft": "info", "confirmed": "warning", "done": "success", "cancelled": "danger"}'/>
            <templates>
                <t t-name="card">
                    <field name="name" class="fw-bold fs-4"/>
                    <field name="tag_ids" widget="many2many_tags"
                           options="{'color_field': 'color'}"/>
                    <div class="row">
                        <div class="col-6">
                            <field name="total_amount"
                                   widget="monetary"/>
                        </div>
                        <div class="col-6 text-end">
                            <field name="company_id"
                                   groups="base.group_multi_company"/>
                        </div>
                    </div>
                </t>
            </templates>
        </kanban>
    </field>
</record>
```

### Kanban Rules (Odoo 18)

- Use `<t t-name="card">` template (Odoo 18 simplified kanban)
- `default_group_by` sets the initial grouping column
- `quick_create="false"` disables inline record creation in columns
- Access field values directly with `<field>` tags inside the template

## Search View Pattern

```xml
<record id="ipai_example_model_view_search" model="ir.ui.view">
    <field name="name">ipai.example.model.search</field>
    <field name="model">ipai.example.model</field>
    <field name="arch" type="xml">
        <search string="Search Examples">
            <!-- Search fields -->
            <field name="name"
                   filter_domain="['|', ('name', 'ilike', self), ('tag_ids.name', 'ilike', self)]"/>
            <field name="company_id"/>

            <!-- Quick filters -->
            <separator/>
            <filter name="filter_draft"
                    string="Draft"
                    domain="[('state', '=', 'draft')]"/>
            <filter name="filter_confirmed"
                    string="Confirmed"
                    domain="[('state', '=', 'confirmed')]"/>
            <filter name="filter_done"
                    string="Done"
                    domain="[('state', '=', 'done')]"/>
            <separator/>
            <filter name="filter_archived"
                    string="Archived"
                    domain="[('active', '=', False)]"/>

            <!-- Group by -->
            <group expand="0" string="Group By">
                <filter name="groupby_state"
                        string="Status"
                        context="{'group_by': 'state'}"/>
                <filter name="groupby_company"
                        string="Company"
                        context="{'group_by': 'company_id'}"/>
            </group>

            <!-- Search panel (left sidebar) -->
            <searchpanel>
                <field name="state" icon="fa-tasks"
                       select="one" enable_counters="1"/>
                <field name="tag_ids" icon="fa-tags"
                       select="multi" enable_counters="1"/>
            </searchpanel>
        </search>
    </field>
</record>
```

### Search View Rules

- `filter_domain` on `<field>` customizes the search operator
- `self` in `filter_domain` = the user's search input
- Filters with `name` attribute can be activated via action `context`: `{'search_default_filter_draft': 1}`
- `<searchpanel>` adds a persistent left sidebar for faceted filtering
- `select="one"` = radio buttons, `select="multi"` = checkboxes

## Action Window

```xml
<record id="ipai_example_model_action" model="ir.actions.act_window">
    <field name="name">Examples</field>
    <field name="res_model">ipai.example.model</field>
    <field name="view_mode">list,form,kanban</field>
    <field name="domain">[('active', '=', True)]</field>
    <field name="context">{
        'search_default_filter_draft': 1,
        'default_company_id': allowed_company_ids[0],
    }</field>
    <field name="help" type="html">
        <p class="o_view_nocontent_smiling_face">
            Create your first example record
        </p>
        <p>
            Track and manage example records from here.
        </p>
    </field>
</record>
```

### Binding Specific Views to an Action

```xml
<record id="ipai_example_model_action_view_list" model="ir.actions.act_window.view">
    <field name="sequence" eval="1"/>
    <field name="view_mode">list</field>
    <field name="view_id" ref="ipai_example_model_view_list"/>
    <field name="act_window_id" ref="ipai_example_model_action"/>
</record>

<record id="ipai_example_model_action_view_form" model="ir.actions.act_window.view">
    <field name="sequence" eval="2"/>
    <field name="view_mode">form</field>
    <field name="view_id" ref="ipai_example_model_view_form"/>
    <field name="act_window_id" ref="ipai_example_model_action"/>
</record>
```

### Context Keys

| Key | Purpose |
|-----|---------|
| `search_default_<filter_name>` | Activate a search filter on load |
| `default_<field>` | Set default value for new records |
| `create` | `False` to hide Create button |
| `edit` | `False` to open in read-only |
| `group_by` | Default grouping |

## Menu Hierarchy

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Root menu (top-level app) -->
    <menuitem id="ipai_example_menu_root"
              name="Examples"
              web_icon="ipai_example/static/description/icon.png"
              sequence="100"/>

    <!-- Category menu -->
    <menuitem id="ipai_example_menu_main"
              name="Examples"
              parent="ipai_example_menu_root"
              sequence="10"/>

    <!-- Action menu item -->
    <menuitem id="ipai_example_model_menu"
              name="All Examples"
              parent="ipai_example_menu_main"
              action="ipai_example_model_action"
              sequence="10"/>

    <!-- Configuration submenu -->
    <menuitem id="ipai_example_menu_config"
              name="Configuration"
              parent="ipai_example_menu_root"
              groups="base.group_system"
              sequence="90"/>

    <menuitem id="ipai_example_tag_menu"
              name="Tags"
              parent="ipai_example_menu_config"
              action="ipai_example_tag_action"
              sequence="10"/>
</odoo>
```

### Menu Rules

- Root menu = top-level app entry (visible in app switcher)
- `web_icon` = path to 128x128 PNG icon for app switcher
- Use `groups` to restrict menu visibility
- `sequence` controls ordering (lower = earlier)
- Three levels typical: Root > Category > Action item

## View Inheritance

Use `inherit_id` to extend existing views from other modules.

```xml
<record id="res_partner_view_form_inherit_ipai_example"
        model="ir.ui.view">
    <field name="name">res.partner.form.inherit.ipai_example</field>
    <field name="model">res.partner</field>
    <field name="inherit_id" ref="base.view_partner_form"/>
    <field name="arch" type="xml">

        <!-- Add field after an existing field -->
        <xpath expr="//field[@name='phone']" position="after">
            <field name="x_example_ref"/>
        </xpath>

        <!-- Add a new page to notebook -->
        <xpath expr="//notebook" position="inside">
            <page string="Examples" name="examples">
                <field name="example_ids"/>
            </page>
        </xpath>

        <!-- Replace a field -->
        <xpath expr="//field[@name='website']" position="replace">
            <field name="website" widget="url"
                   placeholder="https://..."/>
        </xpath>

        <!-- Modify attributes of existing element -->
        <xpath expr="//field[@name='email']" position="attributes">
            <attribute name="required">1</attribute>
        </xpath>

        <!-- Add content before an element -->
        <xpath expr="//group[@name='sale']" position="before">
            <group string="Custom Section" name="custom">
                <field name="x_custom_field"/>
            </group>
        </xpath>

    </field>
</record>
```

### Inheritance Naming Convention

Pattern: `<original_view_name>.inherit.<your_module>`

Example: If inheriting `base.view_partner_form`, the view name should be `res.partner.form.inherit.ipai_example`.

### XPath Position Values

| Position | Effect |
|----------|--------|
| `inside` | Append as last child of matched element |
| `before` | Insert before matched element |
| `after` | Insert after matched element |
| `replace` | Replace matched element entirely |
| `attributes` | Modify attributes of matched element |

### Shorthand (when target field name is unique)

```xml
<!-- These are equivalent when field name is unique in the view -->
<xpath expr="//field[@name='phone']" position="after">
    <field name="mobile"/>
</xpath>

<field name="phone" position="after">
    <field name="mobile"/>
</field>
```

Use the shorthand only when the field appears exactly once in the parent view. Use full xpath for ambiguous targets.
