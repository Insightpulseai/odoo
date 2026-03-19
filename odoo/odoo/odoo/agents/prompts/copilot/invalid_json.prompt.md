---
mode: agent
tools:
  - repo
  - search
description: "Debug and repair invalid JSON in workflow exports, config files, Supabase migration JSONB columns, or API responses."
---

# Invalid JSON Debugging

Use this prompt when a JSON file or API response fails parsing and the error is unclear.
Applies to: n8n workflow exports, Supabase seed files, Odoo config JSONB, Edge Function payloads.

Fill in every bracketed section before invoking.

---

## Context

- **File or source**: [file path, or "API response from <endpoint>"]
- **Error message**: [e.g. `SyntaxError: Unexpected token '}' at position 1432`]
- **Origin**: [n8n export / Supabase seed / API response / config file]
- **Related spec or workflow**: [spec/<slug>/ or workflow name, or "none"]

## Constraints

- Use `json.loads()` only — never `eval()` or `ast.literal_eval()`
- If a tracked file: commit the corrected file with an explanation comment in the PR body
- If a runtime API response: add an error-guard patch to the parsing code only
- Never silently drop keys to make JSON valid — explain every removal in the PR body
- If the source is a generated file, identify and fix the upstream generator instead
- Minimal diff; PR-only

## Task

1. Read the file (or inline the JSON string below).
2. Identify every syntax error and explain the cause of each.
3. Produce a corrected version.
4. If the file is tracked, write it back; if it is a runtime response, patch the parser.
5. Validate the fix:

```bash
python -c "import json; json.load(open('<file>'))"
```

## Verification Gates (all must pass before opening PR)

```bash
python -c "import json; json.load(open('<corrected-file>'))"   # no exception = PASS
pre-commit run --all-files
```

## Acceptance Criteria

- [ ] `python -c "import json; json.load(open(...))"` exits 0
- [ ] Every removed or changed key is explained in the PR body
- [ ] No `eval()` or `ast.literal_eval()` introduced
- [ ] `pre-commit run --all-files` passes
- [ ] PR body includes `[CONTEXT] [CHANGES] [EVIDENCE] [DIFF SUMMARY] [ROLLBACK]`
- [ ] Evidence log saved to `web/docs/evidence/<YYYYMMDD-HHMM+0800>/json-debug/logs/validate.txt`

## Rollback

```bash
git revert <commit-hash>    # revert the corrected file
```
