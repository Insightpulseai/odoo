---
name: Odoo Views and Actions
description: Edit XML views, menus, actions, scheduled actions, or UI definitions in Odoo 18 CE. Use when creating or modifying UI elements.
---

# Odoo Views and Actions

## Purpose

Write correct Odoo 18 CE view XML, menu definitions, window actions, and scheduled actions.

## When to use

- Creating or modifying form/list/kanban/search views
- Adding menus and menu items
- Defining window actions, server actions, or URL actions
- Setting up scheduled actions (`ir.cron`)
- Fixing view inheritance or xpath issues

## Inputs or assumptions

- Odoo 18 CE view types only (no dashboard, cohort, map, gantt)
- `<list>` preferred over `<tree>` (both work)
- Direct XML attributes for `invisible`/`readonly`/`required` (no `attrs` dict)

## Source priority

1. Local view XML in `addons/`
2. Odoo 18 CE view documentation
3. OCA view patterns

## Workflow

1. Identify the parent view for inheritance
2. Use `xpath` with specific selectors (field name, group name)
3. Test view loads: install module on disposable DB
4. Verify menu → action → view chain is complete

## View types (CE 18)

| Type | Tag | Use case |
|------|-----|----------|
| Form | `<form>` | Record detail/edit |
| List | `<list>` | Multi-record table |
| Kanban | `<kanban>` | Card-based board |
| Search | `<search>` | Filter/group definitions |
| Calendar | `<calendar>` | Date-based view |
| Pivot | `<pivot>` | Pivot table analysis |
| Graph | `<graph>` | Charts |
| Activity | `<activity>` | Activity timeline |

**Not in CE**: dashboard, cohort, map, gantt (Enterprise-only).

## View inheritance

```xml
<record id="view_partner_form_inherit" model="ir.ui.view">
    <field name="name">res.partner.form.inherit.ipai</field>
    <field name="model">res.partner</field>
    <field name="inherit_id" ref="base.view_partner_form"/>
    <field name="arch" type="xml">
        <xpath expr="//field[@name='phone']" position="after">
            <field name="my_custom_field"/>
        </xpath>
    </field>
</record>
```

### xpath positions

| Position | Effect |
|----------|--------|
| `inside` | Append children inside matched element |
| `after` | Insert after matched element |
| `before` | Insert before matched element |
| `replace` | Replace matched element entirely |
| `attributes` | Modify attributes of matched element |

### xpath best practices

- Prefer `//field[@name='fieldname']` over positional selectors
- Use `//group[@name='groupname']` for named groups
- Test that the parent view and target element exist
- Avoid `position="replace"` on large subtrees (breaks upgrades)

## Window actions

```xml
<record id="action_my_model" model="ir.actions.act_window">
    <field name="name">My Records</field>
    <field name="res_model">ipai.my.model</field>
    <field name="view_mode">list,form,kanban</field>
    <field name="domain">[('active', '=', True)]</field>
    <field name="context">{'default_state': 'draft'}</field>
</record>
```

## Menus

```xml
<!-- Top-level app menu (shows in app grid) -->
<menuitem id="menu_my_app_root"
          name="My App"
          web_icon="ipai_my_module,static/description/icon.png"
          sequence="50"/>

<!-- Submenu -->
<menuitem id="menu_my_records"
          name="Records"
          parent="menu_my_app_root"
          action="action_my_model"
          sequence="10"/>
```

## Scheduled actions

```xml
<record id="ir_cron_my_task" model="ir.cron">
    <field name="name">My Scheduled Task</field>
    <field name="model_id" ref="model_ipai_my_model"/>
    <field name="state">code</field>
    <field name="code">model._cron_my_task()</field>
    <field name="interval_number">1</field>
    <field name="interval_type">days</field>
    <field name="active" eval="False"/>
    <field name="numbercall">-1</field>
</record>
```

Set `active=False` by default; activate via configuration.

## Output format

Well-formed XML records with proper `id`, `model`, and `arch` fields.

## Verification

- Module installs without view errors
- Menus appear in expected locations
- Actions open correct views
- Inherited views render without xpath errors

## Anti-patterns

- Using view types not available in CE 18
- Replacing entire upstream views when xpath can target specific elements
- Creating menus pointing to non-existent actions
- Using `eval="..."` for simple string/integer values
- Using `attrs` dict syntax (removed in 18) instead of direct attributes
- Referencing fields not declared in the model's dependency chain
