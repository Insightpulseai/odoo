# odoo-staging-validation

Validates staging environment by running automated tests with production-like data and capturing classified test evidence.

## When to use
- Branch promoted to staging environment
- Staging deployment completed
- Pre-production validation requested
- Module upgrade applied to staging

## Key rule
Never use production database for testing. Every test failure must be classified. Never claim tests pass without an evidence log path.

## Cross-references
- `agents/knowledge/benchmarks/odoo-sh-persona-model.md`
- `agents/personas/odoo-tester.md`
- `.claude/rules/testing.md`
