# Runbook: AGENT.BENCHMARK_SCORE_BELOW_THRESHOLD

**Severity**: Medium
**HTTP Status**: 200 (run recorded, flagged)
**Retryable**: No (fix agent, then re-run)

## Symptoms

A benchmark run scored below the minimum tier B (75/100).

```json
{
  "run_id": "<uuid>",
  "skill_id": "pulser-patch",
  "composite_score": 58.2,
  "tier": "C",
  "breakdown": {
    "evidence_compliance": 0.45,
    "diff_minimality": 0.90,
    "ci_pass_rate": 0.75,
    "time_to_green_s": 0.80
  }
}
```

## Root Causes (by metric)

| Low metric | Likely cause |
|-----------|--------------|
| `evidence_compliance` | Agent not writing `detail` JSONB to run_events |
| `diff_minimality` | Diff too large (see AGENT.PATCH_DIFF_TOO_LARGE) |
| `ci_pass_rate` | Repeated CI failures (see AGENT.VERIFY_CI_FAIL) |
| `time_to_green_s` | Slow sandbox / DO runner, or excessive retries |

## Remediation

```bash
# 1. View full benchmark history for this skill
SELECT skill_id, composite_score, tier, created_at
FROM ops.agent_benchmark_results
WHERE skill_id = '<skill_id>'
ORDER BY created_at DESC LIMIT 10;

# 2. Identify the lowest metric and fix the root cause
# See metric-specific runbooks above

# 3. After fixing, trigger a new benchmark run
gh workflow run benchmark-runner.yml \
  --repo Insightpulseai/odoo \
  -f skill_id=<skill_id>

# 4. Three consecutive B+ runs are required for auto-promote
```

## Prevention

Block skill promotions to `active` status until ≥ 3 benchmark runs
with tier ≥ B are recorded in `ops.agent_benchmark_results`.
See `ssot/agents/benchmark.yaml` for threshold config.
