# Implementation Plan — IPAI GitHub App Integration

> Technical plan for building the GitHub App as a Supabase-first integration.
> Status: Draft | Date: 2026-03-01

---

## 1. Primary Requirements

From the PRD:

1. Supabase Edge Functions: webhook ingestion, token brokering, write-back actions
2. Supabase tables: `ops.github_events`, `ops.github_installations`
3. SSOT artifacts: integration registration, secrets, installation mappings
4. Platform contract (C-19)
5. Optional: Odoo thin connector (`ipai_github_connector`)

---

## 2. Technical Context

| Dimension | Value |
|-----------|-------|
| Runtime | Supabase Edge Functions (Deno/TypeScript) |
| Database | Supabase PostgreSQL (`ops` schema) |
| Auth | GitHub App JWT (RS256) + installation tokens |
| Webhooks | HMAC-SHA256 via `X-Hub-Signature-256` |
| Secrets | Supabase Vault (private key, webhook secret, app ID) |
| Optional Odoo | Python 3.12+ / Odoo 19.0 CE |

---

## 3. Architecture

### System Topology

```
GitHub ──webhook──▶ Supabase Edge Function (github-app-webhook)
                       │
                       ├── verify signature (HMAC-SHA256)
                       ├── dedupe by X-GitHub-Delivery
                       ├── persist to ops.github_events
                       └── route by event type
                              │
                              ├── PR events ──▶ handler (comment, check)
                              ├── Issue events ──▶ handler (sync)
                              └── Check events ──▶ handler (Plane issue?)

Token broker:
Supabase Edge Function (github-app-token)
    │
    ├── load private key from Vault
    ├── generate RS256 JWT (iss=app_id, exp=10min)
    ├── POST /app/installations/{id}/access_tokens
    ├── cache token (TTL < 1h) keyed by installation_id
    └── return token to caller

Write-backs:
Supabase Edge Function (github-app-actions)
    │
    ├── obtain installation token from broker
    ├── POST /repos/{owner}/{repo}/issues/{n}/comments
    ├── POST /repos/{owner}/{repo}/check-runs
    └── POST /repos/{owner}/{repo}/issues
```

### Odoo Integration (Optional, Thin)

```
Odoo (ipai_github_connector)
    │
    ├── calls Supabase Edge Functions for:
    │   ├── "link this record to GitHub PR/issue"
    │   ├── "get PR status"
    │   └── "create issue from ticket"
    │
    └── stores: github_object_type, github_object_url,
                github_repo, linked_at
```

### Key Design Decisions

**D1: Supabase is the control plane, not Odoo.** GitHub App auth requires RS256 JWT generation, which is a crypto operation best handled by Supabase Edge Functions (Deno has native `crypto.subtle`). Odoo's role is limited to linking records to GitHub objects.

**D2: Token caching in Supabase.** Installation tokens (1h TTL) are cached in a `ops.github_token_cache` table or in-memory KV. The broker handles concurrent requests without thundering herd (lock on cache miss per installation_id).

**D3: Event routing by `X-GitHub-Event` header.** The webhook function reads the event type and dispatches to typed handlers. Unknown events are stored but not processed (logged as `unhandled`).

**D4: Append-only ops tables.** `ops.github_events` is append-only (per SSOT rule 5 for ops schema). Processing state tracked via `processed` boolean + `processed_at` timestamp.

---

## 4. System of Record Matrix

| Domain | SSOT Owner | Role |
|--------|-----------|------|
| GitHub repos, PRs, issues, checks | **GitHub** | Authoritative; Supabase mirrors events. |
| GitHub App config (permissions, events) | **GitHub Developer Settings** | Must have corresponding SSOT YAML in repo. |
| Webhook events, installation mappings | **Supabase** (`ops.*`) | Derived state from GitHub events. |
| Secrets (private key, webhook secret) | **Supabase Vault** | Never in Odoo or Git. |
| Odoo record ↔ GitHub object links | **Odoo** (`ipai_github_connector`) | Optional; Odoo-local state only. |

---

## 5. Failure-Mode Semantics

| Scenario | Behavior |
|----------|----------|
| Webhook signature invalid | Return `401`. Do not store or process. |
| Duplicate `X-GitHub-Delivery` | Return `200`. No side effects. |
| Token broker: private key missing | Return `503 KEY_MISSING` with `ssot_ref`. |
| Token broker: GitHub API returns error | Return `502` with error details. Caller retries. |
| Write-back fails (PR comment, check run) | Log error with GitHub API response. Mark event as `processed=false`, `error` field set. |
| Unknown event type | Store in `ops.github_events` with `processed=false`, `event_type=<type>`. Log as `unhandled`. |

