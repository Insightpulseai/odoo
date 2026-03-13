# PRD — DeerFlow Patterns Adoption
## spec/deerflow-patterns-adoption · v1.0 · 2026-03-02

---

## Problem Statement

IPAI agents (Pulser, FixBot, OpsAdvisor) each have ad-hoc execution models:
different error codes, no shared memory, non-deterministic retry logic, no
benchmark scoring.  ByteDance deer-flow proves that a **skills registry +
sandboxed executor + structured state machine** is the right abstraction for
agentic DevOps.  We adopt those patterns with our own persistence (Supabase).

---

## Functional Requirements

### FR-1 Skills Registry
- A YAML SSOT (`ssot/agents/skills.yaml`) declares every skill with: id, name,
  description, executor (vercel_sandbox | do_runner), max_duration_s, tags.
- CI validator (`scripts/ci/validate_skills_registry.py`) enforces schema and
  blocks PRs that introduce undeclared skills.
- Supabase table `ops.skills` mirrors YAML on every merge to main via a
  dedicated GitHub Action.

### FR-2 Universal Run Envelope
- Every agent invocation writes to `ops.runs` (kind = 'agent') with a unique
  `run_id`; transitions log to `ops.run_events`.
- `ops.skills` foreign key on `ops.runs.skill_id` enforces that only declared
  skills can produce runs.

### FR-3 Structured State Machine
- Four mandatory states: `PLAN` → `PATCH` → `VERIFY` → `PR`.
- Each state transition is logged as a `run_event` with `step` = state name.
- Agents that skip a state are rejected by the Edge Function (HTTP 422).

### FR-4 Memory Plane
- `ops.memory_entries` table: columns `scope` (run | project | org),
  `key TEXT`, `value JSONB`, `run_id UUID?`, `project TEXT?`.
- Edge Function `ops-memory-write` (authenticated; rate-limited to 100 writes/min).
- Edge Function `ops-memory-read` (authenticated; keyed lookup + prefix scan).

### FR-5 Error Taxonomy
- `ssot/errors/failure_modes.yaml` defines ≥ 12 failure codes for initial
  rollout; each code maps to a runbook at `docs/runbooks/failures/<CODE>.md`.
- `ops.agent_errors` table deduplicates by `fingerprint`; stores `failure_mode`
  foreign key so dashboards can aggregate by code.

### FR-6 Benchmark Engine
- `ssot/agents/benchmark.yaml` declares tier thresholds (A/B/C/F) and weights
  for: evidence_compliance, diff_minimality, ci_pass_rate, time_to_green_s.
- `ops.agent_benchmark_results` stores per-run scores.
- GitHub Action runs benchmark suite on merge to main for skills that changed.

---

## Non-Functional Requirements

| NFR | Target |
|-----|--------|
| p95 memory read latency | < 50 ms |
| Benchmark suite run time | < 5 min |
| Skills CI validator | < 10 s |
| Zero new external dependencies | No new npm/pip packages not already in workspace |

---

## Success Criteria

1. `ops.skills`, `ops.memory_entries`, `ops.agent_errors`, `ops.agent_benchmark_results` tables migrate cleanly on `supabase db push`.
2. CI validator blocks a PR with an undeclared skill within 30 seconds.
3. Pulser's next invocation writes a run with `skill_id` → `ops.runs`.
4. All 12 failure codes have runbooks linked from `ssot/errors/failure_modes.yaml`.
5. At least one benchmark run recorded in `ops.agent_benchmark_results`.
