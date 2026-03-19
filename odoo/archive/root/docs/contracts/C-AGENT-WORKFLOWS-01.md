# C-AGENT-WORKFLOWS-01 — Agent Workflow Interface Contract

**Contract ID**: C-AGENT-WORKFLOWS-01
**Status**: ✅ Active
**Source SSOT**: `ssot/agents/interface_schema.yaml`
**Consumer**: All IPAI agent skills (`ssot/agents/skills.yaml`), executor runtimes
**Validator**: `scripts/ci/validate_skills_registry.py` (via `agent-skills-gate.yml`)
**Last updated**: 2026-03-02

---

## Purpose

This contract defines the required shape of every agent skill entry and the lifecycle
protocol that agent executors must follow when running a skill.

It ensures that:

- Every skill has a typed tool permission list and a security block.
- Every run produces an auditable ops.runs row before any side effect.
- Phase transitions are durable (checkpoint columns in ops.runs).
- Distributed traces are correlatable via trace_id/span_id on ops.run_events.

---

## Skill Entry Schema

Every entry in `ssot/agents/skills.yaml` must conform to the schema defined in
[`ssot/agents/interface_schema.yaml`](../../ssot/agents/interface_schema.yaml).

### Required fields

| Field | Type | Constraints |
|-------|------|-------------|
| `id` | string | kebab-case, unique, matches `^[a-z][a-z0-9-]+$` |
| `name` | string | non-empty display name |
| `description` | string | 1–2 sentences |
| `executor` | enum | `vercel_sandbox` \| `do_runner` \| `supabase_edge_fn` |
| `max_duration_s` | integer | 1–3600; executor returns 504 on breach |
| `tags` | list | free-form strings |
| `state_machine` | list | ordered subsequence of `[PLAN, PATCH, VERIFY, PR, MONITOR]` |
| `owner` | string | team or GitHub handle |
| `status` | enum | `active` \| `experimental` \| `deprecated` |
| `allowed_tools` | list | tool IDs from `ssot/tools/registry.yaml`; `["__none__"]` for read-only skills |
| `security` | mapping | see security block below |

### Security block (required sub-fields)

```yaml
security:
  path_traversal_guard: true   # block "../" and absolute paths outside allowed prefixes
  symlink_guard: true          # resolve symlinks and re-validate resolved path
  metadata_escaping: true      # escape jsonb values written to ops.run_events
  max_skill_body_bytes: 5000   # hard limit per repo_write_file call
```

All four fields are required. Omitting any field causes CI to fail with:

```
skills[N].security.<field>: required field missing (see ssot/agents/interface_schema.yaml for defaults)
```

---

## Run Lifecycle Protocol

Every skill execution must follow this protocol, regardless of executor surface:

### 1. Pre-run (PLAN phase entry)

```
ops_start_run(run_id=<new UUID>, agent_kind=<skill_id>, triggered_by=<source>, started_at=<UTC>)
```

This is the **evidence-first invariant**: no side effect may occur before ops.runs has a row.

### 2. Phase transitions

On completing each phase, the executor must:

```
ops_log_event(run_id, level="info", message="phase <NAME> complete",
              data={phase: <NAME>, trace_id: <UUID>, span_id: <UUID>})
ops.runs.last_phase = <NAME>
ops.runs.checkpoint_at = <UTC now>
```

`trace_id` and `span_id` propagate W3C trace context from the triggering HTTP request.
Both may be null if the executor does not implement OTel context propagation.

### 3. Success

```
ops_complete_run(run_id, last_phase=<final phase>, checkpoint_at=<UTC>)
```

### 4. Failure

```
ops_fail_run(run_id, output={error: <sanitized message>})
```

Error message must not contain secret values (tokens, keys, passwords).

### 5. PR gate (for skills with PR phase)

Skills that include `PR` in their `state_machine` must call `github_open_pr` in the PR
phase and must never push directly to the main branch.  This is enforced by
[`ssot/agents/prod_policy.yaml`](../../ssot/agents/prod_policy.yaml)
`forbidden_actions.push_to_main_branch`.

