# OCA Porting Pipeline — Agent Teams Setup

> Concrete setup for using Claude Code Agent Teams to parallelize OCA module porting
> (18.0 → 19.0, 40 modules, `feat/oca-porting-pipeline` branch)

---

## Architecture

```
Lead Agent (feat/oca-porting-pipeline)
  ├── Teammate 1: server-tools group     (worktree: wt/oca-server-tools)
  ├── Teammate 2: connector group        (worktree: wt/oca-connector)
  ├── Teammate 3: bank-statement-import  (worktree: wt/oca-bank)
  ├── Teammate 4: queue + server-ux      (worktree: wt/oca-queue)
  └── Teammate 5: OCA compliance QA      (worktree: wt/oca-qa, read-only review)
```

Each teammate owns distinct `addons/oca/<repo>/` paths → zero file conflicts.

---

## Step 1: Enable Agent Teams

Add to `~/.claude/settings.json` (or project `.claude/settings.json`):

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  },
  "teammateMode": "in-process"
}
```

> Use `"tmux"` instead of `"in-process"` if running inside a tmux session.

---

## Step 2: Create Worktrees (one per teammate)

Run from repo root:

```bash
REPO_ROOT="/Users/tbwa/Documents/GitHub/Insightpulseai/odoo"
cd "${REPO_ROOT}"

# Create worktrees — each teammate gets its own working directory
git worktree add .worktrees/oca-server-tools feat/oca-porting-pipeline
git worktree add .worktrees/oca-connector     feat/oca-porting-pipeline
git worktree add .worktrees/oca-bank          feat/oca-porting-pipeline
git worktree add .worktrees/oca-queue         feat/oca-porting-pipeline
git worktree add .worktrees/oca-qa            feat/oca-porting-pipeline

# Verify
git worktree list
```

---

## Step 3: Lead Prompt (copy-paste into Claude Code)

```
Enable agent teams for the OCA porting pipeline.

CONTEXT:
- Repo: /Users/tbwa/Documents/GitHub/Insightpulseai/odoo
- Branch: feat/oca-porting-pipeline
- Goal: Port 40 OCA modules from 18.0 → 19.0 in parallel
- Playbook: docs/oca/PORTING_PLAYBOOK.md
- Queue: config/oca/port_queue.yml
- Toolchain: docs/oca/PORTING_TOOLCHAIN.md

Create a team with 5 teammates. Each works in its own worktree to prevent
file conflicts. Assign as follows:

TEAMMATE 1 — server-tools porter
  - Working directory: .worktrees/oca-server-tools
  - Scope: addons/oca/server-tools/
  - Modules: server_environment, web_environment_ribbon
  - Note: server_environment has no deps → port first

TEAMMATE 2 — connector porter
  - Working directory: .worktrees/oca-connector
  - Scope: addons/oca/connector/
  - Modules: component (no deps) → connector (depends on component)
  - Note: must port component before connector

TEAMMATE 3 — bank-statement-import porter
  - Working directory: .worktrees/oca-bank
  - Scope: addons/oca/bank-statement-import/
  - Modules: account_statement_import_base → camt, ofx, file → csv
  - Note: port base first, then leaf modules in parallel

TEAMMATE 4 — queue + server-ux porter
  - Working directory: .worktrees/oca-queue
  - Scope: addons/oca/queue/ + addons/oca/server-ux/
  - Modules: queue_job, base_tier_validation, base_exception, mail_tracking
  - Note: all have no cross-dependencies, can port in any order

TEAMMATE 5 — OCA compliance reviewer (read-only)
  - Working directory: .worktrees/oca-qa
  - Scope: all addons/oca/ paths (read-only review)
  - Role: after each porter commits, review for OCA compliance:
    * __manifest__.py version format (19.0.x.y.z)
    * Python syntax clean (py_compile)
    * No enterprise module deps
    * OCA commit message convention
  - Report violations back to the offending porter via message

QUALITY GATE:
Require plan approval before teammates make any file changes.
Porters must confirm their dependency order before starting.

TASK SIZING:
Create 5-6 tasks per porter, one per module. Mark dependencies using
task blockedBy relationships. Teammates self-claim tasks as they finish.

START: spawn all 5 teammates now. Brief each with the PORTING_PLAYBOOK.md
workflow and their assigned module list.
```

---

## Step 4: Per-Teammate Spawn Context

Each porter gets this context in their spawn prompt (lead generates this automatically
based on the team prompt above, but include it explicitly if needed):

```
You are an OCA porter working on: feat/oca-porting-pipeline

Your working directory: .worktrees/oca-<group>/
Your scope: addons/oca/<repo>/

