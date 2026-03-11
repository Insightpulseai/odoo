# Runbook: Webhooks / pg_net Permission Errors

**Canonical source:** https://supabase.com/docs/guides/troubleshooting/webhook-debugging-guide-M8sk47

---

## Error signatures

- `42501 permission denied for table http_request_queue`
- `ERROR: permission denied for schema net`
- Webhook trigger fires but request never arrives
- `net.http_request_queue` rows stuck with no response

---

## Likely causes

| Cause | Description |
|---|---|
| Missing `pg_net` extension grants | `postgres` role has grants but app role doesn't |
| Trigger on `net.*` tables | Creates deadlock — avoid at all costs |
| Background worker down | `pg_net` worker process crashed |
| Request timeout | Default 5s too short for slow endpoints |
| Firewall / egress blocked | Supabase can't reach your external URL |

---

## Fast checks

```sql
-- Check if pg_net extension is installed
SELECT * FROM pg_extension WHERE extname = 'pg_net';

-- Queue depth (non-zero = backlog or worker down)
SELECT count(*) AS queue_depth FROM net.http_request_queue;

-- Check recent responses (errors should appear here)
SELECT id, created, status_code, error_msg
FROM net._http_response
ORDER BY created DESC
LIMIT 10;

-- Restart background worker (if available — requires superuser)
SELECT pg_reload_conf();
-- Or from Supabase dashboard: Database → Extensions → disable/re-enable pg_net
```

---

## Fix paths

### `42501 permission denied for table http_request_queue`
1. Grant usage on the `net` schema to the role making the call:
   ```sql
   GRANT USAGE ON SCHEMA net TO postgres;
   GRANT ALL ON ALL TABLES IN SCHEMA net TO postgres;
   ```
2. If calling from an app role (e.g. `authenticated`), grant to that role too.
3. Do **not** grant public access to `net.*`.

### Trigger on `net.*` tables
- Remove any trigger that writes to `net.http_request_queue` directly inside a transaction that is also waiting on a response. Use `AFTER` triggers with deferred execution or a separate Edge Function.

### Background worker not processing queue
1. Check Supabase project health in the dashboard.
2. For self-hosted: restart the `pg_net` background worker:
   ```bash
   # Inside the postgres container
   SELECT pg_cancel_backend(pid) FROM pg_stat_activity WHERE application_name LIKE '%pg_net%';
   ```
3. If persistent, file a Supabase support ticket with `net.http_request_queue` row count.

### Timeout issues
- Default `pg_net` timeout is 5 seconds. Increase for slow endpoints:
  ```sql
  UPDATE net.http_request_queue SET timeout_milliseconds = 30000 WHERE ...;
  ```

---

## Prevention
- Use Supabase Edge Functions for outbound HTTP from triggers (avoid `pg_net` in hot paths).
- Monitor `net.http_request_queue` queue depth in your observability stack.
- Use `requireHmac()` from `auth_guard.ts` to verify inbound callbacks; don't trust raw HTTP.
