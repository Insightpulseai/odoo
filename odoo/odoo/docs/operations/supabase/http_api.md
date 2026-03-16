# Runbook: HTTP API / Edge Function Issues

**Canonical source:** https://supabase.com/docs/guides/troubleshooting/http-api-issues

---

## Error signatures

- Intermittent `500 Internal Server Error` on REST API
- Edge Function returns `504 Gateway Timeout`
- Edge Function cold start > 5 seconds
- `net::ERR_FAILED` from client
- `FunctionsHttpError: Edge Function returned a non-2xx status code`

---

## Likely causes

| Cause | Description |
|---|---|
| Under-provisioned project | Free tier CPU/RAM limits hit |
| Edge Function memory leak | Function allocates memory across requests |
| Downstream timeout | Function calls external API that times out |
| Unhandled exception | Function throws, returns 500 without cleanup |
| Missing env var | `Deno.env.get(...)` returns undefined at runtime |
| CORS misconfiguration | Browser blocked by missing `Access-Control-Allow-Origin` |

---

## Fast checks

```bash
# Test Edge Function health directly
curl -i \
  -H "Authorization: Bearer $SUPABASE_ANON_KEY" \
  https://<PROJECT_REF>.supabase.co/functions/v1/<function-name>

# Check function logs via Supabase CLI
supabase functions logs <function-name> --project-ref <PROJECT_REF>

# Check REST API health
curl -i "https://<PROJECT_REF>.supabase.co/rest/v1/?apikey=$SUPABASE_ANON_KEY"
```

```sql
-- Check for slow PostgREST queries
SELECT query, calls, mean_exec_time, total_exec_time
FROM pg_stat_statements
WHERE query ILIKE '%<your_table>%'
ORDER BY mean_exec_time DESC
LIMIT 10;
```

---

## Fix paths

### 500 on REST API
1. Check `pg_stat_activity` for blocking queries.
2. Check PostgREST logs via Supabase dashboard (Logs → PostgREST).
3. Verify the table/view RLS policies are not throwing errors.

### Edge Function timeout (504)
1. Check if the function is waiting on an external HTTP call.
2. Set explicit timeouts for outbound requests:
   ```typescript
   const resp = await fetch(url, { signal: AbortSignal.timeout(25_000) });
   ```
3. Supabase Edge Functions have a hard 60s limit; keep functions under 50s.

### Cold start latency
1. Deploy only necessary imports; avoid large npm packages.
2. Use `esm.sh` or `deno.land/x` imports with version pins (avoids re-fetching).
3. Enable `--no-verify-jwt` only if appropriate (reduces overhead for public endpoints).

### Missing env var
1. Confirm all required secrets are set in Supabase dashboard → Edge Functions → Secrets.
2. Test locally with `supabase functions serve --env-file .env.local`.
3. Use `Deno.env.get("VAR") ?? throwConfigError("VAR")` pattern — fail fast on missing secrets.

### CORS errors
```typescript
// Standard CORS headers for Edge Function
const corsHeaders = {
  "Access-Control-Allow-Origin": Deno.env.get("ALLOWED_ORIGIN") ?? "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};
if (req.method === "OPTIONS") {
  return new Response("ok", { headers: corsHeaders });
}
```

---

## Prevention
- All Edge Functions use `auth_guard.ts` — unhandled errors become 401/500, not unguarded panics.
- Log `edge_logs` table in observability stack; alert on error rate > 1%.
- Use `AbortSignal.timeout()` on all outbound fetch calls.
- Pin dependency versions in imports to avoid breaking changes.
