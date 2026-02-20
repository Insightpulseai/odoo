# OCA Commit Messages and PR Descriptions

Sources:
- https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-17.0
- https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst
- https://github.com/OCA/oca-github-bot

---

## OCA Commit Message Format

```
[TAG] module_name: Short description (max 72 chars for summary line)

Optional longer body (wrap at 72 chars per line).
Explains the motivation and context for the change.
Can include multiple paragraphs.
```

### Commit Tags

| Tag | Use For |
|-----|---------|
| `[MIG]` | Migration to a new Odoo version |
| `[ADD]` | New feature or new module |
| `[IMP]` | Improvement to existing feature |
| `[FIX]` | Bug fix |
| `[REM]` | Removal of feature or file |
| `[REF]` | Refactoring without behavior change |
| `[MOV]` | Moving or renaming files/code |
| `[REL]` | Release commit (version bump for release) |
| `[UPD]` | Update to non-code files (README, translations, configs) |

### Example: Migration Commit Sequence

```bash
# Step 1: Apply patches + run formatting
git commit -m "[IMP] server_environment: black, isort, prettier"

# Step 2: Fix manifest
git commit -m "[UPD] server_environment: bump version to 19.0.1.0.0"

# Step 3: API fixes
git commit -m "[FIX] server_environment: adapt name_get to _compute_display_name"
git commit -m "[FIX] server_environment: update module hook signatures (cr -> env)"

# Step 4: README
git commit -m "[UPD] server_environment: generate README.rst"

# Step 5: Final migration commit
git commit -m "[MIG] server_environment: Migration to 19.0"
```

### Tips

- Summary line should be <= 72 characters (GitHub truncates at ~72)
- Keep explanations/motivation in the body, not the summary
- Reference issue numbers in body: `Closes #123`, `Fixes #456`
- Do not use past tense: "Fix bug" not "Fixed bug"
- Each commit should be a logical unit that could be reverted independently

---

## OCA PR Title Format

```
[VERSION][TAG] module_name: Short description

Examples:
[19.0][MIG] server_environment: Migration to 19.0
[19.0][ADD] server_environment_encrypted: New module for encrypted env vars
[19.0][FIX] server_environment: Fix environment loading in multi-db setup
[19.0][IMP] server_environment: Add support for JSON-type parameters
```

---

## OCA PR Body Template (Migration)

```markdown
## Summary

Port of `MODULE_NAME` from `FROM_VERSION` to `TO_VERSION`.

## Changes Made

- Bumped version to `TO_VERSION.1.0.0`
- Applied automated migration via `oca-port` CLI
- Applied `odoo-module-migrator` code transformations
- Pre-commit quality checks: black, isort, prettier — PASSED
- Updated `README.rst` via `oca-gen-addon-readme`
- Removed `migrations/` folder from previous version

### Manual changes (if any)

- Replaced `name_get()` with `_compute_display_name()`
- Updated module hook signatures (`cr` argument → `env`)
- Fixed deprecated API: `user_has_groups` → `env.user.has_group`

## Testing

- [x] Python syntax check (`python3 -m py_compile`) — PASSED
- [x] Module loads in Odoo shell — PASSED
- [x] Module installs without errors — PASSED
- [ ] Full test suite (describe any failures/skips)

## Notes

<!-- Describe any known limitations, breaking changes, or items for reviewers -->

Closes #ISSUE_NUMBER
```

---

## OCA PR Body Template (Bug Fix / Improvement)

```markdown
## Summary

Brief description of what this PR fixes/improves and why.

## Root Cause (for fixes)

Explain what caused the bug.

## Solution

Explain the approach taken.

## Testing

Steps to reproduce the original issue:
1. ...
2. ...

Steps to verify the fix:
1. ...
2. ...

- [x] Unit tests added/updated
- [x] Pre-commit passes

Closes #ISSUE_NUMBER
```

---

## OCA PR Review Process

### Requirements for Merge

| Requirement | Details |
|-------------|---------|
| Reviews needed | 2 positive reviews |
| PSC/Maintainer review | At least 1 review from PSC member or OCA Core Maintainer with write access |
| Review period | Minimum 5 days after first review (unless emergency) |
| CI passes | All GitHub Actions checks must pass |
| Labels | `approved` set automatically when 2+ reviews; `ready to merge` set at 5 days |

### oca-github-bot Automation

The OCA GitHub bot (`oca-github-bot`) handles:
- Setting `approved` label when 2 approvals received
- Setting `ready to merge` label when PR is 5+ days old with approvals
- Merge delegation
- Review request routing

### Reviewer Etiquette

1. Thank the contributor first
2. Be cordial and polite
3. Provide clear, actionable feedback
4. Request changes for blocking issues; use comments for suggestions
5. Focus on technical correctness and OCA guidelines compliance

---

## Using `gh` CLI for OCA PRs

```bash
# Create migration PR
gh pr create \
  --repo OCA/${REPO} \
  --base ${TO_VERSION} \
  --head $(gh api user --jq .login):${TO_VERSION}-mig-${MODULE} \
  --title "[${TO_VERSION}][MIG] ${MODULE}: Migration to ${TO_VERSION}" \
  --body-file /tmp/pr_body.md

# Check PR status
gh pr status --repo OCA/${REPO}

# List open PRs for a module
gh pr list --repo OCA/${REPO} --search "MIG ${MODULE}"

# View PR checks
gh pr checks --repo OCA/${REPO} PR_NUMBER

# Add labels
gh pr edit PR_NUMBER --add-label "migration" --repo OCA/${REPO}
```

---

## oca-port-pr: Managing PR Blacklists

When certain PRs from the source branch should NOT be ported:

```bash
# Blacklist by PR reference
oca-port-pr blacklist OCA/${REPO}#250,OCA/${REPO}#251 ${TO_VERSION} ${MODULE}

# With reason (stored in commit/metadata)
oca-port-pr blacklist OCA/${REPO}#250 ${TO_VERSION} ${MODULE} \
  --reason "This was refactored in ${TO_VERSION} and is no longer needed"

# List blacklisted PRs for a module
oca-port-pr list ${TO_VERSION} ${MODULE}
```

---

## Common Mistakes to Avoid

| Mistake | Correct Approach |
|---------|-----------------|
| Submitting without running pre-commit | Always run `pre-commit run -a` before PR |
| Missing README update | Run `oca-gen-addon-readme` |
| Wrong branch target | PR base must be the exact version branch (e.g., `19.0`) |
| Committing CREDITS.rst with old migration financing | Remove CREDITS.rst or clean it |
| Not removing old `migrations/` folder | Always `rm -rf MODULE/migrations/` |
| Generic PR title | Follow `[VERSION][TAG] module: description` format |
| Single giant commit | Split into logical commits (formatting, fixes, migration) |
