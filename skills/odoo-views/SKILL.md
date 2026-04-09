# Odoo XML views and actions skill

Use this skill when changing:
- form, list, kanban, calendar, pivot, graph views
- search views and filters
- actions (window, server, URL, report)
- menus and menu items
- inherited XML (xpath expressions)
- QWeb templates

## Checklist

1. Prefer inheritance (`xpath`) over copy-paste replacement.
2. Keep changes minimal and upgrade-safe.
3. Preserve existing security and menu visibility.
4. Avoid brittle selectors — use `name` attribute or `position` attributes that tolerate upstream changes.
5. Validate the view change against the target addon and model.
6. Update tests or smoke checks if the change is behaviorally significant.
7. Follow XML ID conventions: `<model>_view_form`, `<model>_view_tree`, `<model>_action`, `<model>_menu`.

## Pay Special Attention To

- Inherited view chains — check `inherit_id` targets exist in dependencies
- Action/view mode consistency (e.g. `tree,form` not `tree,form,kanban` unless kanban view exists)
- Field existence and security access in the target model
- `groups` attributes on menu items and view elements
- Odoo 18: `tree` renamed to `list` globally — use `list` in new code

## Refuse or Escalate If

- The request requires modifying an OCA view directly (use `ipai_*` override module instead)
- The view adds UI for heavy logic that belongs outside Odoo
- The xpath target relies on `position="replace"` for a large block (fragile across upgrades)
