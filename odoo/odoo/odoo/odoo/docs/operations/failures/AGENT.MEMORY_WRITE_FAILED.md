# Runbook: AGENT.MEMORY_WRITE_FAILED

**Severity**: Medium
**HTTP Status**: 200 (run continues)
**Retryable**: Yes

## Symptoms

The agent could not write to `ops.memory_entries` via `ops-memory-write`.

```json
{
  "run_id": "<uuid>",
  "step": "PLAN",
  "outcome": "partial",
  "detail": { "memory_error": "AGENT.MEMORY_WRITE_FAILED", "key": "plan_output" }
}
```

## Root Causes

1. `ops-memory-write` Edge Function is not deployed.
2. The JWT passed by the agent is expired.
3. Rate limit hit (100 writes/min per user).
4. The `ops.memory_entries` table migration has not been applied yet.

## Remediation

```bash
# 1. Check Edge Function status
supabase functions list

# 2. Deploy if missing
supabase functions deploy ops-memory-write

# 3. Test with a manual write
curl -X POST "$SUPABASE_URL/functions/v1/ops-memory-write" \
  -H "Authorization: Bearer $USER_JWT" \
  -H "Content-Type: application/json" \
  -d '{"scope":"run","run_id":"test-run","key":"test","value":{"ping":true}}'

# 4. Check if migration applied
SELECT COUNT(*) FROM ops.memory_entries;

# 5. If table missing, run migration
supabase db push
```

## Prevention

The run continues despite memory failures (non-blocking by design).
Add a health-check step at run start that verifies `ops-memory-write`
is reachable before beginning PLAN.
