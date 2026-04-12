---
paths:
  - "odoo/custom/**/*.xml"
  - "odoo/OCA/**/*.xml"
---

# Odoo XML view rules — Odoo 18 CE

## View tag rules (Odoo 18 CE breaking changes)
- ALWAYS use `<list>` — NEVER `<tree>`
- ALWAYS use `view_mode="list,form"` — NEVER `view_mode="tree,form"`
- ALWAYS use `type="list"` in `ir.actions.act_window` — NEVER `type="tree"`

## Inheritance
- Always use `inherit_id` for modifications — never create duplicate base views
- XPath: prefer `//field[@name='x']` over positional selectors
- Position values: `before`, `after`, `inside`, `replace`, `attributes`
- Add `priority` attribute only when needed to override OCA views

## Form views
- Group fields logically in `<group>` elements with `string=` labels
- Use `<notebook>` for secondary information — keep the main form clean
- Buttons: use `class="btn-primary"` for the main action, `btn-secondary` for secondary
- Required fields: mark with `required="1"` on the view, not just the model

## List views
- Always specify the fields to display — don't rely on defaults
- Use `decoration-danger`, `decoration-warning`, `decoration-success` for status colors
- Add `optional="show"` or `optional="hide"` for non-critical columns
- Enable `multi_edit="1"` for bulk-editable lists where appropriate

## Search views
- Include `<search>` view for every model with a list view
- Add `<filter>` for common status values and date ranges
- Add `<group>` elements for grouping by common fields
- Add `<searchpanel>` for models where faceted filtering is valuable

## Security XML
- Every menu item needs a `groups` attribute or an explicit `ir.rule`
- Never use `base.group_user` as the only access group for finance models
- Finance menus: restrict to `pulser_finance_*` groups minimum
