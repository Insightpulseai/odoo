# Agent Runtimes — IPAI Stack Catalog

> **Status**: Active | **Effective**: 2026-03-01 | **Owner**: Platform team
>
> This document catalogs all agent runtime frameworks registered in the IPAI stack,
> their surface areas, operational contracts, and governance posture.
>
> SSOT entries: `ssot/integrations/github_copilot_sdk.yaml`,
> `ssot/integrations/microsoft_agent_framework.yaml`

---

## Section 1: Scope

This document covers **agent runtimes** — frameworks and platforms that execute
agentic loops (multi-step, autonomous, or semi-autonomous AI-driven workflows)
within or on behalf of the IPAI Odoo monorepo.

An **agent runtime** in this context is any system that:

- Takes a task as input (natural language, structured spec, or GitHub issue)
- Plans a sequence of steps (decomposition, tool selection)
- Executes those steps against real resources (files, APIs, databases)
- Produces verifiable output (PRs, diffs, evidence artifacts)

**Covered runtimes:**

| Runtime | SSOT File | Status |
|---------|-----------|--------|
| GitHub Copilot SDK + Coding Agent | `ssot/integrations/github_copilot_sdk.yaml` | active (surfaces); planned (Coding Agent) |
| Microsoft Semantic Kernel | `ssot/integrations/microsoft_agent_framework.yaml` | catalog_only |
| Microsoft AutoGen | `ssot/integrations/microsoft_agent_framework.yaml` | catalog_only |

**Out of scope for this document:**

- Claude Code (covered by `~/.claude/CLAUDE.md` + repo `CLAUDE.md`)
- n8n automations (covered by `docs/architecture/N8N_AUTOMATION_CONTRACT.md`)
- Slack agents (covered by `docs/architecture/SLACK_AGENT_CONTRACT.md`)

---

## Section 2: GitHub Copilot SDK

### 2.1 Overview

GitHub Copilot is the primary agentic coding surface for the IPAI stack.
It is deployed across three active surfaces and one planned surface:

| Surface | Auth | Status | Description |
|---------|------|--------|-------------|
| VS Code inline | github_oauth | active | Context-aware completions in editor |
| VS Code Chat | github_oauth | active | Interactive agent in sidebar |
| Copilot CLI | github_oauth | active | `gh copilot explain / suggest` in terminal |
| Coding Agent (autonomous) | github_app | planned | Full agentic loop with PR output |

### 2.2 Agentic Loop (Coding Agent)

When the GitHub Coding Agent is activated, it executes the following loop for
every assigned task:

```
1. PLAN   — Receives task (issue or chat message)
            Reads repo context (.github/copilot-instructions.md, agent-skills/)
            Produces a structured plan (files to modify, test strategy, risk flags)

2. PATCH  — Makes minimal file changes in a sandboxed fork branch
            Reads existing code before writing (never clobbers unknown files)
            Respects SSOT boundary rules from .github/copilot-instructions.md

3. VERIFY — Runs CI gates (lint, typecheck, repo_health.sh, spec_validate.sh)
            Captures gate output as evidence artifacts
            Blocks PR creation if any required gate fails

4. PR     — Opens a PR against the target branch (never pushes to main directly)
            PR body follows the output contract from AGENTIC_CODING_CONTRACT.md
            Evidence section links to captured artifacts from the VERIFY step
```

### 2.3 Repo Contract

The Coding Agent's behavior in this repo is governed by three files:

| File | Purpose |
|------|---------|
| `.github/copilot-instructions.md` | Primary behavior instructions read by the agent on every run |
| `agent-skills/` | Skill definitions (reusable tool wrappers) available to the agent |
| `docs/architecture/AGENTIC_CODING_CONTRACT.md` | The canonical agentic loop contract and rubric reference |

**Invariants enforced by the repo contract:**

- The agent may not modify `ssot/`, `supabase/migrations/`, or `.github/workflows/`
  without an explicit human approval step in PR review.
- Every Coding Agent run must produce an `ops.runs` INSERT before the patch step begins.
- The PR body must include an Evidence section following the output contract.
- The agent must not hardcode secrets or commit `.env` files.

### 2.4 SSOT Reference

Full surface catalog, risk flags, and governance posture:
`ssot/integrations/github_copilot_sdk.yaml`

---

## Section 3: Microsoft Agent Framework

### 3.1 Semantic Kernel

**Status**: `catalog_only` — registered as architecture reference, no production deployment.

Semantic Kernel (SK) is Microsoft's model-agnostic skill composition framework.
It allows LLM planners to sequence typed functions (skills/plugins) into executable
pipelines. SK supports Python, C#, and Java.

**Relevance to IPAI:**

SK is registered as the preferred orchestration layer for multi-step agentic
workflows that span multiple service boundaries (Copilot → Odoo RPC → Supabase → n8n).
When activated, SK orchestration config will live in `agents/semantic-kernel/`.

**Key concepts:**

