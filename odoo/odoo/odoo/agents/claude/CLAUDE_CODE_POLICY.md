# Claude Code Usage Policy — Insightpulseai/odoo

> Governance for Claude Code CLI usage in this repository.
> All team members and automated agents must follow these rules.

---

## Routing

All Claude Code CLI invocations in this repo MUST route through the Vercel AI Gateway.
See `docs/agents/VERCEL_CLAUDE_CODE.md` for setup instructions.

Required env vars:
```bash
ANTHROPIC_BASE_URL=https://ai-gateway.vercel.sh
ANTHROPIC_AUTH_TOKEN=<team-gateway-key>
ANTHROPIC_API_KEY=   # empty — gateway authenticates
```

Direct Anthropic API access (without gateway) is only allowed for:
- Emergency fallback when gateway is unavailable
- Individual developer experiments outside of repo work

---

## Allowed operations (Claude Code in this repo)

| Operation | Allowed | Notes |
|-----------|---------|-------|
| Read any file | ✅ | No restrictions |
| Edit source code files | ✅ | Must pass lint + typecheck |
| Create new files | ✅ | Follow CLAUDE.md conventions |
| Run `npm/pnpm/python` commands | ✅ | Via Bash tool |
| `git status / diff / add / commit / push` | ✅ | OCA commit style required |
| `gh pr create / view / comment` | ✅ | For PR workflow |
| SSH to production droplet | ⚠️ Read-only only | No `rm`, no `docker restart`, no config changes |
| Modify `.github/workflows/` | ✅ | Requires PR review |
| Modify `infra/` | ✅ | Requires PR review |
| `git push --force` | ❌ | Never |
| Delete branches | ❌ | Never without explicit instruction |
| Modify `CLAUDE.md` | ⚠️ | Only via `scripts/agents/sync_agent_instructions.py` |

---

## Model tiers

Use the most capable model appropriate for the task. Prefer lower tiers for speed/cost:

| Task | Recommended model |
|------|------------------|
| File edits, completions, boilerplate | `claude-haiku-4-5-20251001` |
| Primary development, PRs, analysis | `claude-sonnet-4-6` (default) |
| Architecture, critical path decisions | `claude-opus-4-6` |

---

## Evidence and audit trail

Every Claude Code session that modifies files must produce:
- A git commit with an OCA-style message
- Evidence in `web/docs/evidence/<YYYYMMDD-HHMM+0800>/<scope>/` for significant changes
- A reference to the relevant spec bundle (`spec/<feature>/`) if one exists

Do not claim completion without a commit hash or an evidence artifact path.

---

## What Claude Code must not do

1. Hardcode secrets, tokens, or passwords in any file
2. Add `NEXT_PUBLIC_` prefix to server-only variables
3. Commit `.env*` files
4. Skip pre-commit hooks (`--no-verify`)
5. Introduce UI framework dependencies without a PR discussion
6. Generate code that bypasses RLS policies
7. Add `service_role` key to client-side code

---

## Periodic review

This policy is reviewed quarterly. Changes must be submitted as a PR to this file
with a brief rationale in the PR description.

Last reviewed: 2026-02