WORKFLOW (from docs/oca/PORTING_PLAYBOOK.md):
1. Check port_queue.yml for next unblocked module in your scope
2. Run: oca-port <MODULE> --from 18.0 --to 19.0 --repo OCA/<REPO>
3. Smoke test: version check → py_compile → shell load → install
4. Evidence: web/docs/evidence/<TIMESTAMP>/oca-port-<MODULE>/logs/
5. Update port_queue.yml: set status = "completed"
6. Commit: chore(oca): port <MODULE> from 18.0 to 19.0
7. Mark task completed, claim next task

RULES:
- Only edit files under your assigned addons/oca/<repo>/ path
- Never edit config/oca/port_queue.yml while another teammate is editing it
  (coordinate via mailbox message first)
- Claim port_queue.yml updates sequentially — send a message before editing
- Evidence timestamps: Asia/Manila timezone (UTC+08:00)
- Commit convention: chore(oca): port <module> from 18.0 to 19.0

If oca-port fails with "No migration found" → manual port mode:
  clone OCA/<REPO> → update __manifest__.py → fix Python 3.12 compat → copy

Send a message to the QA teammate after each module commit.
Wait for QA approval before marking task complete.
```

---

## Step 5: Task List Structure

The lead creates these tasks at team start:

```
# P0 — server-tools group (Teammate 1)
[T01] port server_environment           → no deps
[T02] port web_environment_ribbon       → blocked by T01

# P0 — connector group (Teammate 2)
[T03] port component                    → no deps
[T04] port connector                    → blocked by T03

# P0 — bank-statement-import (Teammate 3)
[T05] port account_statement_import_base → no deps
[T06] port account_statement_import_camt → blocked by T05
[T07] port account_statement_import_ofx  → blocked by T05
[T08] port account_statement_import_file → blocked by T05
[T09] port account_statement_import_csv  → blocked by T08

# P0 — queue + server-ux (Teammate 4)
[T10] port queue_job                    → no deps
[T11] port base_tier_validation         → no deps
[T12] port base_exception               → no deps
[T13] port mail_tracking                → no deps

# QA reviews (Teammate 5) — auto-triggered by porter messages
[T14] review: server_environment        → blocked by T01
[T15] review: component                 → blocked by T03
[T16] review: account_statement_import_base → blocked by T05
... (one review task per port)
```

---

## Step 6: Hooks (Optional Quality Enforcement)

Add to `.claude/settings.json`:

```json
{
  "hooks": {
    "TaskCompleted": [
      {
        "matcher": "chore(oca): port",
        "hooks": [
          {
            "type": "command",
            "command": "python3 -m py_compile $(git diff HEAD~1 --name-only | grep '\\.py$') && echo 'SYNTAX_OK' || (echo 'SYNTAX_FAIL' && exit 2)"
          }
        ]
      }
    ],
    "TeammateIdle": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "yq '.priorities.P0.modules[] | select(.status == \"pending\") | .name' config/oca/port_queue.yml | head -1 | grep -q . && echo 'MODULES_REMAINING' || echo 'QUEUE_EMPTY'"
          }
        ]
      }
    ]
  }
}
```

---

## Navigation Quick Reference

| Action | Keypress |
|--------|----------|
| Cycle to next teammate | Shift+Down |
| Toggle task list | Ctrl+T |
| Interrupt teammate | Escape |
| Return to lead | Shift+Down (wraps) |

---

## Monitoring Commands (tell the lead)

```
"Show me the task list status"
"How many modules has teammate 3 completed?"
"Ask teammate 2 to wait — component needs a manual fix first"
"Tell all teammates to pause and report current status"
"Ask the QA teammate to run a summary of compliance issues found"
"Clean up the team"  ← only after all tasks complete
```

---

## Conflict Prevention Rules

| Resource | Owner | Access for others |
|----------|-------|-------------------|
| `addons/oca/server-tools/` | Teammate 1 | read-only |
| `addons/oca/connector/` | Teammate 2 | read-only |
| `addons/oca/bank-statement-import/` | Teammate 3 | read-only |
| `addons/oca/queue/` + `server-ux/` | Teammate 4 | read-only |
| `config/oca/port_queue.yml` | Shared — message before editing | |
| `web/docs/evidence/` | Each teammate writes to own timestamp | no conflict |

---

## Expected Throughput

Without Agent Teams: ~1-2 modules/day (sequential)
With Agent Teams (4 porters in parallel): ~6-8 modules/day

P0 completion: ~2 days instead of 7-10 days.

---

## Limitations to Watch For

- `/resume` does NOT restore teammates if session is interrupted → lead must respawn
- `port_queue.yml` edits require coordination (send mailbox message before editing)
- If oca-port fails silently, teammate may mark task complete incorrectly →
  QA reviewer is the catch for this
- One team per session → clean up before starting a new team

---

*Generated: 2026-02-20 | Branch: feat/oca-porting-pipeline*
