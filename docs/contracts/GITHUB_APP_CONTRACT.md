# GitHub App Contract (C-19)

> **Scope**: Defines the integration boundary between the IPAI GitHub App and
> Supabase Edge Functions that receive webhooks and broker installation tokens.
>
> SSOT: `ssot/integrations/github/github_app_ipai.yaml`
> Last updated: 2026-03-01

---

## 1. Parties

| Role | Component | Location |
|------|-----------|----------|
| **Source (inbound)** | GitHub API (webhooks) | External |
| **Source (outbound)** | Supabase Edge Functions | `supabase/functions/github-app-webhook/`, `supabase/functions/github-app-token/`, `supabase/functions/github-app-actions/` |
| **Consumer** | GitHub REST/GraphQL API | `api.github.com` |
| **SSOT metadata** | GitHub App SSOT | `ssot/integrations/github/github_app_ipai.yaml` |
| **Installation map** | Installation mappings | `ssot/mappings/github_installations.yaml` |
| **Secret registry** | Supabase Vault | `ssot/secrets/registry.yaml` (names only) |

---

## 2. Protocol

### 2.1 Inbound: Webhook Reception

```
POST <SUPABASE_EDGE_URL>/github-app-webhook
Headers:
  X-GitHub-Event: <event_type>
  X-GitHub-Delivery: <uuid>
  X-Hub-Signature-256: sha256=<hmac>
  Content-Type: application/json
Body:
  { action, sender, repository, installation, ... }
Response (200 OK):
  { ok: true }
Response (error):
  { ok: false, code: ErrorCode, message: string }
  ErrorCodes: UNAUTHORIZED | BAD_REQUEST | METHOD_NOT_ALLOWED | SERVICE_ERROR
```

### 2.2 Outbound: Installation Token Exchange

```
1. Edge Function creates JWT:
   - Algorithm: RS256
   - Payload: { iss: <GITHUB_APP_ID>, iat: <now>, exp: <now + 600> }
   - Sign with: GITHUB_APP_PRIVATE_KEY_PEM

2. Exchange JWT for installation token:
   POST https://api.github.com/app/installations/<installation_id>/access_tokens
   Headers:
     Authorization: Bearer <jwt>
     Accept: application/vnd.github+json
   Response:
     { token: "ghs_...", expires_at: "...", permissions: {...} }

3. Use installation token for scoped API calls:
   Authorization: Bearer ghs_...
```

---

## 3. Auth & Verification

### 3.1 Webhook Signature Verification

All inbound webhooks MUST be verified before processing:

```typescript
const signature = req.headers.get("X-Hub-Signature-256");
const body = await req.text();
const expected = "sha256=" + hmac("sha256", GITHUB_WEBHOOK_SECRET, body);
if (!timingSafeEqual(signature, expected)) {
  return jsonErr("UNAUTHORIZED", "Invalid signature", 401);
}
```

### 3.2 JWT Signing for Token Exchange

- Algorithm: RS256 (RSA PKCS#1 v1.5 with SHA-256)
- Key: PEM-encoded RSA private key from Supabase Vault
- JWT lifetime: 10 minutes maximum (GitHub enforced)
- Installation tokens: 1 hour lifetime (GitHub enforced)

---

## 4. Invariants

1. **Signature verification is mandatory.** Every webhook request MUST have its `X-Hub-Signature-256` verified against the shared secret before any processing occurs. Reject with 401 on mismatch.

2. **Idempotency via X-GitHub-Delivery.** The `X-GitHub-Delivery` header is a UUID unique per delivery. Persist before side effects; deduplicate on `(delivery_id)`. Store in `ops.github_deliveries` (if table exists) or use the event audit trail.

3. **Least-privilege permissions.** The GitHub App MUST request only the minimum permissions needed. Start with read-only; escalate only when a specific feature requires write access. Permissions are declared in `ssot/integrations/github/github_app_ipai.yaml`.

4. **Short-lived tokens only.** Never store installation tokens in the database or Vault. They are ephemeral (1-hour lifetime) and must be requested on demand for each operation.

5. **Allowlisted events only.** Only events listed in `policy.allowlisted_events` in the SSOT YAML are processed. Unknown event types are acknowledged (200) but not processed.

6. **Audit trail.** All webhook deliveries and token exchanges are audited to `ops.platform_events` with `actor: github-app-webhook` or `actor: github-app-token`.

---

## 5. Environment Variables (Supabase Vault)

| Secret name | Purpose | Vault key |
|-------------|---------|-----------|
| `GITHUB_APP_ID` | JWT `iss` claim for App authentication | `github_app_id` |
| `GITHUB_APP_PRIVATE_KEY_PEM` | RS256 private key for JWT signing | `github_app_private_key_pem` |
| `GITHUB_WEBHOOK_SECRET` | HMAC-SHA256 shared secret for webhook verification | `github_webhook_secret` |

All values stored in Supabase Vault. Names registered in `ssot/secrets/registry.yaml`.

---

## 6. Event Processing Flow

```
GitHub webhook delivery
  |
  v
github-app-webhook (Edge Function)
  |-- Verify X-Hub-Signature-256
  |-- Check event type in allowlist
  |-- Deduplicate on X-GitHub-Delivery
  |-- Audit to ops.platform_events
  |-- Route to handler by event type:
  |     pull_request -> PR automation
  |     check_run    -> Check status
  |     issues       -> Issue sync
  |
  v
github-app-token (Edge Function, internal)
  |-- Create RS256 JWT (iss=APP_ID, exp=10min)
  |-- POST /app/installations/{id}/access_tokens
  |-- Return short-lived ghs_* token
  |
  v
github-app-actions (Edge Function, internal)
  |-- Use installation token for API calls
  |-- Post PR comments, create check runs, etc.
  |-- Audit results to ops.platform_events
```

---

## 7. Error Handling

| Scenario | Response | Action |
|----------|----------|--------|
| Invalid signature | 401 UNAUTHORIZED | Log attempt, do not process |
| Unknown event type | 200 OK (acknowledge) | Log, skip processing |
| Duplicate delivery | 200 OK (idempotent) | Return cached result |
| JWT creation failure | 500 SERVICE_ERROR | Log error, retry with backoff |
| Token exchange failure | 500 SERVICE_ERROR | Log error, surface in audit |
| GitHub API rate limit | 429 (propagate) | Respect `Retry-After`, log |

---

## 8. CI Enforcement

- `ssot-surface-guard.yml` validates that Edge Function directories contain README.md
- `platform-guardrails.yml` scans for hardcoded secrets in function source
- Allowlisted events in SSOT YAML must match webhook configuration in GitHub App settings

---

## 9. Related Docs

- `ssot/integrations/github/github_app_ipai.yaml` -- App metadata SSOT
- `ssot/mappings/github_installations.yaml` -- Installation ID mappings
- `ssot/secrets/registry.yaml` -- Secret name registry
- `docs/contracts/SUPABASE_EDGE_FUNCTIONS_CONTRACT.md` -- Edge Function standards
- `docs/contracts/SUPABASE_VAULT_CONTRACT.md` -- Vault access patterns
- `docs/contracts/PLATFORM_CONTRACTS_INDEX.md` -- Contract index (C-19)
