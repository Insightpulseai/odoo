---
applyTo: "addons/**/*.xml"
---

You are editing Odoo 18 CE XML data and views.

## View inheritance

- Prefer `<xpath expr="..." position="inside|after|before|replace|attributes">` over full view replacement
- Use `inherit_id` referencing the original view's XML ID
- Keep xpath expressions stable: prefer `name=` attributes over positional selectors
- Test that the parent view exists before inheriting

## XML IDs

- Format: `<module>.<type>_<model>_<purpose>` (e.g., `ipai_finance_ppm.view_project_form`)
- Never reuse or shadow CE/OCA XML IDs
- Prefix all IDs with the module's technical name

## Menus and actions

- Root menus need `web_icon="<module>,static/description/icon.png"`
- Use `ir.actions.act_window` for model actions, not server actions for simple opens
- `ir.cron` records: set `active=False` by default in data files; activate via config

## View types (CE 18 only)

Supported: `form`, `list`, `kanban`, `search`, `calendar`, `pivot`, `graph`, `activity`, `qweb`
Not available in CE: `dashboard`, `cohort`, `map`, `gantt` (Enterprise-only)

## Data files

- Use `noupdate="1"` for records that users may customize (settings, defaults)
- Use `noupdate="0"` (default) for structural data (views, menus, ACLs)
- Demo data goes in `demo/` directory, referenced in manifest `demo` key
- Never put credentials or secrets in XML data files

## Do not

- Use `<attribute name="invisible">1</attribute>` to hide fields globally (use groups)
- Create views for models that don't exist in your module's dependencies
- Reference fields that haven't been declared in the model
- Use `eval="..."` for simple values (use direct value instead)