| Concept | Description |
|---------|-------------|
| Kernel | Container that holds LLM connectors, plugins, and memory |
| Plugin | A collection of typed functions (native code or prompt templates) |
| Planner | Auto-sequencer that converts a user goal into a plugin call sequence |
| Memory | Vector or key-value store for agent context persistence |

**Planned plugin surface:**

- `OdooRpcPlugin` — reads Odoo models via JSON-RPC (read-only)
- `SupabaseQueryPlugin` — reads from Supabase via REST API (read-only)
- `N8nTriggerPlugin` — triggers n8n webhooks for automation workflows
- `OpsRunsPlugin` — inserts/updates `ops.runs` and `ops.run_events` rows

**Activation path:**

1. Open implementation PR setting SK status to `porting`
2. Add `agents/semantic-kernel/kernel_config.py` with plugin allowlist
3. Add `ops.run_events` logging hook to each plugin execution
4. All gates pass in CI
5. Update SSOT entry status to `active`

### 3.2 AutoGen

**Status**: `catalog_only` — registered as architecture reference, no production deployment.

AutoGen is Microsoft Research's multi-agent conversation framework. Agents
(AssistantAgent, UserProxyAgent, GroupChatManager) exchange messages to complete
tasks collaboratively via a typed conversation API (AgentChat v0.4+).

**Relevance to IPAI:**

AutoGen is the reference pattern for orchestrating multiple specialized domain
agents (finance_ssc_agent, devops_agent, odoo_developer_agent) in a supervised
group chat with a human-in-the-loop approval gate.

**Activation criteria:**

AutoGen is not activated until:
- Copilot Coding Agent is GA and live on this repo (PR gate enforced)
- At least two specialized agent roles are implemented in `agents/autogen/`
- ops.run_events logging is wired into the GroupChatManager step transitions

### 3.3 SSOT Reference

Full component catalog, risk flags, and posture:
`ssot/integrations/microsoft_agent_framework.yaml`

---

## Section 4: IPAI Agentic Loop

This section defines the canonical agentic loop that all agent runtimes in the
IPAI stack must follow, regardless of which framework executes it.

### 4.1 Loop Phases

```
╔══════════════════════════════════════════════════════════════╗
║  PLAN                                                        ║
║  ├── Create ops.runs entry (status: running)                 ║
║  ├── Read task input (issue, spec bundle, or chat message)   ║
║  ├── Identify impacted files and spec references             ║
║  ├── Produce structured plan (files, test strategy, risks)   ║
║  └── Attach plan to ops.runs.plan_artifact                   ║
╠══════════════════════════════════════════════════════════════╣
║  PATCH                                                       ║
║  ├── Read each target file before writing                    ║
║  ├── Apply minimal diff (only required changes)              ║
║  ├── No changes to ssot/, migrations/, workflows/ without    ║
║  │   explicit approval flag in task input                    ║
║  └── Record ops.run_events: step=patch, outcome=applied      ║
╠══════════════════════════════════════════════════════════════╣
║  VERIFY                                                      ║
║  ├── scripts/repo_health.sh                                  ║
║  ├── scripts/spec_validate.sh (if spec bundle referenced)    ║
║  ├── pnpm lint + typecheck (JS/TS targets)                   ║
║  ├── python -m flake8 (Python targets)                       ║
║  ├── Capture gate output to docs/evidence/<stamp>/           ║
║  └── Record ops.run_events: step=verify, outcome=pass|fail   ║
║       BLOCK PR creation on any gate failure                  ║
╠══════════════════════════════════════════════════════════════╣
║  PR                                                          ║
║  ├── Open PR on feature branch (never push to main)          ║
║  ├── PR body follows output contract (CONTEXT, CHANGES,      ║
║  │   EVIDENCE, DIFF SUMMARY sections)                        ║
║  ├── Attach evidence_path to ops.runs entry                  ║
║  └── Update ops.runs status: completed (or failed)           ║
╚══════════════════════════════════════════════════════════════╝
```

### 4.2 Loop Invariants

These invariants apply to every agent runtime and every agentic run:

1. **ops.runs entry before patch** — The run must be logged before any file is modified.
2. **PR required for all code changes** — No direct commits to main/master. Ever.
3. **Verify before PR** — CI gates must pass before the PR is opened.
4. **Evidence attached to ops.runs** — `evidence_path` must be populated in the ops.runs row.
5. **No secrets in diffs** — Agent-generated patches are scanned for secret patterns before PR.
6. **Minimal patch** — Only files required for the task are modified. Unrelated changes block merge.

### 4.3 ops.runs Schema

Each agentic run produces one row in `ops.runs` and one or more rows in `ops.run_events`:

