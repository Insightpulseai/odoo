# Runbook: AGENT.STATE_MACHINE_SKIP

**Severity**: Critical
**HTTP Status**: 422
**Retryable**: No

## Symptoms

An agent attempted a state transition that violates the declared
`state_machine` order for the skill.

```
{
  "error": "AGENT.STATE_MACHINE_SKIP",
  "attempted": "PATCH",
  "expected_next": "PLAN",
  "run_id": "<uuid>"
}
```

## Root Causes

1. Agent implementation called `logRunEvent(step: "PATCH")` before `logRunEvent(step: "PLAN")`.
2. A retry resumed from the wrong state after a crash.
3. The skill's `state_machine` array in `ssot/agents/skills.yaml` was updated
   but the agent implementation was not updated to match.

## Remediation

```bash
# 1. Find the run and its current events
SELECT step, outcome, created_at
FROM ops.run_events
WHERE run_id = '<run_id>'
ORDER BY created_at;

# 2. Determine the last successful state
# The agent must be restarted from PLAN

# 3. If the run is stuck, cancel it
UPDATE ops.runs SET status = 'cancelled' WHERE id = '<run_id>';

# 4. Restart the run from PLAN
# Trigger a new invocation of the skill

# 5. Fix the agent code to respect state order
# See spec/deerflow-patterns-adoption/prd.md FR-3
```

## Prevention

The Edge Function validates state transitions against `ops.skills.state_machine`
on every `run_event` insert.  Agent unit tests should include a state-order test.
