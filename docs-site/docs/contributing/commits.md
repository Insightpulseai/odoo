# Commit conventions

All commits follow the OCA-style convention: one logical change per commit, with a structured message format.

## Message format

```
<type>(<scope>): <description>
```

### Types

| Type | Use for |
|------|---------|
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `refactor` | Code restructuring without behavior change |
| `docs` | Documentation changes only |
| `test` | Test additions or modifications |
| `chore` | Maintenance, tooling, infrastructure |

### Scopes

| Scope | When to use |
|-------|-------------|
| `oca` | OCA layer, submodules, lock files |
| `repo` | Repo-wide maintenance (structure, config) |
| `ci` | Workflows, gating, pre-commit hooks |
| `deps` | Dependencies, toolchain updates |
| `deploy` | Docker, nginx, infrastructure |
| Module name | Changes to a specific module (e.g., `ipai_finance_ppm`) |

### Examples

```
feat(ipai_finance_ppm): add BIR 2307 withholding tax computation
fix(ipai_slack_connector): handle missing channel ID in webhook payload
chore(oca): update web_responsive to latest 19.0 commit
chore(ci): add spec-kit-enforce workflow to all-green-gates
docs(contributing): add commit convention reference
refactor(ipai_auth_oidc): extract token validation to shared utility
test(ipai_finance_ppm): add unit tests for tax line generation
chore(deploy): update container app scaling rules
```

## Commit discipline

### One logical change per commit

Each commit addresses a single concern. Do not mix unrelated changes.

| Do | Do not |
|----|--------|
| Separate module code and CI workflow into two commits | Bundle module code, CI changes, and docs in one commit |
| Fix one bug per commit | Fix three bugs in one "fixes" commit |

### Evidence commits

If a task requires evidence capture (test logs, verification output), commit the evidence files in a separate commit:

```
docs(evidence): add test logs for ipai_finance_ppm 2026-03-13
```

### Docs and tests alongside code

When a code change affects behavior, include documentation and test updates in the same commit or as an immediately following commit.

## PR discipline

- Keep PRs small and focused. One feature or fix per PR.
- Run the verification sequence before pushing:

```bash
./scripts/repo_health.sh && ./scripts/spec_validate.sh && ./scripts/ci_local.sh
```

- Reference the spec bundle in the PR description if applicable.
- All CI checks must pass before merge (`all-green-gates` is required).

## Co-authorship

When working with AI assistants, include the co-author trailer:

```
feat(ipai_finance_ppm): add BIR 2307 computation

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```
