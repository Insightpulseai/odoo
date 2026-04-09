# odoo-upgrade-safe-extension

Ensures all module changes use inheritance-based patterns and are safe across Odoo version upgrades.

## When to use
- Module review or audit for upgrade safety
- A PR modifies models, views, or data files
- Version upgrade planning (e.g. 17.0 to 18.0)
- A new module is added to the install baseline

## Key rule
All extensions must use `_inherit` for models and inherited views with xpath for UI. No core
or OCA files may be modified. Schema changes require migration scripts. Odoo 18 breaking changes
(groups_id to group_ids, tree to list) must be handled.

## Cross-references
- `agents/knowledge/benchmarks/odoo-developer-howtos.md`
- `agents/knowledge/benchmarks/odoo-coding-guidelines.md`
- `~/.claude/rules/odoo18-coding.md`
- `~/.claude/rules/oca-governance.md`
