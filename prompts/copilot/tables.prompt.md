---
mode: agent
tools:
  - repo
  - search
description: "Generate a comparison table, matrix, or structured reference from a data source. All rows must be present; no invented data."
---

# Table Generation

Use this prompt when a doc, SSOT YAML, or PR description needs a comparison table,
matrix, or structured reference that doesn't exist yet.

Fill in every bracketed section before invoking.

---

## Context

- **Data source**: [file path, YAML key, CSV path, or paste list below]
- **Target doc**: [repo-relative path where the table will be embedded or created]
- **Format**: [GitHub Markdown table / YAML mapping / CSV]
- **Columns required**: [e.g. `Module | Domain | Status | OCA Equivalent`]
- **Sort / group**: [e.g. "sort by domain ascending, group by status"]
- **Related spec**: [spec/<slug>/ or "none"]

## Constraints

- Use GitHub Markdown tables — never HTML `<table>` tags (unless the doc is HTML)
- No merged cells (Markdown does not support them)
- Row count in the output must equal row count in the source — never truncate with "..."
- Never invent data not present in the source — cite the source for each cell if asked
- Minimal diff: embed the table in the target doc or create the standalone file only
- PR-only; no direct push to `main`

## Task

1. Read the data source file or use the list pasted below.
2. Count source rows; record the count.
3. Generate the table with the requested columns and sort order.
4. Verify row count matches source (document in PR body: "Source: N rows → Table: N rows").
5. Embed in the target doc at the correct location, or create the standalone file.

## Verification Gates (all must pass before opening PR)

```bash
pre-commit run --all-files   # markdown lint
```

Row count check (document in evidence):
```bash
# Example: count rows in a YAML list
python -c "import yaml; d=yaml.safe_load(open('<source>')); print(len(d['items']))"
```

## Acceptance Criteria

- [ ] Table row count equals source row count
- [ ] No data invented — every cell traceable to the source
- [ ] No HTML tables used (unless doc is HTML)
- [ ] No truncation with "..."
- [ ] `pre-commit run --all-files` passes
- [ ] PR body includes `[CONTEXT] [CHANGES] [EVIDENCE] [DIFF SUMMARY] [ROLLBACK]`
- [ ] Evidence log saved to `web/docs/evidence/<YYYYMMDD-HHMM+0800>/tables/logs/row_count.txt`

## Rollback

```bash
git revert <commit-hash>    # removes the table
```
