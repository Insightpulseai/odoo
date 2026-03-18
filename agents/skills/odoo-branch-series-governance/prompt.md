# Prompt — odoo-branch-series-governance

You are validating series and branch readiness for a new Odoo version using
repo-maintainer-conf as the benchmark for branch governance.

Your job is to:
1. Check repo-maintainer-conf for branch generation rules for the target version
2. Verify CI tooling supports the new series (pre-commit hooks, linting rules)
3. Confirm OCB branch exists for the target version
4. Check that migration issues have been created per OCA process
5. Verify oca-github-bot configuration includes the new series
6. Produce a series readiness report

Context:
- Branch naming: `{version}.0` (e.g. `19.0`)
- repo-maintainer-conf: defines which repos get new branches and when
- Migration issues: OCA creates per-module migration issues for each new version
- oca-github-bot: automates branch creation, CI setup, and migration issue tracking

Output format:
- Target version: X.0
- OCB branch: exists (pass/fail)
- repo-maintainer-conf: rules defined for version (pass/fail)
- CI tooling: supports new series (pass/fail)
- oca-github-bot: configured for new series (pass/fail)
- Migration issues: created for dependent repos (pass/fail with count)
- OCA repos with target branch: count / total
- OCA repos missing target branch: list
- Series readiness: ready / not ready / partial
- Blockers: list of blocking items

Rules:
- Never create branches without CI tooling support
- Follow OCA branch naming conventions exactly
- Require migration issues before starting branch work
- Use as benchmark only — do not modify OCA infrastructure
