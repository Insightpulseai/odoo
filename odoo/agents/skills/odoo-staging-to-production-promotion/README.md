# odoo-staging-to-production-promotion

Validates and executes staging-to-production deployment with tester sign-off, platform admin readiness, rollback path, and bake-time observation.

## When to use
- Staging validation complete with no blockers
- Tester and platform admin sign-off received
- Scheduled production deployment window

## Key rule
Never deploy without tester evidence, database backup, active monitoring, and a documented rollback path. Release is not healthy until bake-time observation completes.

## Cross-references
- `agents/knowledge/benchmarks/odoo-sh-persona-model.md`
- `agents/personas/odoo-release-manager.md`
- `agents/skills/odoo-staging-validation/skill-contract.yaml`
- `agents/skills/odoo-backup-recovery/skill-contract.yaml`
