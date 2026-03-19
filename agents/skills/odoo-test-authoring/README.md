# odoo-test-authoring

Writes Python tests for Odoo module functionality, regression checks, and integration tests.

## When to use
- A new module is created without test coverage
- New business logic requires regression tests
- A bug fix needs a regression test
- A PR modifies models or business logic without corresponding tests

## Key rule
Tests must run on disposable `test_<module>` databases. Never use prod, dev, or staging DBs.
Every failure must be classified per the testing policy. Never claim "all tests pass" without
citing the evidence log.

## Cross-references
- `agents/knowledge/benchmarks/odoo-developer-howtos.md`
- `agents/knowledge/benchmarks/odoo-coding-guidelines.md`
- `~/.claude/rules/testing.md`
