# odoo-github-flow

Validates GitHub integration workflow for Odoo CE 18 — PR discipline, branch naming, merge rules, and status checks.

## When to use
- New PR opened against main or staging
- Branch naming convention check needed
- Merge readiness assessment
- CODEOWNERS coverage verification

## Key rule
Every PR must have passing status checks, OCA-style commit messages, proper branch naming, and CODEOWNERS coverage. Missing any is a blocker.

## Cross-references
- `agents/knowledge/benchmarks/odoo-sh-persona-model.md`
- `agents/personas/odoo-developer.md`
- `.claude/rules/github-governance.md`
