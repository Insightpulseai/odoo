# IPAI Engineering Constitution (LLM Pack)

## Core Principles

1. **SSOT: GitHub repos** - No manual UI operations; all changes via code
2. **All changes via PRs** - CI green required before merge
3. **No secrets in repo** - Use Vault, Actions secrets, or environment variables
4. **Idempotent scripts** - Deterministic, reproducible outputs
5. **Evidence-based deployment** - Every deploy produces verifiable proof

## Execution Model

```
explore -> plan -> implement -> verify -> commit
```

- Never guess: Read files first, then change them
- Simplicity first: Prefer the simplest implementation
- Verify always: Include verification after any mutation
- Minimal diffs: Keep changes small and reviewable
- Update together: Docs and tests change with code

## Technology Stack

| Component | Technology |
|-----------|------------|
| ERP | Odoo CE 18.0 + OCA |
| Database | PostgreSQL 15 |
| Automation | n8n + Supabase Edge Functions |
| Chat | Mattermost |
| AI Agents | Claude, ChatGPT, Codex |
| Control Plane | Supabase (spdtwktxdalcfigzeqrz) |

## Banned Behaviors

- No deployment guides as primary output (execute instead)
- No "here's how to..." (do it and show proof)
- No asking for confirmation to proceed
- No time estimates
- No unstated assumptions

## Commit Convention

```
feat|fix|refactor|docs|test|chore(scope): description
```

Examples:
- `feat(finance-ppm): add month-end close wizard`
- `fix(workspace): resolve portal access issue`
- `chore(ci): add spec validation workflow`
