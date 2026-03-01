# PRD — IPAI GitHub App Integration

> Product Requirements Document for a first-class GitHub App integrated via Supabase Edge Functions.
> Status: Draft | Date: 2026-03-01

---

## 1. Feature Overview

### Problem

The repo uses ad-hoc GitHub interactions (PATs in CI, manual webhooks per repo). There is no centralized GitHub integration that:
- Receives webhooks across all installed repos/orgs
- Uses scoped, short-lived installation tokens
- Persists events to the ops ledger for observability
- Enables write-backs (PR comments, check runs, issue creation)

### Solution

Build an **IPAI GitHub App** as a Supabase-first integration:

1. **Supabase Edge Functions** handle webhook ingestion, JWT auth, installation token brokering, and event processing.
2. **SSOT artifacts** register the integration, secrets, and installation mappings.
3. **Optional Odoo connector** (`ipai_github_connector`) for linking Odoo records to GitHub objects.

### Why GitHub App (not OAuth App or PAT)

| Criterion | GitHub App | OAuth App | PAT |
|-----------|-----------|-----------|-----|
| Centralized webhooks | Yes (one URL) | No (per-repo setup) | No |
| Scoped tokens | Installation tokens (1h) | User tokens (long-lived) | User tokens (long-lived) |
| Service user required | No | Often yes | Yes |
| Granular permissions | Per-permission | Scope-based | Scope-based |

---

## 2. User Scenarios

### P1 — Must Have

| # | Scenario | Acceptance Criteria |
|---|---------|-------------------|
| US-1 | As a platform, I receive GitHub webhook events (PR, issue, check) at a single endpoint with verified signatures. | Edge Function validates `X-Hub-Signature-256`, deduplicates by `X-GitHub-Delivery`, stores in `ops.github_events`. |
| US-2 | As a platform, I can obtain installation access tokens for any installed repo/org without long-lived credentials. | Token broker generates JWT (RS256), exchanges for installation token, caches with TTL. |
| US-3 | As an ops engineer, I have an ops ledger of all GitHub events for observability and audit. | `ops.github_events` table with delivery ID, event type, repo, action, timestamp, processed flag. |

### P2 — Should Have

| # | Scenario | Acceptance Criteria |
|---|---------|-------------------|
| US-4 | As a platform, I can post PR comments with Advisor findings using installation tokens. | `github-app-actions` Edge Function creates PR comments via GitHub API. |
| US-5 | As a platform, I can create GitHub check runs with build/test results. | Edge Function creates check runs using the `checks: write` permission. |
| US-6 | As a platform, I can open GitHub issues from Advisor findings or Odoo tickets. | Edge Function creates issues using `issues: write` permission. |

### P3 — Nice to Have

| # | Scenario | Acceptance Criteria |
|---|---------|-------------------|
| US-7 | As a developer, I can link Odoo records to GitHub PRs/issues via `ipai_github_connector`. | Odoo module shows linked GitHub objects on record forms. |
| US-8 | As a platform, failed CI builds create Plane issues automatically. | Webhook handler for `check_run.completed` (conclusion=failure) calls Plane API to create issue. |

---

## 3. Functional Requirements

