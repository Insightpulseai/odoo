---
mode: agent
tools:
  - repo
  - search
description: "Generate a Mermaid architecture, sequence, ER, or class diagram that renders natively on GitHub. No external services, no invented nodes."
---

# Diagram Generation

Use this prompt when an architecture, data flow, sequence, or entity-relationship
needs visualisation that renders natively in GitHub Markdown.

Fill in every bracketed section before invoking.

---

## Context

- **System to diagram**: [e.g. `n8n → Supabase Edge Function → ops.task_queue → Odoo`]
- **Diagram type**: [flowchart / sequence / ER / class]
- **Target doc**: [repo-relative path of the `.md` file where the diagram will be embedded]
- **Existing partial description** (if any): [repo-relative path or "none"]
- **Related spec**: [spec/<slug>/ or "none"]

## Constraints

- Use Mermaid only (````mermaid` code block) — **no** PlantUML, Lucidchart, or draw.io XML
- No external service URLs in the diagram or doc
- All nodes and edges must correspond to real components in the repo or SSOT
  (check `docs/architecture/PLATFORM_REPO_TREE.md` and `ssot/` for canonical names)
- Never invent components not described in the system description above
- Output: Mermaid source text embedded in the target `.md` file
- Minimal diff: add the diagram block only
- PR-only; no direct push to `main`

## Task

1. Read the existing partial description or SSOT files to confirm component names.
2. Generate a Mermaid diagram matching the system description above.
3. Validate it mentally: every node and edge must map to a real repo entity.
4. Embed the ````mermaid` block at the appropriate location in the target doc.

## Verification Gates (all must pass before opening PR)

```bash
pre-commit run --all-files   # markdown lint
```

Mermaid syntax check (optional local):
```bash
npx @mermaid-js/mermaid-cli mmdc -i <diagram.mmd> -o /tmp/diagram.svg
```

## Acceptance Criteria

- [ ] Mermaid code block renders on GitHub (no syntax errors)
- [ ] No PlantUML, Lucidchart, or draw.io content
- [ ] All nodes match real components in SSOT or repo
- [ ] No external service URLs in the diff
- [ ] `pre-commit run --all-files` passes
- [ ] PR body includes `[CONTEXT] [CHANGES] [EVIDENCE] [DIFF SUMMARY] [ROLLBACK]`
- [ ] Evidence log saved to `web/docs/evidence/<YYYYMMDD-HHMM+0800>/diagrams/logs/mermaid_lint.txt`

## Rollback

```bash
git revert <commit-hash>    # removes the diagram block
```
