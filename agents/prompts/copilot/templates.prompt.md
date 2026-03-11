---
mode: agent
tools:
  - repo
  - search
description: "Scaffold a new spec bundle, runbook, migration, PR body, or SSOT YAML from a canonical reference file. No placeholder values left."
---

# Template Creation

Use this prompt when a new spec bundle, runbook, migration file, or PR description
needs to follow a standard structure and no template instance exists yet.

Fill in every bracketed section before invoking.

---

## Context

- **Template type**: [spec bundle / runbook / migration / PR body / SSOT YAML / agent file]
- **Reference file** (existing example): [repo-relative path to an existing file of the same type]
- **New slug / name**: [e.g. `ipai-webhook-retry`, `dns-mail-contract`, `add_ocr_confidence_col`]
- **Target path**: [canonical path per `docs/architecture/PLATFORM_REPO_TREE.md`]
- **Related spec**: [spec/<slug>/ or "none"]

## Constraints

- New file must be created at a path listed in `docs/architecture/PLATFORM_REPO_TREE.md`
  (or the SSOT Assignment Table must be updated first)
- Frontmatter / schema must match the reference file exactly
- No placeholder values left (`[TODO]`, `<fill_in>`, `TBD`)
- No hardcoded secrets — use `<from-vault>` or env var placeholders
- Minimal diff: create the single new file only
- PR-only; no direct push to `main`

## Task

1. Read `docs/architecture/PLATFORM_REPO_TREE.md` to verify the target path is canonical.
2. Read the reference file to extract the exact schema / frontmatter.
3. Create the new file at the target path, following the reference schema, with all
   placeholder sections filled in for the new slug.
4. If the path is not in `PLATFORM_REPO_TREE.md`, add a row to the SSOT Assignment Table
   as part of the same PR.

## Verification Gates (all must pass before opening PR)

```bash
pre-commit run --all-files
python scripts/ci/check_repo_structure.py   # SSOT boundary check
```

## Acceptance Criteria

- [ ] New file created at the correct canonical path
- [ ] Frontmatter / schema matches the reference file
- [ ] No placeholder values remain in the file
- [ ] No hardcoded secrets
- [ ] `pre-commit run --all-files` passes
- [ ] PR body includes `[CONTEXT] [CHANGES] [EVIDENCE] [DIFF SUMMARY] [ROLLBACK]`
- [ ] Evidence log saved to `web/docs/evidence/<YYYYMMDD-HHMM+0800>/templates/logs/created.txt`

## Rollback

```bash
git revert <commit-hash>    # removes the new template file
```
