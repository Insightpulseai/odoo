---
mode: ask
description: "Template for Reviewer agent read-only code review runs. Fill in the bracketed sections."
---

# Reviewer — Read-Only Code Review Prompt

Use this prompt when invoking the Reviewer agent. No file edits will be made.
Fill in the bracketed sections before invoking.

---

## Context

- **PR branch**: [branch name, e.g. `feat/ops-runs-checkpoint`]
- **PR number**: [GitHub PR # if available]
- **Files changed**: [List key files, or "all changed files in the PR"]
- **Domains touched**: [e.g., supabase/migrations, ssot/agents, apps/ops-console]

## Review Task

Review the above for:

1. **SSOT boundary compliance** — files in the correct directories per `docs/architecture/PLATFORM_REPO_TREE.md`
2. **PR atomicity** — only one logical domain changed (per `.github/copilot-instructions.md`)
3. **No hardcoded secrets** — no tokens, passwords, or API keys in any changed file
4. **Migration safety** — any `supabase/migrations/` files use `ADD COLUMN IF NOT EXISTS`; no `DROP`/`TRUNCATE` on `ops.*`
5. **Commit convention** — messages follow `type(scope): description`
6. **PR body completeness** — includes `[CONTEXT]` `[CHANGES]` `[EVIDENCE]` `[DIFF SUMMARY]`
7. **OCA compliance** — no OCA source modifications; overrides use `ipai_*` modules
8. **No Enterprise dependencies** — no EE module imports or `odoo.com` IAP calls

## Output Format

Produce a structured review using the Reviewer agent output format:

```
Status: PASS | FAIL | NEEDS_REVISION
Issues: [file:line — severity — description]
SSOT Compliance: [PASS/FAIL per check]
Recommendation: [one paragraph]
```

## Scope Limits

- **Read only** — do not modify any file
- If you identify a fix that is needed, describe it precisely but do not apply it
