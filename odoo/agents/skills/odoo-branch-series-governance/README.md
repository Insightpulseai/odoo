# odoo-branch-series-governance

Validate branch and series readiness for new Odoo versions — branch creation, CI tooling updates, migration issue tracking.

## When to use
- New Odoo version is released
- Series migration planning begins
- Branch creation for new version

## Key rule
Never create a series branch without CI tooling support. Follow OCA branch naming
conventions (e.g. `19.0`). Migration issues must be created per OCA process before
branch work begins. The oca-github-bot must be updated for the new series.

## Cross-references
- `agents/knowledge/benchmarks/oca-community-governance.md`
- `agent-platform/ssot/learning/oca_skill_persona_map.yaml`
