# odoo-module-dependency-management

Validates and manages Odoo module dependency graphs across ipai_*, OCA, and upstream CE addons.

## When to use
- New module added to addons manifest
- Dependency change in any __manifest__.py
- OCA submodule updated
- Module install/upgrade failure debugging
- Periodic dependency audit

## Key rule
Config -> OCA -> Delta (ipai_*). Never introduce Enterprise dependencies. Never modify OCA source. Full transitive dependency chain must resolve cleanly.

## Cross-references
- `agents/knowledge/benchmarks/odoo-sh-persona-model.md`
- `agents/personas/odoo-developer.md`
- `.claude/rules/oca-governance.md`
- `config/addons.manifest.yaml`
