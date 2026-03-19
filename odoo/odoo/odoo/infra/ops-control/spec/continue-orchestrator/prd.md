# spec/continue-orchestrator/prd.md

## Summary
Continue Orchestrator is an improved "control plane" for Continue that upgrades automation from "agent runs" to **governed, replayable, provable changes** across IDE, terminal, and CI.

It preserves:
- Mission Control Tasks/Workflows/Integrations
- CLI TUI + headless modes
- Config-driven agents (`config.yaml`)
- Secrets management model

…and adds:
- Policy-as-code gates
- Run Ledger (audit + replay)
- Deterministic tool sandboxing
- Evidence-first PRs
- Cost/latency controls + run budgets

## Problem
Continue already automates coding tasks via agents and workflows (cron/webhooks) that can create PRs, react to Sentry/Snyk, etc.  
But teams hit blockers at scale:
1. **Unclear provenance**: Why did the agent change X? What tools/data did it use?
2. **Hard-to-audit automation**: Workflows run across repos; failures/spikes visible, but the "why" and "what exactly happened" are fragmented.
3. **Inconsistent guardrails**: Configs define behavior, but org-wide constraints (what can be touched, when approval is required) are not a first-class artifact.
4. **Non-replayable results**: Same prompt/config can yield different tool calls/results depending on timing, tool state, and model variance.
5. **Risky write actions**: Automated PRs/patches are valuable but need stronger "write fences" and evidence requirements.

## Goals
- Make agent work **provable** (audit trail) and **repeatable** (replay).
- Make automation **safe by construction** (policy).
- Make PRs **merge-ready** (evidence bundle + tests).
- Keep UX the same for day-to-day users (IDE/CLI/Mission Control).

## Personas
1. **Individual dev**: Wants fast fixes and refactors in IDE/CLI.
2. **Team lead**: Wants standardized configs and predictable agent behavior.
3. **Platform/DevOps**: Wants CI automation with budgets, logs, and compliance.
4. **Security/Compliance**: Wants least-privilege, auditability, and approval gates.

## Key concepts
### 1) Policy Packs
A versioned, repo/org-scoped policy file:
- allowed repos/branches
- allowed file globs
- allowed MCP tools + endpoints
- approval thresholds (auto/required)
- max run budgets (tokens, tool calls, minutes)

### 2) Run Ledger (append-only)
Every run stores:
- config hash (config.yaml + referenced blocks)
- policy hash
- inputs (prompt, trigger context, event payload)
- tool calls + sanitized outputs
- diffs/patches
- tests executed + logs
- PR link + status
- replay token (to re-run deterministically)

### 3) Deterministic Execution Mode
Optional "deterministic" run:
- tool calls recorded + re-used during replay
- model sampling pinned
- time/network nondeterminism isolated via "tool adapters"

### 4) Evidence-first PRs
Every agent-created PR must include:
- changelog/summary
- reproduction instructions
- test results (unit + lint at minimum)
- provenance block (run id, hashes)

## Functional requirements
### FR1 — Policy authoring & evaluation
- Support org and repo policies (inheritance + overrides).
- Policies evaluated on:
  - run start (can it run?)
  - tool invocation (can it call this tool with these args?)
  - write actions (can it commit/push/open PR?)

### FR2 — Run Ledger API + UI
- Mission Control: per-run "Ledger" tab with:
  - timeline of decisions/tool calls
  - artifact downloads (patch, logs)
  - replay button
- CLI: `cn ledger show <run>` and `cn replay <run>`.

### FR3 — Budgeting
- Enforce max:
  - runtime
  - model tokens
  - tool invocations
  - PR attempts
- Budget overruns => stop + emit actionable failure reason.

### FR4 — PR evidence enforcement
- Agent cannot open PR unless:
  - minimal test suite ran
  - provenance summary attached
  - policy allows write actions

### FR5 — Integration-safe triggers
- For existing Workflows (cron/webhooks), Orchestrator injects policy + ledger automatically.
- For integrations (GitHub, Sentry, Snyk, Slack, etc.), Orchestrator records event payloads to ledger.

### FR6 — Secrets handling (no regressions)
- Continue's secret patterns remain: `${{ secrets.SECRET_NAME }}`.
- Ledger stores only secret references, never secret values.

## Non-functional requirements
- **Reliability**: clear failure modes and retry semantics.
- **Latency**: policy checks must be sub-50ms locally, sub-200ms remote.
- **Observability**: extend existing metrics with "policy denials", "budget stops".
- **Compatibility**: works with current config.yaml spec and blocks.

## UX requirements
- Mission Control:
  - Add "Policies" and "Ledger" sections (adjacent to Metrics/Sharing).
  - Per-agent "Required Evidence" toggle (default on for orgs).
- CLI:
  - `cn run ...` gains `--policy <pack>` and `--deterministic`.

## Success metrics
- ≥30% reduction in "agent PR reverted" rate
- ≥25% reduction in manual interventions per run (tracked in metrics)
- ≥90% of agent PRs include passing CI at open time
- Mean time-to-audit (find cause/tool) < 2 minutes

## Risks
- Policy complexity sprawl → mitigate with templates + linting.
- Determinism limits: external tools are inherently variable → mitigate via tool adapters and "record/replay".

## Rollout
- Phase 1: Ledger + evidence PR templates (no policy enforcement).
- Phase 2: Soft policies (warn-only).
- Phase 3: Hard policies (block).
- Phase 4: Deterministic replay for supported tools.

## Pulser SDK (required)
- Provide a `pulser/` adapter so Pulser agents can:
  - trigger Continue runs
  - read Ledger artifacts
  - enforce org policies in multi-agent orchestrations
- Publish a minimal `pulser-sdk` integration guide + example workflow.

## Out of scope (explicit)
- Building new IDE UI from scratch
- Replacing Continue Hub/Mission Control sharing model
