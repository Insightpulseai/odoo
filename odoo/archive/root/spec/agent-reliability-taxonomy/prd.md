# PRD — Agent Reliability Taxonomy (Errors, Failure Modes, Troubleshooting, Smol Training)

## Overview
IPAI's platform uses multiple agent runners (Claude Code, Codex, etc.) and multiple execution surfaces
(GitHub Actions, Supabase Edge Functions, Vercel, Odoo). To prevent "agent chaos," we standardize how
failures are represented, classified, resolved, and improved over time.

## Goals
1. A single **error envelope** and consistent **error code taxonomy** across services.
2. A single **failure mode registry** with runbook linkage and escalation rules.
3. A deterministic **agent troubleshooting guide** usable by humans and agents.
4. A measurable agent performance improvement system:
   - benchmark suite + scoring
   - controlled ablations
   - preference optimization (DPO/GRPO-like) using ops outcomes

## Non-goals
- Replacing existing CI frameworks.
- Rewriting all existing systems at once.
- Building an LLM training cluster orchestration system.

## Users
- Platform Engineers (operate, converge, deploy)
- Agent Runners (Claude/Codex/GHA bots)
- Compliance/Finance (audit trail)
- Project Owners (want resolution + prevention)

## Functional Requirements

### FR1 — Standard error envelope (HTTP boundary)
All HTTP endpoints must return a single JSON error format on failure (Problem Details–style with `ipai.code`
extensions). Must include: `type`, `title`, `status`, `detail`, `instance`, and `ipai` extension payload.

### FR2 — Error code taxonomy (stable, versioned)
Define `ipai.code` string format, naming conventions, and a canonical registry.
Support hierarchical dot-separated codes, e.g. `CI.CACHE.PATH_MISSING`.

### FR3 — Failure mode registry (SSOT)
Maintain `ssot/errors/failure_modes.yaml`:
- `code`, `category`, `severity`, `retryable`
- detection patterns (sources + substrings/regex)
- runbook path
- remediation type (checklist/fixbot/guardrail)
- escalation rule (count/time thresholds)

### FR4 — Agent error logging (deduped)
Every agent execution layer must upsert errors into `ops.agent_errors`:
- dedupe by fingerprint
- increment count on repeats
- link to `run_id`, `work_item_ref`, artifacts, and failure_mode code

### FR5 — Troubleshooting guide (agent-ready)
Provide runbook templates and top initial runbooks for the top failure modes.
Provide a top-level troubleshooting guide: classification → evidence → remediation → verification → closure.

### FR6 — Resolution documentation
Every resolved incident produces a resolution record linked to:
- `run_id`, error fingerprint / `error_id`
- artifact URLs, PR link (if any)
- prevention updates (guardrails/runbook changes)

### FR7 — Auto-escalation + recurrence handling
Repeated failures must trigger escalation per SSOT thresholds:
- Slack alert / work item / merge block (for critical cases like placeholders).

### FR8 — Benchmark scoring for agent performance
Define `ssot/agents/benchmark.yaml` for:
- task categories, scoring weights
- thresholds per maturity tier (baseline/established/optimized)
Store results in `ops.agent_benchmark_results`.

### FR9 — Smol Training Playbook adoption for agent improvement
- Define controlled ablation framework for agent prompt/policy/tool variants.
- Define preference optimization dataset generation from ops outcomes:
  (prompt/context/patch) paired with (better/worse) outcomes.
- Define evaluation harness aligned to IPAI benchmarks (not generic CoT).

## Acceptance Criteria
- A known failure (e.g., missing Vercel env var) is:
  1. logged into `ops.agent_errors` with `code=ENV.KEY_MISSING`
  2. linked to the correct runbook
  3. produces a resolution record after fix
  4. appears in benchmark results as a failure mode hit
- At least 12 initial failure modes are registered with runbooks.
- At least one benchmark run produces a scorecard per agent type.
- At least one ablation variant is measurable via benchmark results.