```sql
-- ops.runs (one per agentic run)
INSERT INTO ops.runs (
    task_id,          -- Plane issue ID or GitHub issue number
    agent_id,         -- 'copilot_coding_agent' | 'semantic_kernel' | 'autogen'
    triggered_by,     -- GitHub actor or agent identifier
    status,           -- 'running' | 'completed' | 'failed'
    plan_artifact,    -- Path to structured plan document
    evidence_path,    -- Path to docs/evidence/<stamp>/ bundle
    pr_url            -- URL of the opened PR (null until PR step)
) VALUES (...);

-- ops.run_events (one per step transition)
INSERT INTO ops.run_events (
    run_id,     -- FK to ops.runs.id
    step,       -- 'plan' | 'patch' | 'verify' | 'pr'
    outcome,    -- 'started' | 'completed' | 'failed'
    detail      -- JSON: gate names, file counts, error messages
) VALUES (...);
```

---

## Section 5: Governance

### 5.1 SSOT Registration

Every agent runtime used in production must have:

1. A SSOT entry in `ssot/integrations/<runtime>.yaml`
2. A status of `active` (not `planned` or `catalog_only`)
3. An ops.runs logging hook wired into the agentic loop
4. PR evidence following the output contract

**To register a new runtime:**

1. Create `ssot/integrations/<runtime>.yaml` following the `ssot.integrations.v1` schema
2. Add a row to the References table at the bottom of this document
3. If the runtime triggers code changes: add it to `ssot/advisor/rubrics/agentic_coding.yaml`
   `audit_trail.levels` as a recognized `agent_id` value
4. Open a PR and get CODEOWNERS approval for `ssot/`

### 5.2 ops.runs Audit

The Ops Console (`apps/ops-console/`) surfaces `ops.runs` entries for each
agentic run. Operators can:

- Filter by `agent_id` to see all Coding Agent runs
- Navigate to `evidence_path` to inspect gate output
- Open the linked `pr_url` to review the code change
- Score the run against the agentic_coding rubric

Runs without an `ops.runs` entry are **governance violations** and must be
retroactively documented or the corresponding PRs must be reverted.

### 5.3 PR Evidence Requirement

Every PR opened by an agent runtime must include the following sections in the
PR body (per the output contract in `CLAUDE.md` and `AGENTIC_CODING_CONTRACT.md`):

```
**[CONTEXT]**      — repo, branch, cwd, goal, timestamp
**[CHANGES]**      — file: intent pairs
**[EVIDENCE]**     — command: result: pass/fail lines
**[DIFF SUMMARY]** — file: why it changed
```

PRs missing any of these sections should be flagged by reviewers and the
agentic coding rubric dimension `pr_evidence` will score 0 for that run.

### 5.4 Restricted Paths

The following paths require explicit human approval before any agent runtime
may modify them, regardless of the task input:

| Path | Reason |
|------|--------|
| `ssot/` | SSOT mutation has platform-wide effects |
| `supabase/migrations/` | Schema changes are irreversible in production |
| `.github/workflows/` | CI changes could disable safety gates |
| `infra/` | Infrastructure changes affect production availability |
| `.github/copilot-instructions.md` | Agent behavior SSOT — self-modification risk |

---

## Section 6: Roadmap

| Milestone | Target | Owner |
|-----------|--------|-------|
| GitHub Copilot Coding Agent GA activation | After Copilot Business license confirmed | Platform |
| Wire ops.runs logging into Copilot Coding Agent runs | Same sprint as Coding Agent activation | Platform |
| Semantic Kernel implementation PR | Following quarter after Coding Agent is stable | Platform |
| AutoGen multi-agent orchestration | H2 2026 (pending Coding Agent maturity assessment) | Platform |
| Automated rubric scoring in Ops Console | Concurrent with SK implementation | BI |

**Blocking dependencies for Coding Agent activation:**

1. Copilot Business or Enterprise license provisioned for the Insightpulseai org
2. `github_governance` rulepack org_rulesets_default_branch check: PASS
3. `.github/copilot-instructions.md` created and CODEOWNERS entry added
4. `ops.runs` table present in Supabase with the schema in Section 4.3
5. SSOT entry `ssot/integrations/github_copilot_sdk.yaml` status updated to reflect
   `coding_agent.status: active`

---

## References

| Resource | Path / URL |
|----------|-----------|
| GitHub Copilot SDK SSOT | `ssot/integrations/github_copilot_sdk.yaml` |
| Microsoft Agent Framework SSOT | `ssot/integrations/microsoft_agent_framework.yaml` |
| Agentic Coding Contract | `docs/architecture/AGENTIC_CODING_CONTRACT.md` |
| Agentic Coding Rubric | `ssot/advisor/rubrics/agentic_coding.yaml` |
| Baseline Workbook | `ssot/advisor/workbooks/agentic_coding_baseline.yaml` |
| GitHub Governance Rulepack | `ssot/advisor/rulepacks/github_governance.yaml` |
| Ops Advisor Contract | `docs/architecture/OPS_ADVISOR_CONTRACT.md` |
| GitHub Copilot Coding Agent docs | https://docs.github.com/copilot/using-github-copilot/using-copilot-coding-agent |
| Semantic Kernel overview | https://learn.microsoft.com/semantic-kernel/overview/ |
| AutoGen documentation | https://microsoft.github.io/autogen/ |
| GitHub Well-Architected — Governance | https://wellarchitected.github.com/library/governance/ |
