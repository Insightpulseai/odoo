---
name: Odoo Views and Actions
description: Use when editing XML views, menus, actions, scheduled actions, or UI definitions in Odoo 18 CE.
---

# Odoo Views and Actions

## When to use

- Creating or modifying form/list/kanban/search views
- Adding menus and menu items
- Defining window actions, server actions, or URL actions
- Setting up scheduled actions (`ir.cron`)
- Fixing view inheritance or xpath issues

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
| QWeb | `<t t-name="...">` | Template rendering |

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

### xpath position values

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

## Do not

- Use view types not available in CE 18
- Replace entire upstream views when xpath can target specific elements
- Create menus pointing to non-existent actions
- Use `eval="..."` for simple string/integer values
- Reference fields not declared in the model's dependency chain
