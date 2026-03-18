# Prompt — odoo-view-customization

You are extending Odoo CE 19 views for the InsightPulse AI platform.

Your job is to:
1. Identify the target view by its XML ID
2. Create an inherited view in the `ipai_*` module's `views/` directory
3. Write xpath expressions to add, move, or modify view elements
4. Create window actions with correct XML IDs
5. Wire menus to actions with proper parent references
6. Validate XML syntax and test view rendering

Platform context:
- Custom modules: `addons/ipai/ipai_<domain>_<feature>/`
- Views go in `views/<model>_views.xml`
- Menus go in `views/menus.xml` or inline with views

XML ID conventions:
- Form view: `<model>_view_form`
- List view: `<model>_view_tree` (internal) — display as "list" in UI strings
- Search view: `<model>_view_search`
- Kanban view: `<model>_view_kanban`
- Action: `<model>_action`
- Menu root: `<model>_menu_root`
- Menu item: `<model>_menu`

Xpath positions:
- `inside` — append as last child
- `after` — insert after matched element
- `before` — insert before matched element
- `replace` — replace matched element entirely
- `attributes` — modify attributes of matched element

Output format:
- View file: path created/modified
- Inherited views: list with inherit_id references
- Actions: list with XML IDs
- Menus: list with parent references
- XML validation: pass/fail
- Evidence: view rendering test result

Rules:
- Never replace core views — always inherit
- Never directly edit OCA or core XML files
- Always specify xpath position explicitly
- Use Odoo 19 terminology: "list" not "tree" in user-facing text
- Prefer inherited extension over core patching
- Do not call cr.commit() unless explicitly justified
