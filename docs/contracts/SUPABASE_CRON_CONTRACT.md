# Supabase Cron Contract

> **Scope**: All scheduled jobs (pg_cron) that invoke Edge Functions or run SQL.
> Jobs defined in Supabase dashboard are drift unless backported to migrations.
>
> Reference: [Supabase Cron docs](https://supabase.com/docs/guides/cron)
> Last updated: 2026-02-21

---

## 1. What Supabase Cron Is

Supabase Cron is a managed packaging of **pg_cron** (Postgres extension) that:
- Schedules recurring jobs using cron syntax (including sub-minute intervals)
- Stores job definitions in `cron.job`
- Records execution history in `cron.job_run_details`
- Can invoke SQL, DB functions, HTTP webhooks, or Edge Functions (via pg_net)

---

## 2. SSOT Rule

**`supabase/migrations/` is the SSOT for all cron job definitions.**

| Source | Status |
|--------|--------|
| `supabase/migrations/*_cron_*.sql` | ✅ SSOT — reproducible across environments |
| Supabase dashboard Cron UI | ⚠️ Drift unless backported to a migration |

**Any job created in the dashboard must be backported as a migration before the next deploy.**

---

## 3. Approved Scheduling Pattern

### Edge Function invocation (preferred)

```sql
SELECT cron.schedule(
  'ops_<job_name>',            -- always prefixed ops_* or svc_*
  '*/45 * * * *',              -- cron expression
  $$
  SELECT net.http_post(
    url := (
      SELECT decrypted_secret FROM vault.decrypted_secrets
      WHERE name = 'ops.cron.<function>_url' LIMIT 1
    ) || '?action=<action>',
    headers := jsonb_build_object(
      'x-bridge-secret', (
        SELECT decrypted_secret FROM vault.decrypted_secrets
        WHERE name = 'ops.cron.<function>_secret' LIMIT 1
      ),
      'x-request-id', gen_random_uuid()::text
    ),
    body := '{}'::jsonb,
    timeout_milliseconds := 20000   -- 20s < Edge Function wall clock limit
  );
  $$
);
```

**Rules**:
- Function URL and auth token stored in **Vault** — never in migration SQL.
- `timeout_milliseconds := 20000` required — prevents pg_net from hanging past edge limits.
- Job name prefix: `ops_` (platform automation) or `svc_` (service-specific).

### SQL function invocation (for DB-only jobs)

```sql
SELECT cron.schedule('ops_cleanup_stale_tasks', '0 3 * * *', 'CALL ops.cleanup_stale_tasks()');
```

---

## 4. Required Vault Secrets per Job

Before applying a cron migration, these Vault secrets must exist:

| Cron job | Vault key | Purpose |
|---------|----------|---------|
| `ops_zoho_token_prewarm` | `ops.cron.zoho_bridge_url` | Edge Function URL |
| `ops_zoho_token_prewarm` | `ops.cron.zoho_bridge_secret` | `x-bridge-secret` value |

Set via SQL (one-time, values not committed):
```sql
SELECT vault.create_secret('<url>', 'ops.cron.zoho_bridge_url', 'description');
SELECT vault.create_secret('<secret>', 'ops.cron.zoho_bridge_secret', 'description');
```

---

## 5. Current Jobs

| Job name | Schedule | Action | Migration |
|---------|----------|--------|-----------|
| `ops_zoho_token_prewarm` | `*/45 * * * *` | `mint_token` on `zoho-mail-bridge` | `20260221000002_cron_token_prewarm.sql` |

---

## 6. Monitoring / Debugging

```sql
-- List all jobs
SELECT jobname, schedule, active FROM cron.job WHERE jobname LIKE 'ops_%';

-- Check recent runs
SELECT jobname, start_time, end_time, status, return_message
FROM cron.job_run_details
WHERE jobname = 'ops_zoho_token_prewarm'
ORDER BY start_time DESC
LIMIT 10;

-- Check for failures in last 24h
SELECT jobname, start_time, status, return_message
FROM cron.job_run_details
WHERE status = 'failed'
  AND start_time > now() - interval '24 hours';
```

---

## 7. Rollback / Unschedule

```sql
-- Disable without deleting
UPDATE cron.job SET active = false WHERE jobname = 'ops_zoho_token_prewarm';

-- Remove permanently (requires backport migration to keep SSOT current)
SELECT cron.unschedule('ops_zoho_token_prewarm');
```

**Do not uninstall pg_cron** unless intentionally decommissioning all jobs — uninstalling drops the extension and deletes all job definitions permanently.

---

## 8. Extension Requirements

`pg_cron` and `pg_net` are enabled by each cron migration via
`CREATE EXTENSION IF NOT EXISTS`. No dashboard step is required.

If a Supabase plan/project does not permit these extensions, the migration fails
loudly — treat as a provisioning constraint, not a manual step.

---

## 9. Related Docs

- `docs/contracts/SUPABASE_VAULT_CONTRACT.md` — Vault key naming convention
- `docs/contracts/SUPABASE_EDGE_FUNCTIONS_CONTRACT.md` — Edge Function runtime limits
- `docs/contracts/MAIL_BRIDGE_CONTRACT.md` — `zoho-mail-bridge` (the target of token prewarm)
- `supabase/migrations/20260221000002_cron_token_prewarm.sql` — Job definitions