---

## 6. Security Model

### JWT Generation

```
Header:  { "alg": "RS256", "typ": "JWT" }
Payload: { "iss": APP_ID, "iat": now - 60, "exp": now + 600 }
Sign:    RS256(private_key, header + payload)
```

### Webhook Verification

```
expected = HMAC-SHA256(webhook_secret, raw_body)
actual = X-Hub-Signature-256 header (strip "sha256=" prefix)
result = timing-safe comparison
```

### Permissions (v1 — Least Privilege)

| Permission | Access | Why |
|-----------|--------|-----|
| `issues` | `read` (v1), `write` (v2) | Read events; write for issue creation |
| `pull_requests` | `read` | PR events for Advisor |
| `checks` | `write` | Create check runs |
| `metadata` | `read` | Required (implicit) |

---

## 7. SSOT Artifacts

### Integration Registration

```yaml
# ssot/integrations/github_app_ipai.yaml
id: github_app_ipai
provider: github
category: devops_integration
description: "IPAI GitHub App for webhooks, installation tokens, and PR/issue automation"
surfaces: [webhooks, installation_tokens, checks, pr_comments]
required_secrets:
  - github_app_id
  - github_app_private_key_pem
  - github_webhook_secret
policy:
  audit_required: true
  idempotency_key: "github:delivery:{X-GitHub-Delivery}"
  allowlisted_events:
    - pull_request
    - pull_request_review
    - check_run
    - check_suite
    - issues
    - issue_comment
```

### Secrets Registry

```yaml
# ssot/secrets/registry.yaml (additions)
github_app_id:
  purpose: "GitHub App identifier for JWT iss claim"
  stores: [supabase_vault]
  consumers:
    - supabase_edge:github-app-token
  rotation: on_compromise

github_app_private_key_pem:
  purpose: "RS256 private key for GitHub App JWT signing"
  stores: [supabase_vault]
  consumers:
    - supabase_edge:github-app-token
  rotation: annually

github_webhook_secret:
  purpose: "HMAC-SHA256 webhook signature verification"
  stores: [supabase_vault]
  consumers:
    - supabase_edge:github-app-webhook
  rotation: annually
```

---

## 8. Constitutional Compliance

| Constraint | How addressed |
|-----------|---------------|
| C1 (GitHub App) | Using GitHub App, not PATs or OAuth Apps. |
| C2 (Supabase control plane) | All auth + webhook processing in Edge Functions. |
| C3 (Private key in Vault) | Vault only; never in Git, logs, or Odoo. |
| C4 (Webhook verification) | HMAC-SHA256 on `X-Hub-Signature-256`. |
| C5 (Idempotency) | Dedupe by `X-GitHub-Delivery` UUID. |
| C6 (Short-lived tokens) | Installation tokens cached with TTL < 1h. |
| C7 (Least privilege) | v1 permissions: read issues/PRs, write checks. |
| C8 (Event allowlist) | 6 events subscribed (see SSOT YAML). |
| C9 (Secrets registry) | All 3 secrets in `ssot/secrets/registry.yaml`. |
| C10 (No console-only) | SSOT YAML mirrors GitHub App settings. |

---

## 9. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Private key exposure | Low | Critical | Vault-only storage; rotation runbook. |
| GitHub API rate limit (5000/h per installation) | Low | Medium | Token broker logs remaining; preemptive backoff. |
| Webhook delivery failures | Low | Medium | GitHub retries; dedupe handles re-delivery. |
| Supabase Edge Function cold starts | Medium | Low | Webhook returns 200 quickly; processing can be async. |
| Scope creep (too many permissions) | Medium | Medium | Constitution C7 enforces least-privilege review per PR. |

---

## 10. Verification Commands

```bash
# Test webhook signature verification
deno test supabase/functions/github-app-webhook/test.ts

# Test JWT generation
deno test supabase/functions/github-app-token/test.ts

# Validate SSOT integration registration
test -f ssot/integrations/github_app_ipai.yaml && echo "PASS" || echo "FAIL"

# Validate secrets registered
grep 'github_app_id' ssot/secrets/registry.yaml && echo "PASS" || echo "FAIL"
grep 'github_app_private_key_pem' ssot/secrets/registry.yaml && echo "PASS" || echo "FAIL"
grep 'github_webhook_secret' ssot/secrets/registry.yaml && echo "PASS" || echo "FAIL"

# Validate contract exists
test -f docs/contracts/GITHUB_APP_CONTRACT.md && echo "PASS" || echo "FAIL"
```

---

## 11. Handoff

After plan approval → generate tasks via `/speckit.tasks` → implement phase by phase.
