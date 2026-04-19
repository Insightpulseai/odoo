# Session Lifecycle

Canonical session lifecycle for Claude Code / repo-local agents in IPAI.

Authority: [CLAUDE_CODE_OPERATING_STANDARD.md §10](CLAUDE_CODE_OPERATING_STANDARD.md)

---

## 8-step flow

```
start → load_authority → inspect_repo → make_plan → execute → validate → summarize → commit_or_handoff
```

---

## 1. Start

- Read system context + `<system-reminder>` blocks
- Note session-specific guidance (worktree? CI? headless?)
- Note deferred tool availability (ToolSearch)

## 2. Load authority

Per [CLAUDE_CODE_OPERATING_STANDARD.md §1](CLAUDE_CODE_OPERATING_STANDARD.md):

1. User explicit instruction
2. `CLAUDE.md` (repo) + `~/.claude/CLAUDE.md` (global)
3. `.claude/rules/*.md` (on demand)
4. SSOTs (`ssot/`, `platform/ssot/`, `infra/ssot/`)
5. `docs/architecture/*`
6. `spec/<slug>/*`
7. Code truth
8. Azure live runtime (if relevant)

Do NOT start without authority loaded for the scope.

## 3. Inspect repo

- `git status` → working tree state
- `git log --oneline -5` → recent direction
- `git branch` → current lane
- `ls` targeted dirs → orient structure
- Read 1–3 most relevant SSOTs

## 4. Make plan

- Outcome (1 sentence)
- Authority (SSOT / rule / spec reference)
- Plan (3–7 bullets for non-trivial work)
- Evidence path if applicable
- TodoWrite for 3+ step work; exactly one `in_progress` at a time

## 5. Execute

- Parallel tool calls when independent
- Read before Edit; never Write before Read
- Minimal diffs
- Announce each significant action in one sentence

## 6. Validate

Per [CLAUDE_CODE_OPERATING_STANDARD.md §5](CLAUDE_CODE_OPERATING_STANDARD.md):

- Test run, or
- Verification command with output, or
- Schema / policy check, or
- Artifact diff, or
- Runtime health check

Cite evidence paths.

## 7. Summarize

- Outcome (1–3 lines)
- Evidence (paths)
- Verification (pass/fail with key lines)
- Changes shipped (paths + one-line intent)
- Next action (1 line) or nothing

Use [output-format.md](../../../.claude/rules/output-format.md) structure when paste-to-ChatGPT is likely.

## 8. Commit or handoff

**Commit path**:
1. `git status` + `git diff`
2. `git log --oneline -5` for style
3. Stage explicit files (never `git add -A`)
4. Conventional Commits message + `Co-Authored-By` trailer
5. Never push without explicit approval

**Handoff path**:
1. Update TodoWrite state
2. Capture context in evidence bundle if substantial
3. Note what's in-flight vs blocked
4. Note any uncommitted work

---

## Headless variant

If invoked headless (CI, background agent, scheduled):

- Skip interactive clarifying questions
- Continue everything executable; report blockers at end
- Keep output structured (evidence + verification)
- Do NOT invent missing credentials or prompts

See [HEADLESS_AGENT_WORKFLOWS.md](HEADLESS_AGENT_WORKFLOWS.md).

---

## Subagent variant

If invoked as a subagent:

- Expect self-contained prompt (no parent context)
- Narrow to the specific task
- Report in the format the parent requested
- Do not spawn further subagents unless parent explicitly permits

---

## Anti-patterns (avoid)

| Anti-pattern | Correct behavior |
|---|---|
| Write code before reading authority | Load authority first |
| Fabricate file paths | Glob/Grep first |
| Write comments explaining what code does | Let identifiers speak; only comment the non-obvious WHY |
| Trailing summary of what just changed | User can read the diff; don't recap unless asked |
| `git add -A` | Stage explicit files |
| Push without approval | Stop, ask |
| Create `.md` files proactively | Only when user requested |
| Run destructive commands without approval | Escalate per [OPERATING_STANDARD §7](CLAUDE_CODE_OPERATING_STANDARD.md) |
| Repeatedly re-read a just-edited file | Trust edit/write errors |
| Narrate internal deliberation | State decisions directly |
