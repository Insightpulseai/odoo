# odoo-openupgrade-assessment

Assess upgrade readiness using OpenUpgrade as the benchmark path — coverage analysis, migration script inventory, breaking change identification.

## When to use
- New Odoo version is released
- Upgrade planning phase begins
- Pre-migration review is requested

## Key rule
OpenUpgrade coverage is never assumed complete. Every module must be individually verified
for migration script availability. Custom ipai_* modules always require manual migration
assessment. Rehearsal on a disposable database is mandatory before any production upgrade.

## Cross-references
- `agents/knowledge/benchmarks/oca-community-governance.md`
- `agent-platform/ssot/learning/oca_skill_persona_map.yaml`
