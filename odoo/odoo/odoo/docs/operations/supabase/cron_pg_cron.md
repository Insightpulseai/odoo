# Runbook: pg_cron Job Not Running

**Canonical source:** https://supabase.com/docs/guides/troubleshooting/pgcron-debugging-guide-n1KTaz

---

## Error signatures

- Job shows as scheduled in `cron.job` but never executes
- No rows in `cron.job_run_details` for expected runs
- Job ran successfully once then stopped
- Status = `failed` in `cron.job_run_details`

---

## Likely causes

| Cause | Description |
|---|---|
| Extension not enabled | `pg_cron` not installed on the project |
| Schedule in wrong timezone | pg_cron uses UTC; local schedule offset assumed |
| SQL syntax error in job | Job created but fails silently |
| Role permissions | Job runs as `postgres` but target table has restrictive RLS |
| Supabase platform pause | Free-tier project paused (auto-pauses after 1 week inactive) |
| Job maximum count hit | Edge case: `max_running` limit reached |

---

## Fast checks

```sql
-- List all scheduled jobs
SELECT jobid, schedule, command, nodename, active
FROM cron.job
ORDER BY jobid;

-- Last 20 run results
SELECT jobid, job_pid, database, command, status, return_message, start_time, end_time
FROM cron.job_run_details
ORDER BY start_time DESC
LIMIT 20;

-- Failed runs in last 24h
SELECT *
FROM cron.job_run_details
WHERE status = 'failed'
  AND start_time > now() - interval '24 hours';

-- Check pg_cron extension
SELECT * FROM pg_extension WHERE extname = 'pg_cron';
```

---

## Fix paths

### No rows in `cron.job_run_details`
1. Verify the schedule expression is correct UTC:
   ```sql
   -- Every 2 minutes
   SELECT cron.schedule('test-job', '*/2 * * * *', 'SELECT 1');
   ```
2. Confirm `pg_cron` is enabled: Supabase dashboard → Database → Extensions → pg_cron.
3. Check if the project is paused (free tier).

### Status = `failed`
1. Read `return_message` in `cron.job_run_details` — it contains the SQL error.
2. Fix the SQL command or the target function.
3. Re-activate:
   ```sql
   UPDATE cron.job SET active = true WHERE jobid = <id>;
   ```

### Timezone confusion
- All pg_cron schedules are UTC.
- Manila (UTC+08:00) 08:00 local = 00:00 UTC: `0 0 * * *`
- Use the cron.schedule `schedule` column to confirm UTC intent.

### RLS blocking job
- pg_cron runs as the `postgres` superuser — RLS applies to `authenticated` role, not `postgres`.
- If calling a function via cron that does `SECURITY INVOKER`, it may be affected. Use `SECURITY DEFINER` for cron-called functions.

---

## Prevention
- Log `cron.job_run_details` to your observability stack (alert on `status = 'failed'`).
- Test new cron expressions manually before relying on them in production.
- Keep schedules in UTC and document the local equivalent in comments.
