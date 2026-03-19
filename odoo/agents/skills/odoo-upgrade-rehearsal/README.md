# odoo-upgrade-rehearsal

Execute and validate upgrade rehearsal on a disposable database — test migration scripts, verify data integrity, capture evidence.

## When to use
- Upgrade planning has been approved
- Migration scripts are ready (OpenUpgrade + custom)
- Pre-production rehearsal gate

## Key rule
Never rehearse on production or canonical dev databases. Always use a disposable copy.
Every failure must be classified per testing policy (passes locally / init only / env issue /
migration gap / real defect). Raw test output must be saved to evidence.

## Cross-references
- `agents/knowledge/benchmarks/oca-community-governance.md`
- `agents/skills/odoo-openupgrade-assessment/skill-contract.yaml`
- `agent-platform/ssot/learning/oca_skill_persona_map.yaml`
