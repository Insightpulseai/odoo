# odoo-ci-validation

Validates CI pipeline status, test gates, and build verification for Odoo CE 18 module changes via GitHub Actions.

## When to use
- PR opened or updated with module changes
- CI pipeline failure on required status check
- Pre-merge validation request
- Build status verification after push

## Key rule
All required status checks must pass. Test failures must be classified per testing policy. Never skip CI or bypass pre-commit hooks.

## Cross-references
- `agents/knowledge/benchmarks/odoo-sh-persona-model.md`
- `agents/personas/odoo-developer.md`
- `.claude/rules/testing.md`
