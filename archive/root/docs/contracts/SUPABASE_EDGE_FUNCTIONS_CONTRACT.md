# Supabase Edge Functions Contract

> **Scope**: Defines the approved use cases, runtime constraints, and code standards
> for all Edge Functions in `supabase/functions/`. Every function must comply.
>
> Reference: [Supabase Edge Functions docs](https://supabase.com/docs/guides/functions)
> Last updated: 2026-02-21

---

## 1. What Edge Functions Are (and Aren't)

**Edge Functions** = server-side TypeScript running on Deno, deployed globally.

| Approved use | Not approved |
|-------------|-------------|
| Webhook receivers (GitHub, Stripe, Zoho) | CPU-intensive computation |
| Third-party API bridges (Zoho Mail, n8n) | Long-running batch processing |
| Auth hooks and provisioning | Client-facing BFF (use Odoo API instead) |
| Scheduled invocations (via pg_cron + pg_net) | Streaming large datasets |
| SSOT gateway (secret-safe proxy) | Direct DB manipulation without RLS |

---

## 2. Runtime Limits (Hard)

| Limit | Free tier | Paid tier |
|-------|-----------|-----------|
| Memory | 256 MB | 256 MB |
| CPU time per request | 2 s | 2 s |
| Wall clock duration | 150 s | 400 s |
| Idle timeout | 150 s | 150 s |

**Design implications**:
- All outbound API calls (Zoho, GitHub, n8n) must have explicit `timeout` options.
- `fetch()` calls must complete within the wall clock limit — set `signal: AbortSignal.timeout(20_000)` (20s) as the default.
- No busy loops. No `while (true)` polling inside a single invocation.
- Long jobs → emit an async task to `ops.task_queue`, return 202 immediately.

---

## 3. Required Function Contract

Every function in `supabase/functions/` must implement:

### 3.1 `?action=` allowlist
```typescript
const ALLOWED_ACTIONS = new Set(["health", /* ... */]);
// Any action not in this set → 404 NOT_FOUND (not 400)
```

### 3.2 Structured error responses
```typescript
type ErrorCode =
  | "UNAUTHORIZED" | "BAD_REQUEST" | "METHOD_NOT_ALLOWED"
  | "NOT_FOUND" | "SERVICE_ERROR" | "NOT_CONFIGURED";

function jsonErr(code: ErrorCode, message: string, status: number): Response
function jsonOk(data: unknown, status?: number): Response
```

### 3.3 Auth guard (`x-bridge-secret` or JWT)
- Internal functions: `requireBridgeAuth(req)` using `x-bridge-secret` header
- External functions: `verify_jwt = true` in `supabase/config.toml`
- `health` action: no auth required; returns `{ok: true, service: "<name>"}` only

### 3.4 Request ID for idempotency
```typescript
const requestId = req.headers.get("x-request-id") ?? crypto.randomUUID();
// Include in audit log; use for deduplication where applicable
```

### 3.5 Structured logging (no secrets)
```typescript
// Allowed to log: status, event_type, target, request_id, timing
// NEVER log: secrets, tokens, passwords, full email bodies, personal data
console.log(JSON.stringify({ request_id, event, status, ms }));
```

### 3.6 Audit trail for side-effecting operations
```typescript
// All state-changing operations (send email, create user, etc.) must audit to:
await supabase.from("ops.platform_events").insert({
  event_type: "<function>.<action>",
  actor: "<function-name>",
  target: "<recipient/resource>",
  payload: { /* non-sensitive */ },
  status: "ok" | "error",
  error_detail: errorMessage ?? null,
});
```

### 3.7 README + env var declaration
Every function directory must contain `README.md` with:
- Purpose and approved actions
- Required env var names (no values)
- Auth mechanism
- Example curl for `health` check

---

## 4. Secret Handling Rules

| Location | When to use | Access pattern |
|----------|-------------|----------------|
| Edge Function Secrets (`supabase secrets set`) | Runtime-only secrets (API keys, tokens) | `Deno.env.get("VAR_NAME")` |
| Supabase Vault | Secrets needed inside Postgres (pg_cron) | `SECURITY DEFINER` RPC |
| Container env vars | Odoo/n8n runtime | Not accessible to Edge Functions |

**Never**:
- Hard-code secret values in TypeScript source
- Log `Deno.env.get(...)` results
- Include secrets in error responses or audit payloads

---

## 5. Current Functions Inventory

| Function | Auth | `verify_jwt` | Purpose | Status |
|----------|------|-------------|---------|--------|
| `zoho-mail-bridge` | `x-bridge-secret` | `false` | ERP doc email via Zoho API | ✅ Deployed |
| `copilot-chat` | none | `false` | AI chat proxy | ✅ Deployed |
| `github-slack-bridge` | webhook secret | `false` | GitHub → Slack | ✅ Deployed |
| `github-app-auth` | JWT | `true` | GitHub OAuth | ✅ Deployed |
| `infra-memory-ingest` | JWT | `true` | Infrastructure memory | ✅ Deployed |
| `schema-changed` | JWT | `true` | Schema change events | ✅ Deployed |
| `tenant-invite` | JWT | `true` | Tenant provisioning | ✅ Deployed |
| `cron-processor` | JWT | `true` | Scheduled job runner | ✅ Deployed |
| `ipai-copilot` | none | `false` | Copilot API | ✅ Deployed |
| `sync-odoo-modules` | none | `false` | Odoo module sync | ✅ Deployed |

**`_template-bridge/`** — see `supabase/functions/_template-bridge/` for the canonical starting point.

---

## 6. Scheduling Pattern (pg_cron + pg_net)

For scheduled invocations, follow Supabase's recommended pattern:

```sql
-- Store the function URL + token in Vault (not in SQL)
SELECT vault.create_secret(
  'https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/cron-processor',
  'ops.cron.function_url',
  'Cron processor Edge Function URL'
);

-- Schedule using pg_cron + pg_net
SELECT cron.schedule(
  'cron-processor-hourly',
  '0 * * * *',
  $$
  SELECT net.http_post(
    url := (SELECT decrypted_secret FROM vault.decrypted_secrets
            WHERE name = 'ops.cron.function_url'),
    headers := jsonb_build_object(
      'Content-Type', 'application/json',
      'Authorization', 'Bearer ' || (SELECT decrypted_secret FROM vault.decrypted_secrets
                                     WHERE name = 'auth.jwt.service_role_key')
    ),
    body := '{}'::jsonb
  )
  $$
);
```

This is the only approved pattern for scheduled Edge Function invocation.

---

## 7. CI Enforcement

`ssot-surface-guard.yml` checks that:
- `supabase/functions/` directories added in a PR contain a `README.md`
- No new `supabase/functions/` files contain string literals matching `password|secret|api.key|token`

See also: `platform-guardrails.yml` (secret scan on committed files)

---

## 8. Related Docs

- `docs/contracts/SUPABASE_VAULT_CONTRACT.md` — Vault vs Edge Secrets decision table
- `docs/contracts/MAIL_BRIDGE_CONTRACT.md` — `zoho-mail-bridge` implementation details
- `docs/contracts/SUPABASE_AUTH_SMTP_CONTRACT.md` — Auth invite flow (Pattern A, no Edge Function)
- `supabase/functions/_template-bridge/` — Canonical function template
- `supabase/config.toml` — `verify_jwt` settings per function
