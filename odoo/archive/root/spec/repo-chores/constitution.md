# Constitution: Repo Hygiene & Drift Gates

**Version**: 1.0
**Effective**: 2026-02-14
**Scope**: Repository-wide chore automation, lint enforcement, and drift prevention.

---

## Non-Negotiable Rules

1. **No business logic changes.** This spec covers only repo hygiene: formatting, linting, drift gates, deprecated addon quarantine, and deterministic doc regeneration.

2. **Idempotency required.** Every script and CI gate must produce identical results on consecutive runs with no code changes. Running `chore_repo.sh` twice must produce zero diff.

3. **CI-first enforcement.** All hygiene checks must run in CI. Local scripts are convenience wrappers; CI is the authority.

4. **Deprecated addons are quarantined, not deleted.** Modules move to `addons/_deprecated/` and are blocked from install sets by CI. History preserved.

5. **Single generator per artifact.** `spec.md` tree is generated only by `scripts/gen_repo_tree.sh`. No other script may modify the tree section.

6. **Lint configs are repo-root SSOT.** `.yamllint.yml`, `.markdownlint-cli2.jsonc`, `.flake8`, `pyproject.toml` are the single sources for their respective tools.

7. **No manual UI steps.** All chores are CLI/CI-executable. No instructions requiring browser or GUI actions.

---

## Constraints

- Python 3.12+ (Odoo 19 baseline)
- Bash scripts must be POSIX-compatible where possible, `bash` shebang acceptable
- CI workflows target `ubuntu-latest`
- No new runtime dependencies; lint tools are pip/npm dev-only

---

## Amendment Process

Changes to this constitution require:
1. PR with rationale
2. Passing CI gates
3. Maintainer approval
