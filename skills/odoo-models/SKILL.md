# Odoo model and business logic skill

Use this skill when changing:
- models
- fields
- compute methods
- onchange methods
- constraints
- business methods
- manifests tied to model logic
- security (ir.model.access.csv, record rules)

## Checklist

1. Identify whether the change belongs in CE core, OCA, config/data, external bridge, or thin custom addon.
2. Confirm the addon boundary is single-purpose.
3. Minimize schema changes — add fields, don't restructure tables.
4. Follow Odoo 18 model class attribute order: private attrs → defaults → fields → SQL constraints → compute → selection → constrains/onchange → CRUD → actions → business methods.
5. Use `Command` tuples for x2many writes (`Command.create()`, `Command.link()`, `Command.set()`).
6. Use `_(...)` lazy translation with positional args — never f-strings or `.format()` inside `_()`.
7. Keep methods small and testable.
8. Add or update tests for changed logic.
9. Note upgrade risks and dependency impacts.

## Naming Conventions

- Many2one: `*_id` (e.g. `partner_id`)
- x2many: `*_ids` (e.g. `line_ids`, `tag_ids`)
- Compute: `_compute_<field>`
- Onchange: `_onchange_<field>`
- Constraint: `_check_<field>`
- Action: `action_<verb>` (e.g. `action_confirm`)
- Boolean: `is_*` or `has_*`

## Refuse or Escalate If

- The request recreates an Enterprise feature as a fat custom addon
- The change should live in an external bridge instead
- An OCA module already covers the need
- The method would exceed 50 lines — decompose first
- `cr.commit()` or context mutation is proposed
