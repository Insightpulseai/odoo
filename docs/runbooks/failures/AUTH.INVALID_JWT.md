# Runbook: AUTH.INVALID_JWT

**Severity**: High
**HTTP Status**: 401
**Retryable**: No (re-authenticate first)

## Symptoms

An Edge Function returned 401 with `AGENT.AUTH.INVALID_JWT`.

```json
{
  "error": "AUTH.INVALID_JWT",
  "message": "JWT verification failed or token expired"
}
```

## Root Causes

1. The client forwarded a JWT that has already expired (Supabase JWTs expire after 1 hour by default).
2. The JWT was signed with the wrong secret (wrong Supabase project).
3. The `Authorization: Bearer` header was missing or had incorrect casing.
4. The user's session was revoked (sign-out on another device).

## Remediation

**For human callers (ops-console):**
```bash
# 1. Sign out and sign back in via the ops-console UI
# The session refresh happens automatically via Supabase Auth helpers

# 2. Verify the session manually
curl -X GET "$SUPABASE_URL/auth/v1/user" \
  -H "apikey: $SUPABASE_ANON_KEY" \
  -H "Authorization: Bearer $USER_JWT"
```

**For agent callers (CI / Edge Functions):**
```bash
# 1. Check the service role key is correctly set in GitHub Secrets
# The service role key never expires — if using this, something else is wrong

# 2. Verify the key matches the Supabase project
echo $SUPABASE_SERVICE_ROLE_KEY | cut -c1-20  # compare with dashboard

# 3. Check you're calling the right project URL
echo $SUPABASE_URL  # should be https://spdtwktxdalcfigzeqrz.supabase.co
```

## Prevention

- Implement JWT refresh in the ops-console search page (call `getSession()` which auto-refreshes).
- Never cache JWTs for > 50 minutes; refresh before each agent invocation.
- Use service role key only in server-side Edge Functions, never in the browser.
