# Runbook: AGENT.PLAN_EMPTY

**Severity**: High
**HTTP Status**: 200 (run recorded, not errored)
**Retryable**: Yes

## Symptoms

The PLAN phase completed without producing actionable steps.  The run
status is set to `completed` with outcome `no_plan`.

```json
{
  "run_id": "<uuid>",
  "status": "completed",
  "output": { "plan_items": 0, "failure_mode": "AGENT.PLAN_EMPTY" }
}
```

## Root Causes

1. The input issue/spec has no parseable requirements (vague title, no body).
2. The LLM call returned an empty structured response.
3. The issue was already resolved; no diff needed.

## Remediation

```bash
# 1. Check the input that was provided
SELECT input FROM ops.runs WHERE id = '<run_id>';

# 2. Check if the issue body is populated on GitHub
gh issue view <issue_number> --repo Insightpulseai/odoo

# 3. If the issue is vague, add a description and re-trigger the skill
# 4. If it was already resolved, close the issue and mark run as expected
UPDATE ops.runs SET metadata = metadata || '{"expected_empty_plan": true}'
WHERE id = '<run_id>';
```

## Prevention

Validate issue body length (≥ 50 chars) before dispatching pulser-patch.
Add a pre-flight check in the skill's PLAN phase that returns early with a
clear error if input requirements are below the quality threshold.
