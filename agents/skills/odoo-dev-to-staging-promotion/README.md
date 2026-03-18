# odoo-dev-to-staging-promotion

Validates and executes dev-to-staging branch promotion with full CI and developer evidence verification.

## When to use
- Dev branch ready for staging promotion
- All CI checks passing and developer sign-off complete
- Scheduled promotion window

## Key rule
Never promote without CI evidence. Never skip staging. Document rollback path before promotion.

## Cross-references
- `agents/knowledge/benchmarks/odoo-sh-persona-model.md`
- `agents/personas/odoo-release-manager.md`
- `agents/skills/odoo-ci-validation/skill-contract.yaml`