| ID | Description | Priority | Story |
|----|------------|----------|-------|
| FR-1 | Supabase Edge Function `github-app-webhook`: verify `X-Hub-Signature-256` (HMAC-SHA256), dedupe by `X-GitHub-Delivery`, persist to `ops.github_events`, route by event type. | P1 | US-1 |
| FR-2 | Supabase Edge Function `github-app-token`: generate RS256 JWT from App ID + private key, exchange for installation access token via `POST /app/installations/{id}/access_tokens`, cache with TTL < 1h per installation. | P1 | US-2 |
| FR-3 | Supabase table `ops.github_events` (delivery_id unique, event_type, action, repo_full_name, installation_id, payload JSONB, processed boolean, created_at). | P1 | US-3 |
| FR-4 | Supabase table `ops.github_installations` (installation_id, account_type, account_login, repos JSONB, permissions JSONB, events JSONB, created_at, updated_at). | P1 | US-1,2 |
| FR-5 | Supabase Edge Function `github-app-actions`: post PR comment, create check run, open issue — all using installation tokens from token broker. | P2 | US-4,5,6 |
| FR-6 | SSOT integration registration: `ssot/integrations/github_app_ipai.yaml` with event allowlist, required secrets, policies. | P1 | — |
| FR-7 | SSOT installation mappings: `ssot/mappings/github_installations.yaml` scaffold + Supabase table sync. | P1 | — |
| FR-8 | Optional Odoo module `ipai_github_connector`: thin bridge calling Supabase Edge Functions for GitHub object linking. | P3 | US-7 |

---

## 4. Non-Functional Requirements

### Security

- App private key in Supabase Vault only; never in Git or logs.
- Webhook signature verification is mandatory — no bypass path.
- Installation tokens cached in-memory with TTL; never persisted to disk.
- Least-privilege permissions; start with `issues: read`, `pull_requests: read`, `checks: write`.

### Reliability

- Webhook handler is idempotent (dedupe by `X-GitHub-Delivery`).
- Installation token cache handles concurrent requests (no thundering herd on expiry).
- Missing secret returns `503 KEY_MISSING` with `ssot_ref` — not silent failure.

### Observability

- All webhook events persisted to `ops.github_events` before processing.
- Token broker logs installation ID + expiry (not the token value).
- Failed write-backs logged with GitHub API error response.

---

## 5. Integration Points

### GitHub App Auth (2 layers)

**A) App authentication (JWT)**
- Generate JWT signed with RS256 using App private key.
- Claims: `iss` = App ID, `iat` = now - 60s, `exp` = now + 10min.
- Header: `Authorization: Bearer <JWT>`.

**B) Installation authentication**
- Exchange JWT for installation access token: `POST /app/installations/{INSTALLATION_ID}/access_tokens`.
- Response includes `token` (1h TTL) and `permissions`.
- All repo/org API calls use: `Authorization: token <installation_token>`.

### GitHub Webhooks

- **Signature**: `X-Hub-Signature-256` = `sha256=<HMAC-SHA256(secret, payload)>`.
- **Delivery ID**: `X-GitHub-Delivery` (UUID) for idempotency.
- **Event header**: `X-GitHub-Event` (e.g., `pull_request`, `issues`, `check_run`).

### Event Allowlist (v1)

| Event | Actions | Permission Required |
|-------|---------|-------------------|
| `pull_request` | `opened`, `closed`, `merged`, `synchronize` | `pull_requests: read` |
| `pull_request_review` | `submitted` | `pull_requests: read` |
| `check_run` | `completed` | `checks: read` |
| `check_suite` | `completed` | `checks: read` |
| `issues` | `opened`, `closed`, `labeled` | `issues: read` |
| `issue_comment` | `created` | `issues: read` |

---

## 6. Success Criteria

| Metric | Target |
|--------|--------|
| Webhook signature verification | Valid + invalid + missing tested |
| Idempotency | Duplicate `X-GitHub-Delivery` = no-op |
| Token broker | Generates valid JWT; obtains installation token; caches correctly |
| Ops ledger | All webhook events persisted to `ops.github_events` |
| Secrets registered | All 3 secrets in `ssot/secrets/registry.yaml` |
| Integration registered | `ssot/integrations/github_app_ipai.yaml` committed |
| Platform contract | `docs/contracts/GITHUB_APP_CONTRACT.md` committed |

---

## 7. Out of Scope

- GitHub Enterprise Server support (cloud-first; add later if needed).
- Full Odoo ↔ GitHub bidirectional sync (Plane is the PM layer, not GitHub Issues directly).
- GitHub Actions workflow generation (separate concern; CI workflows are already managed in `.github/workflows/`).
