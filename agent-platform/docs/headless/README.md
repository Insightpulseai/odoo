# Claude Headless — Integration Spec

> **Canonical rule**
>
> Claude headless is a **deterministic repo-and-operations automation lane** for Pulser, running in bare mode, with schema-constrained outputs, explicit tool permissions, and resumable sessions — **not** the main business-runtime assistant.

## Two Lanes

```
Lane A — product runtime
  = Odoo + Foundry + Azure AI Search + Pulser policy engine + validators + behavior matrix

Lane B — repo automation runtime  (this spec)
  = Claude headless / Agent SDK, --bare, schema outputs, narrow tool approvals, PR/CI workflows
```

## Non-Negotiables

1. **Default to `--bare`** in every automation. No local hook/skill/plugin/MCP/auto-memory/CLAUDE.md leakage.
2. **Schema-first output** — `--output-format json` + `--json-schema` whenever downstream systems consume the result.
3. **Explicit `--allowedTools`** — never rely on interactive prompts in CI.
4. **Resumable sessions** — capture session id; resume only that session for multi-step operator flows.
5. **Prompt layering via `--append-system-prompt`** — keep default behavior, add narrow role instructions.
6. **No business mutations** — headless never writes to Odoo, approves invoices, or touches production state. All business writes go through Lane A.

## Authorized Use Cases

| Use case | Lane | Pattern |
|---|---|---|
| Spec Kit bundle checks | B | schema output + constitution/PRD/plan/tasks comparison |
| Odoo repo migrations / refactors | B | codemods, XML/view migration, naming normalization |
| Infra review (Bicep, Terraform) | B | diff review with append-system-prompt |
| PR diff review | B | structured findings JSON |
| Release/cutover checklists | B | deterministic checklist generation |
| Drift detection summaries | B | resource graph vs SSOT comparison |
| Cost-optimization review | B | Azure billing vs budget analysis |
| Repo hygiene / commit messages | B | staged diff → conventional commit |
| **End-user research tools** | A | stays in Pulser runtime |
| **Finance cockpit / approvals** | A | stays in Pulser runtime under RBAC |
| **Production business writes** | A | stays in Pulser runtime |

## Four Patterns

### Pattern 1 — Schema-first automation
```bash
claude --bare -p "<prompt>" \
  --output-format json \
  --json-schema agent-platform/runtimes/claude-headless/schemas/<name>.json
```

### Pattern 2 — Explicit tool approvals
```bash
claude --bare -p "<prompt>" \
  --allowedTools "Read,Grep,Glob"   # narrowest set that works
```

### Pattern 3 — Reusable operator sessions
```bash
SID=$(claude --bare -p "investigate X" --print-session-id)
claude --bare --resume "$SID" -p "now patch"
claude --bare --resume "$SID" -p "now verify"
```

### Pattern 4 — Prompt layering
```bash
claude --bare -p "<task>" \
  --append-system-prompt "You are a security reviewer. Report findings as JSON."
```

## Files in this lane

- `runtimes/claude-headless/lib/run.sh` — shared bare-mode invocation helper
- `runtimes/claude-headless/schemas/*.json` — JSON schemas for structured outputs
- `runtimes/claude-headless/scripts/*.sh` — concrete automation scripts
- `.github/workflows/claude-headless-*.yml` — CI pipelines

## What not to do

- Do not make headless the authority for business-state mutation
- Do not let local memory/plugins leak into CI (always `--bare`)
- Do not use freeform text output where a schema should exist
- Do not treat it as the main multitenant agent platform
- Do not let it bypass the behavior matrix, RBAC, or validator model

## Reference

Source: https://code.claude.com/docs/en/headless