---

## Phase Order Constraint

State machine phases must appear in this canonical order:

```
PLAN → PATCH → VERIFY → PR → MONITOR
```

Re-entering a phase within a single run is not permitted. The validator enforces that
`state_machine` is a strictly-ordered subsequence of the canonical order.

---

## Durable Checkpoints

Migrations `supabase/migrations/20260302002000_ops_runs_phase_checkpoint.sql` and
`supabase/migrations/20260302002001_ops_run_events_tracing.sql` add:

| Column | Table | Purpose |
|--------|-------|---------|
| `last_phase VARCHAR(64)` | `ops.runs` | Most recently completed phase |
| `checkpoint_at TIMESTAMPTZ` | `ops.runs` | UTC timestamp of last checkpoint write |
| `trace_id UUID` | `ops.run_events` | W3C trace-id for distributed tracing |
| `span_id UUID` | `ops.run_events` | W3C span-id for phase-level latency |

These columns enable:

- **Stale run detection**: `checkpoint_at < NOW() - INTERVAL '30 minutes'` with status=running
- **Phase replay**: resume a partially-completed run from `last_phase` after a transient failure
- **Cross-service trace correlation**: join `ops.run_events.trace_id` with external OTel collectors

---

## Relationship to Microsoft Agent Framework

This contract introduces IPAI equivalents of MAF Durable Task Scheduler checkpoints
(see [Microsoft Learn — Agent Framework: Durable Task](https://learn.microsoft.com/en-us/azure/ai-services/agents/how-to/agent-framework-overview)):

| MAF concept | IPAI equivalent |
|-------------|----------------|
| Durable Task superstep | `ops.runs.last_phase` + `checkpoint_at` |
| OTel span propagation | `ops.run_events.trace_id` + `span_id` |
| Tool approval gate | `slack_post_approval_request` + `requires_human_approval: true` |
| Skill progressive disclosure | `ssot/tools/registry.yaml` `allowed_in_skills` per-skill allowlist |

---

## Invariants

1. **Evidence-first**: `ops_start_run` must be the first action of every skill run.
2. **Append-only ops tables**: agents INSERT but never UPDATE/DELETE ops.* rows, except via the defined RPC helpers (`ops_complete_run`, `ops_fail_run`).
3. **No push to main**: skills with a PR phase must use `github_open_pr`; `push_to_main_branch` is globally forbidden.
4. **Sanitized error output**: `ops_fail_run` output must not expose secrets.
5. **Checkpoint write**: executors must update `last_phase` and `checkpoint_at` on every phase transition.

---

## Adding a New Phase

1. Add the new phase name to `valid_phases` in [`ssot/agents/interface_schema.yaml`](../../ssot/agents/interface_schema.yaml).
2. Add it to `phase_order_canonical` in the same file.
3. Update `VALID_STATES` in [`scripts/ci/validate_skills_registry.py`](../../scripts/ci/validate_skills_registry.py).
4. Update any affected skills' `state_machine` list.
5. Open a PR — CI gate must pass before merge.

---

## References

- Schema: [`ssot/agents/interface_schema.yaml`](../../ssot/agents/interface_schema.yaml)
- Skills: [`ssot/agents/skills.yaml`](../../ssot/agents/skills.yaml)
- Policy: [`ssot/agents/prod_policy.yaml`](../../ssot/agents/prod_policy.yaml)
- Tools: [`ssot/tools/registry.yaml`](../../ssot/tools/registry.yaml)
- Migrations: [`supabase/migrations/20260302002000_ops_runs_phase_checkpoint.sql`](../../supabase/migrations/20260302002000_ops_runs_phase_checkpoint.sql)
- Migrations: [`supabase/migrations/20260302002001_ops_run_events_tracing.sql`](../../supabase/migrations/20260302002001_ops_run_events_tracing.sql)
- Validator: [`scripts/ci/validate_skills_registry.py`](../../scripts/ci/validate_skills_registry.py)
- CI gate: [`.github/workflows/agent-skills-gate.yml`](../../.github/workflows/agent-skills-gate.yml)
