# odoo-view-customization

Safely extends Odoo UI through inherited views, actions, and menus using xpath expressions.

## When to use
- New fields must appear in existing form, list, or kanban views
- UI layout changes are required on existing views
- New menu items or window actions are needed
- A PR modifies `views/` XML files

## Key rule
Always use inherited views with xpath expressions. Never replace core views or directly edit
OCA/core XML files. Follow Odoo 19 XML ID conventions and use `list` (not `tree`) in user-facing strings.

## Cross-references
- `agents/knowledge/benchmarks/odoo-developer-howtos.md`
- `agents/knowledge/benchmarks/odoo-coding-guidelines.md`
- `~/.claude/rules/odoo19-coding.md`
