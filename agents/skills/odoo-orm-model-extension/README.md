# odoo-orm-model-extension

Extends Odoo models with fields, computed fields, constraints, and business logic using `_inherit`.

## When to use
- A new field is needed on an existing Odoo model
- Computed fields or business logic must be added
- Model behavior needs customization through override
- A PR modifies files in a `models/` directory

## Key rule
All model extensions must use `_inherit` in a custom `ipai_*` module. Never modify OCA or core source.
Follow Odoo 19 class attribute order, field naming conventions, and use Command tuples for x2many writes.

## Cross-references
- `agents/knowledge/benchmarks/odoo-developer-howtos.md`
- `agents/knowledge/benchmarks/odoo-coding-guidelines.md`
- `~/.claude/rules/odoo19-coding.md`
