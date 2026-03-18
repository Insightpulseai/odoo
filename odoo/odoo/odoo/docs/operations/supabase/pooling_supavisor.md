# Runbook: Connection Pooling / Supavisor

**Canonical source:** https://supabase.com/docs/guides/troubleshooting/supavisor-faq-YyP5tI

---

## Error signatures

- `remaining connection slots are reserved for non-replication superuser connections`
- `FATAL: too many connections`
- Latency spikes at high concurrency
- `connection refused` from Edge Functions / serverless
- REST API returns 5xx intermittently under load

---

## Likely causes

| Cause | Description |
|---|---|
| Direct connections bypassing Supavisor | Using port 5432 directly from serverless |
| Pool exhaustion | Max pool size too small for concurrency |
| Long-held transactions | Open transactions blocking pool slots |
| Idle connections not released | ORM not closing connections properly |
| Project under-provisioned | Free/Pro tier connection limit hit |

---

## Connection endpoints

| Use case | Host | Port | Note |
|---|---|---|---|
| Serverless / Edge Functions | Supavisor (pooler) | `6543` | Recommended for ephemeral connections |
| Long-running / migrations | Direct | `5432` | Use for psql, migrations, admin tasks |
| Prisma / ORMs (serverless) | Supavisor | `6543` | Set `?pgbouncer=true` in connection string |

---

## Fast checks

```sql
-- Active connection count by state
SELECT state, count(*) FROM pg_stat_activity
WHERE datname = current_database()
GROUP BY state;

-- Long-running queries (> 60s)
SELECT pid, now() - query_start AS duration, query, state
FROM pg_stat_activity
WHERE state != 'idle'
  AND now() - query_start > interval '60 seconds'
ORDER BY duration DESC;

-- Idle connections holding locks
SELECT pid, usename, application_name, state, wait_event_type, wait_event
FROM pg_stat_activity
WHERE state = 'idle in transaction'
  AND query_start < now() - interval '5 minutes';
```

---

## Fix paths

### `too many connections`
1. Switch serverless workloads to use the **Supavisor pooler endpoint** (port `6543`).
2. In connection string, add `?pgbouncer=true` (disables prepared statements, required for transaction pooling).
3. Terminate idle transactions:
   ```sql
   SELECT pg_terminate_backend(pid)
   FROM pg_stat_activity
   WHERE state = 'idle in transaction'
     AND query_start < now() - interval '10 minutes';
   ```

### Latency spikes
1. Check for long-running queries blocking pool slots (query above).
2. Review `pg_stat_activity` for lock contention.
3. Consider upgrading project tier for higher pool limits.

### Edge Functions using wrong port
- Edge Functions must use `SUPABASE_DB_URL` configured with port `6543`.
- Never hardcode `5432` in serverless function env vars.

---

## Connection string patterns

```
# Pooler (serverless / Edge Functions)
postgresql://postgres.PROJECT_REF:PASSWORD@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres?pgbouncer=true

# Direct (migrations / admin)
postgresql://postgres.PROJECT_REF:PASSWORD@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres
```

---

## Prevention
- Always use port `6543` (pooler) from Edge Functions and short-lived processes.
- Monitor active connection count; alert when > 80% of project limit.
- Use `connection_limit=1` in Prisma for serverless deploys.
