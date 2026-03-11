# Runbook: Auth / JWT Issues

**Canonical source:** https://supabase.com/docs/guides/troubleshooting

---

## Error signatures

- `401 Unauthorized` / `{"message":"invalid JWT"}`
- `invalid claim: missing sub`
- `403 Forbidden` on an RLS-protected table
- `JWSError JWSInvalidSignature`

---

## Likely causes

| Cause | Description |
|---|---|
| Wrong token type | Using `anon` key as a user token (no `sub` claim) |
| Service role used client-side | RLS bypass; security incident |
| Clock skew | Client clock > 60s from server time |
| Expired JWT | Token TTL exceeded; needs refresh |
| RLS policy scoping | Policy uses `auth.uid()` but row has a different owner column |
| Missing `sub` in custom JWT | Custom auth integration omitted required claim |

---

## Fast checks

```sql
-- Recent auth errors in the last hour
SELECT id, created_at, status, error_message
FROM auth.audit_log_entries
WHERE created_at > now() - interval '1 hour'
  AND status NOT IN (200, 201)
ORDER BY created_at DESC
LIMIT 20;

-- Check if a JWT is a service role key (should never come from browser)
-- If Authorization: Bearer <token> has role=service_role → rotate immediately
SELECT current_setting('request.jwt.claims', true)::jsonb ->> 'role' AS jwt_role;

-- RLS policy inspection
SELECT schemaname, tablename, policyname, cmd, qual
FROM pg_policies
WHERE tablename = '<your_table>';
```

---

## Fix paths

### `missing sub` claim
1. Verify you are using a **user JWT** (`Authorization: Bearer <user_jwt>`) not the `anon` key.
2. If custom JWT, ensure `sub` is set to the user's UUID.
3. If using `createClient` from browser, verify `supabase.auth.getSession()` returns a session before the request.

### Service role used client-side
1. **Rotate the service role key immediately** via Supabase dashboard.
2. Update all server-side env vars (`SUPABASE_SERVICE_ROLE_KEY`).
3. Ensure client code only ever uses `SUPABASE_ANON_KEY`.

### `403` from RLS
1. Check `pg_policies` for the affected table.
2. Verify the policy `qual` expression matches the JWT claims structure.
3. Test with: `SET ROLE authenticated; SET LOCAL "request.jwt.claims" = '{"sub":"<uuid>"}'; SELECT ...`

### Clock skew
1. Sync server time: `ntpdate pool.ntp.org` (or equivalent).
2. Check container/VM time sync if self-hosted.

---

## Prevention
- Never pass `SUPABASE_SERVICE_ROLE_KEY` to client-side code.
- Use `guardAuth()` from `supabase/functions/_shared/auth_guard.ts` in all Edge Functions.
- Store service_role key in `ir.config_parameter` (Odoo) or `Deno.env` (Edge Functions) only.
