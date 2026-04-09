# odoo-extendability-check

Verify code follows the "think extendable" principle — small methods, no hardcoded blocking
logic, proper _inherit usage, configurable parameters, and proper hook points.

## When to use
- New module code (models, wizards, controllers)
- Inherited model changes
- Business logic review
- Post-generation quality gate for implementation skill outputs

## Key rule
Odoo modules must be designed for extension. Methods stay small (under 30 lines) so
submodules can `super()` on them. Business logic is not hardcoded in ways that prevent
override. `_inherit` is used for model extension, never copy-paste. Hook points are
provided as small, overridable methods.

## Cross-references
- `agents/knowledge/benchmarks/odoo-coding-guidelines.md`
- `agents/knowledge/benchmarks/odoo-developer-howtos.md`
- `~/.claude/rules/odoo18-coding.md`
