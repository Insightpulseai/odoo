---
mode: agent
tools:
  - repo
  - tests
  - search
description: "Template for FixBot end-to-end implementation runs. Fill in the bracketed sections before invoking."
---

# FixBot — End-to-End Implementation Prompt

Use this prompt file when invoking the FixBot agent for a fix or small feature.
Fill in every bracketed section. Do not invoke with placeholders left empty.

---

## Context

- **Scope**: [Which files, directories, or domains are in scope for this fix]
- **Out of scope**: [Explicitly list what FixBot must not touch]
- **Related spec**: [spec/<slug>/ if one exists, or "none"]
- **Related issue/PR**: [GitHub issue # or PR # if applicable]

## Constraints

- PR-only; no direct push to `main`
- Minimal diffs — touch only what is needed for this fix
- Forbidden paths (do not touch without explicit override):
  - `supabase/migrations/**`
  - `infra/**`
  - `.github/workflows/**`
  - `ssot/**`
- Secrets by name only — never inline credential values

## Task

[Describe exactly what needs to be implemented or fixed. Be specific about:
- What the current broken behavior is
- What the correct behavior should be
- Any specific files or functions to modify]

## Verification Gates (all must pass before opening PR)

```bash
python scripts/ci/check_repo_structure.py     # SSOT boundary check
pre-commit run --all-files                    # linters and formatters
```

[Add any domain-specific gate, e.g.:]
```bash
bash scripts/ci/validate_skills_registry.py   # if ssot/agents/ is in scope
bash scripts/dev/docker_doctor.sh             # if DevContainer config is in scope
```

## Acceptance Criteria

- [ ] [Specific testable outcome 1]
- [ ] [Specific testable outcome 2]
- [ ] All verification gates above pass
- [ ] PR body includes [CONTEXT] [CHANGES] [EVIDENCE] [DIFF SUMMARY] [ROLLBACK]

## Rollback

[How to revert if this change causes a regression:
- e.g., `git revert <commit-hash>`
- e.g., `ALTER TABLE ops.runs DROP COLUMN IF EXISTS last_phase;`]
