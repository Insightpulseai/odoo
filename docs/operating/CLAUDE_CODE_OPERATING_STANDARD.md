# Claude Code Operating Standard (IPAI)

**Status**: canonical
**Authority**: [ssot/governance/claude-code-operating-standard-authority.yaml](../../ssot/governance/claude-code-operating-standard-authority.yaml)

---

## Purpose

Defines how Claude Code (or any repo-local AI agent) should operate in this monorepo. Consolidates what was previously spread across `CLAUDE.md`, `.claude/rules/*`, SSOTs, and evidence.

One document, one operating standard, zero ambiguity.

---

## 1. Authority order (read every session)

When Claude Code starts in this repo, read authority in this order. Lower sources never override higher.

1. **User explicit instruction** (in-session, highest)
2. **CLAUDE.md** at repo root + `~/.claude/CLAUDE.md` global
3. **`.claude/rules/*.md`** (path-scoped rules auto-loaded on demand)
4. **SSOT files under `ssot/`, `platform/ssot/`, `infra/ssot/`, `data-intelligence/ssot/`**
5. **`docs/architecture/*`** (architecture decisions of record)
6. **`spec/<slug>/*`** (capability-specific specs + tasks)
7. **Code truth** (what's actually in the tree)
8. **Azure live runtime** (via `az` / MCP) — ground truth for deployed state
9. **Conversation memory** (personal, non-canonical)

**Rule**: when sources conflict, the higher source wins. If live runtime diverges from SSOT, that's DRIFT — raise it, don't silently accept it.

---

## 2. Startup routine (first 5 actions)

Every session, in order:

1. **Read** `CLAUDE.md` + session `<system-reminder>` blocks
2. **Orient** — `git status` + `git log --oneline -5` + current branch
3. **Identify goal** — what did the user ask? what's the implicit authority (SSOT / spec / runbook)?
4. **Load context** — read the 1–3 most relevant SSOTs before touching code
5. **Plan** — state the plan in one sentence before acting (unless the task is trivial)

Do NOT:
- Start by writing code before reading authority
- Assume defaults without checking SSOT
- Fabricate file paths or commands

---

## 3. Planning routine

For any non-trivial change:

1. State the **outcome** (1 sentence)
2. State the **authority** (which SSOT / spec / rule governs this)
3. State the **plan** (3–7 bullets)
4. State the **evidence path** (where will logs / outputs go)

Use TodoWrite for 3+ step work. Exactly one task in-progress at a time.

---

## 4. Execution routine

- Prefer dedicated tools (Read/Edit/Write/Glob/Grep/Bash) over Agent delegation unless parallel or heavy.
- Use parallel tool calls when independent.
- Never run destructive commands without explicit user approval (see §7).
- When editing: Read first → Edit second. Never Write before Read.
- Keep diffs minimal. No drive-by refactors.

---

## 5. Validation routine

Every non-trivial task ends with ONE of:

- Test run (pytest / odoo test / playwright smoke)
- Verification command with output (curl / az query / git log)
- Schema / policy validation
- Rendered artifact diff
- Runtime health check

**Self-verification is mandatory.** Generation alone is not done.

Cite evidence paths in the final message when evidence is captured.

---

## 6. PR / commit routine

1. Review diff: `git status` + `git diff`
2. Summarize the change in one sentence + rationale
3. Group by logical unit — one commit per concern
4. Use Conventional Commits: `feat|fix|docs|refactor|test|chore(scope): description`
5. Include `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>` trailer
6. Never push without explicit user approval
7. Never use `--no-verify` or amend published commits without explicit approval

---

## 7. Escalation rules

**Stop and ask the user before any of these:**

- Destructive operations (`rm -rf`, `DROP TABLE`, `git push --force`, `git reset --hard`, `kubectl delete`, `az * delete`)
- Hard-to-reverse operations (downgrading deps, modifying CI/CD pipelines, amending published commits)
- Shared-state mutations (pushing code, creating PRs, sending Slack/email, modifying shared infra/permissions, creating ADO work items, inviting Entra guests)
- Uploads to third-party web tools (diagram renderers, gists)
- Live-tenant changes (Entra, Odoo prod, Azure prod resources)

When blocked: say what's missing in one sentence, continue everything that can be done without asking questions.

---

## 8. Forbidden shortcuts

Never:

- Hardcode secrets in source (see `.claude/rules/secrets-policy.md`)
- Echo secrets in debug output
- Ask the user to paste tokens
- Use `git add -A` (risks sensitive files) — stage explicit files
- Bypass hooks with `--no-verify` unless user explicitly approved
- Write documentation files without user asking (no proactive `.md` sprawl)
- Fabricate module names, CLI flags, or URLs (see CLAUDE.md guardrail)
- Use deprecated services (Supabase, Vercel, Cloudflare Workers, n8n, DigitalOcean, Mailgun, Mattermost, Wix — per CLAUDE.md deprecation list)

---

## 9. Subagent usage

See [templates/claude/SUBAGENT_CATALOG.md](../../templates/claude/SUBAGENT_CATALOG.md).

Use subagents (`Agent` tool) when:

- 2+ independent tasks that can parallelize with separable file/plane ownership
- Context-protection (delegate research that would flood main session)
- Role specialization matches an existing subagent type (python-expert, quality-engineer, security-engineer, root-cause-analyst, etc.)

Default model: `sonnet` for subagent dispatches per CLAUDE.md global routing rule. Use `haiku` for log parsing / simple grep. `opus` only when task requires deep reasoning.

Never:

- Dispatch subagents for SSOT/architecture drafting (main session owns this)
- Dispatch subagents without a self-contained prompt
- Duplicate work across parallel subagents

---

## 10. Session lifecycle (see SESSION_LIFECYCLE.md)

```
start → load_authority → inspect_repo → make_plan → execute → validate → summarize → commit_or_handoff
```

Detail in [SESSION_LIFECYCLE.md](SESSION_LIFECYCLE.md).

---

## 11. Tone and output

- Default concise. No trailing summaries unless asked.
- Tables over prose for structured data.
- No emojis unless user explicitly requested.
- Reference files with `[filename.ext](path)` markdown links (clickable in VS Code extension).
- End with one-sentence status + next action (or nothing if nothing to say).

---

## 12. Deprecation hygiene

When touching legacy code, check if the module/service is on the CLAUDE.md deprecation list. If it is:

- Don't extend it
- Don't add features to it
- Leave a pointer to the replacement
- Raise it if user seems unaware

---

## 13. Evidence discipline

Per [ssot/release/go-live-readiness.yaml](../../ssot/release/go-live-readiness.yaml):

- Every meaningful task produces evidence in `docs/evidence/<YYYYMMDD-HHMM>/<scope>/`
- Evidence is not SSOT (see `.claude/rules/ssot-platform.md` Rule 6)
- Named approver + timestamp + commit hash + SSOT link for closure
- Never mark work done without these four

---

## 14. Tool / MCP usage

- MCP allowlist authority: [ssot/governance/mcp-allowlist.yaml](../../ssot/governance/mcp-allowlist.yaml)
- Current runtime state: [ssot/tooling/mcp-runtime-state.yaml](../../ssot/tooling/mcp-runtime-state.yaml)
- Unified MCP pattern: [ssot/agent-platform/skill-pack-pattern-unified.yaml](../../ssot/agent-platform/skill-pack-pattern-unified.yaml)

Use MCP servers for tool access, not for architecture decisions.

---

## 15. Related standards

| Concern | Authority |
|---|---|
| Project identity + invariants | `CLAUDE.md` + `~/.claude/CLAUDE.md` |
| Path-scoped rules | `.claude/rules/*.md` |
| Subagent catalog | [templates/claude/SUBAGENT_CATALOG.md](../../templates/claude/SUBAGENT_CATALOG.md) |
| Session lifecycle | [SESSION_LIFECYCLE.md](SESSION_LIFECYCLE.md) |
| Headless workflows | [HEADLESS_AGENT_WORKFLOWS.md](HEADLESS_AGENT_WORKFLOWS.md) |
| Starter CLAUDE.md template | [templates/claude/CLAUDE.md](../../templates/claude/CLAUDE.md) |
| Unified capability template | [spec/_templates/unified-capability-template.md](../../spec/_templates/unified-capability-template.md) |
| Go-live readiness | [ssot/release/go-live-readiness.yaml](../../ssot/release/go-live-readiness.yaml) |
| Planning authority | [ssot/governance/planning-surface-authority-map.yaml](../../ssot/governance/planning-surface-authority-map.yaml) |
| Identity authorities | [ssot/identity/entra-identity-matrix.yaml](../../ssot/identity/entra-identity-matrix.yaml) |
| Agent runtime | [ssot/agent-platform/agent_framework_adoption.yaml](../../ssot/agent-platform/agent_framework_adoption.yaml) |

---

## Non-goals

- Not a replacement for `CLAUDE.md` (this complements)
- Not a substitute for individual SSOT files (this references them)
- Not adopted as a rigid process — solo-ops scale prefers clear rules over ceremony
- Not a marketing document — internal operator standard
