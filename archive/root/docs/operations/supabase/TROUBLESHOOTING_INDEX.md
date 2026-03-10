# Supabase Troubleshooting Index

**Last updated:** 2026-02-27
**Canonical source:** Supabase official troubleshooting hub — https://supabase.com/docs/guides/troubleshooting

This index routes incidents to the correct runbook and to Supabase's authoritative docs.
For machine routing, see `ssot/runbooks/supabase_troubleshooting_map.yaml`.

---

## Quick route by symptom

| Symptom / Error | Runbook | Severity default |
|---|---|---|
| `401 Unauthorized` / `invalid claim: missing sub` | [auth_jwt.md](./auth_jwt.md) | SEV2 |
| `403 Forbidden` / wrong RLS policy | [auth_jwt.md](./auth_jwt.md) | SEV2 |
| `42501 permission denied for table http_request_queue` | [webhooks_pg_net.md](./webhooks_pg_net.md) | SEV2 |
| Webhook never fires / stuck queue | [webhooks_pg_net.md](./webhooks_pg_net.md) | SEV2 |
| pg_cron job not running / missing runs | [cron_pg_cron.md](./cron_pg_cron.md) | SEV3 |
| `connection refused` / `too many connections` / 5xx from REST | [pooling_supavisor.md](./pooling_supavisor.md) | SEV1 |
| Edge Function timeout / 5xx / slow TTFB | [http_api.md](./http_api.md) | SEV2 |
| Storage: unauthorized access / bucket misconfiguration | [storage_buckets.md](./storage_buckets.md) | SEV2 |

---

## Incident classes

### 1. Auth / JWT issues
**Runbook:** [auth_jwt.md](./auth_jwt.md)
**Supabase docs:** https://supabase.com/docs/guides/troubleshooting

Key scenarios:
- User gets `401` despite correct password → check `missing sub` claim, token type, clock skew
- Service role accidentally used client-side → RLS bypass, security incident
- `403` with valid JWT → RLS policy incorrectly scoped, check `auth.uid()` vs `auth.role()`

---

### 2. Webhooks / pg_net permission errors
**Runbook:** [webhooks_pg_net.md](./webhooks_pg_net.md)
**Supabase docs:** https://supabase.com/docs/guides/troubleshooting/webhook-debugging-guide-M8sk47

Key scenarios:
- `42501 permission denied for table http_request_queue` → pg_net extension permissions
- Webhook fires but response never arrives → background worker down, check `pg_net.http_request_queue`
- Trigger on `net.*` tables → avoid (deadlock risk)

---

### 3. pg_cron: jobs not running
**Runbook:** [cron_pg_cron.md](./cron_pg_cron.md)
**Supabase docs:** https://supabase.com/docs/guides/troubleshooting/pgcron-debugging-guide-n1KTaz

Key scenarios:
- Job shows scheduled but no `cron.job_run_details` rows
- Job ran once then stopped
- Timezone confusion (pg_cron uses UTC)

---

### 4. Connection pooling / Supavisor
**Runbook:** [pooling_supavisor.md](./pooling_supavisor.md)
**Supabase docs:** https://supabase.com/docs/guides/troubleshooting/supavisor-faq-YyP5tI

Key scenarios:
- `remaining connection slots are reserved` / `too many connections`
- Latency spikes under load
- Serverless functions exhausting the pool

---

### 5. HTTP API / Edge Function issues
**Runbook:** [http_api.md](./http_api.md)
**Supabase docs:** https://supabase.com/docs/guides/troubleshooting/http-api-issues

Key scenarios:
- Intermittent 5xx on REST API
- Edge Function cold starts > 5s
- Under-provisioned project tier

---

### 6. Storage bucket security
**Runbook:** [storage_buckets.md](./storage_buckets.md)

Key scenarios:
- Public bucket serving private finance documents
- Cross-user receipt access
- Bucket naming / key path inconsistencies

---

## Fast checks (copy-paste)

```sql
-- Check recent auth errors
SELECT id, created_at, status, error_message
FROM auth.audit_log_entries
WHERE created_at > now() - interval '1 hour'
  AND status != 200
ORDER BY created_at DESC
LIMIT 20;

-- pg_net queue depth
SELECT count(*) FROM net.http_request_queue;
SELECT count(*) FROM net._http_response WHERE created < now() - interval '5 min';

-- pg_cron recent jobs
SELECT jobid, jobname, start_time, end_time, status, return_message
FROM cron.job_run_details
ORDER BY start_time DESC
LIMIT 10;

-- Active connections
SELECT count(*), state FROM pg_stat_activity GROUP BY state;
```
