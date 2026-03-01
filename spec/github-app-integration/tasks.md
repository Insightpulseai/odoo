# Tasks — IPAI GitHub App Integration

> Task breakdown for implementing the GitHub App as a Supabase-first integration.
> Generated from: plan.md | Date: 2026-03-01

---

## Legend

- **ID**: `T-<phase>.<seq>` (e.g., T-1.1)
- **P**: Parallelizable with other tasks in same phase? (Y/N)
- **US#**: User Story reference from PRD
- **Dep**: Dependency on other task(s)

---

## Phase 1: SSOT & Governance

| ID | Task | P | US# | Dep | Status |
|----|------|---|-----|-----|--------|
| T-1.1 | Create `ssot/integrations/github_app_ipai.yaml` with: id, provider, category, surfaces, required_secrets, policy (audit, idempotency key, event allowlist) | Y | — | — | ☐ |
| T-1.2 | Register secrets in `ssot/secrets/registry.yaml`: `github_app_id` (stores: supabase_vault, consumers: github-app-token), `github_app_private_key_pem` (stores: supabase_vault, consumers: github-app-token, rotation: annually), `github_webhook_secret` (stores: supabase_vault, consumers: github-app-webhook, rotation: annually) | Y | — | — | ☐ |
| T-1.3 | Create `ssot/mappings/github_installations.yaml` scaffold (org/repo → installation_id mapping template) | Y | — | — | ☐ |
| T-1.4 | Create `docs/contracts/GITHUB_APP_CONTRACT.md` (C-19): source = Supabase Edge Functions, consumer = GitHub API, protocol = webhooks + REST, invariants (signature, dedupe, least-privilege), validator | Y | — | — | ☐ |
| T-1.5 | Add C-19 row to `docs/contracts/PLATFORM_CONTRACTS_INDEX.md` | N | — | T-1.4 | ☐ |
| T-1.6 | Update `docs/architecture/PLATFORM_REPO_TREE.md` SSOT Assignment Table: add `supabase/functions/github-app-*` and `ssot/integrations/github_app_ipai.yaml` paths | Y | — | — | ☐ |

---

## Phase 2: Supabase Schema (Migrations)

| ID | Task | P | US# | Dep | Status |
|----|------|---|-----|-----|--------|
| T-2.1 | Create Supabase migration: `ops.github_events` table (delivery_id TEXT UNIQUE, event_type TEXT, action TEXT, repo_full_name TEXT, installation_id BIGINT, payload JSONB, processed BOOLEAN DEFAULT false, processed_at TIMESTAMPTZ, error TEXT, created_at TIMESTAMPTZ DEFAULT now()) | Y | US-3 | — | ☐ |
| T-2.2 | Create Supabase migration: `ops.github_installations` table (installation_id BIGINT PRIMARY KEY, account_type TEXT, account_login TEXT, repos JSONB, permissions JSONB, events JSONB, created_at TIMESTAMPTZ DEFAULT now(), updated_at TIMESTAMPTZ DEFAULT now()) | Y | US-1,2 | — | ☐ |
| T-2.3 | Add RLS policies: `ops.github_events` and `ops.github_installations` restricted to service_role only | Y | — | T-2.1,T-2.2 | ☐ |

---

## Phase 3: Edge Functions — Core

| ID | Task | P | US# | Dep | Status |
|----|------|---|-----|-----|--------|
| T-3.1 | Implement `supabase/functions/github-app-webhook/index.ts`: read `X-Hub-Signature-256`, verify HMAC-SHA256 using webhook secret from Vault, reject invalid | N | US-1 | T-2.1 | ☐ |
| T-3.2 | Add deduplication to webhook function: check `X-GitHub-Delivery` against `ops.github_events.delivery_id`, skip if exists | N | US-1 | T-3.1 | ☐ |
| T-3.3 | Add event persistence: insert into `ops.github_events` with all fields, return `200` | N | US-1,3 | T-3.2 | ☐ |
| T-3.4 | Add event routing: read `X-GitHub-Event` header, dispatch to typed handlers (PR, issue, check); log unknown events as `unhandled` | N | US-1 | T-3.3 | ☐ |
| T-3.5 | Implement `supabase/functions/github-app-token/index.ts`: load private key from Vault, generate RS256 JWT (iss=app_id, iat=now-60s, exp=now+10min) | N | US-2 | T-1.2 | ☐ |
| T-3.6 | Add installation token exchange: `POST /app/installations/{id}/access_tokens` using JWT, parse response token + expiry | N | US-2 | T-3.5 | ☐ |
| T-3.7 | Add token caching: store token per installation_id with TTL < expiry; handle concurrent requests (cache-aside pattern) | N | US-2 | T-3.6 | ☐ |

---

## Phase 4: Tests

| ID | Task | P | US# | Dep | Status |
|----|------|---|-----|-----|--------|
| T-4.1 | Unit tests for webhook signature verification: valid signature, invalid signature, missing header, empty payload | Y | US-1 | T-3.1 | ☐ |
| T-4.2 | Unit tests for deduplication: new delivery processed, duplicate delivery skipped | Y | US-1 | T-3.2 | ☐ |
| T-4.3 | Unit tests for JWT generation: correct claims (iss, iat, exp), valid RS256 signature | Y | US-2 | T-3.5 | ☐ |
| T-4.4 | Unit tests for installation token exchange: successful exchange, error handling (401, 404, rate limit) | Y | US-2 | T-3.6 | ☐ |
| T-4.5 | Unit tests for token cache: cache hit (return cached), cache miss (fetch new), cache expired (fetch new), concurrent access | Y | US-2 | T-3.7 | ☐ |

---

## Phase 5: Edge Functions — Write-Backs (P2)

| ID | Task | P | US# | Dep | Status |
|----|------|---|-----|-----|--------|
| T-5.1 | Implement `supabase/functions/github-app-actions/index.ts`: action router for `comment`, `check_run`, `issue` | N | US-4,5,6 | T-3.7 | ☐ |
| T-5.2 | Add PR comment action: obtain installation token, `POST /repos/{owner}/{repo}/issues/{n}/comments` | N | US-4 | T-5.1 | ☐ |
| T-5.3 | Add check run action: `POST /repos/{owner}/{repo}/check-runs` with name, status, conclusion, output | N | US-5 | T-5.1 | ☐ |
| T-5.4 | Add issue creation action: `POST /repos/{owner}/{repo}/issues` with title, body, labels | N | US-6 | T-5.1 | ☐ |
| T-5.5 | Unit tests for write-back actions: successful post, auth failure, rate limit handling | Y | US-4,5,6 | T-5.2,T-5.3,T-5.4 | ☐ |

---

## Phase 6: Odoo Connector (P3, Optional)

| ID | Task | P | US# | Dep | Status |
|----|------|---|-----|-----|--------|
| T-6.1 | Scaffold `addons/ipai/ipai_github_connector/` module (manifest, models, security, data) | N | US-7 | — | ☐ |
| T-6.2 | Implement `github_link` mixin model: fields `github_object_type`, `github_object_url`, `github_repo`, `linked_at` | N | US-7 | T-6.1 | ☐ |
| T-6.3 | Add helper methods: `_github_link_pr(repo, pr_number)`, `_github_link_issue(repo, issue_number)` — calls Supabase Edge Functions, not GitHub API directly | N | US-7 | T-6.2 | ☐ |
| T-6.4 | Add form view widget showing linked GitHub objects | N | US-7 | T-6.3 | ☐ |

---

## Phase 7: Cross-Platform (P3, Optional)

| ID | Task | P | US# | Dep | Status |
|----|------|---|-----|-----|--------|
| T-7.1 | Add webhook handler for `check_run.completed` (conclusion=failure): call Plane API to create issue using `ipai_plane_connector` | N | US-8 | T-3.4, Plane spec Phase 1 | ☐ |
| T-7.2 | Unit test for GitHub → Plane issue creation on build failure | N | US-8 | T-7.1 | ☐ |

---

## Task Dependencies (ASCII)

```
Phase 1 (SSOT) — mostly parallel
  T-1.1, T-1.2, T-1.3, T-1.6 — independent
  T-1.4 → T-1.5 (index depends on contract)

Phase 2 (Schema) — parallel
  T-2.1, T-2.2 — independent
  T-2.3 — depends on T-2.1 + T-2.2

Phase 3 (Edge Functions) — two parallel tracks
  Webhook track: T-3.1 → T-3.2 → T-3.3 → T-3.4
  Token track:   T-3.5 → T-3.6 → T-3.7

Phase 4 (Tests) — all parallel, each depends on Phase 3 counterpart

Phase 5 (Write-backs) — sequential, depends on token broker
  T-5.1 → T-5.2, T-5.3, T-5.4 (parallel) → T-5.5

Phase 6 (Odoo) — sequential, independent of Edge Functions
  T-6.1 → T-6.2 → T-6.3 → T-6.4

Phase 7 (Cross-platform) — depends on both GitHub + Plane specs
  T-7.1 → T-7.2
```

---

## Merge Gates (CI-Enforced)

| Gate | Phase | Requirement | Enforcement |
|------|-------|-------------|-------------|
| **Gate A** (Signature) | Phase 4 | Webhook signature verification tests pass (valid/invalid/missing). | `github-app-webhook/test.ts` |
| **Gate B** (Schema) | Phase 2 | `ops.github_events.delivery_id` has UNIQUE constraint. | Migration validation |
| **Gate C** (SSOT) | Phase 1 | `ssot/secrets/registry.yaml` has entries for all 3 GitHub App secrets. | `ssot-surface-guard.yml` |
| **Gate D** (JWT) | Phase 4 | JWT generation tests pass (correct claims, valid RS256 signature). | `github-app-token/test.ts` |

---

## Implementation Strategy

**MVP-first**: Phases 1–4 form the MVP. Ship SSOT artifacts, schema, webhook + token Edge Functions, and tests together.

**Phase 5** (write-backs) ships when a concrete use case is prioritized (e.g., Advisor PR comments).

**Phase 6** (Odoo connector) ships only if Odoo users need GitHub object links on forms.

**Phase 7** (cross-platform GitHub → Plane) ships after both specs are implemented.

---

## Progress Tracking

| Phase | Tasks | Done | % |
|-------|-------|------|---|
| 1. SSOT & Governance | 6 | 0 | 0% |
| 2. Supabase Schema | 3 | 0 | 0% |
| 3. Edge Functions (Core) | 7 | 0 | 0% |
| 4. Tests | 5 | 0 | 0% |
| 5. Write-Backs (P2) | 5 | 0 | 0% |
| 6. Odoo Connector (P3) | 4 | 0 | 0% |
| 7. Cross-Platform (P3) | 2 | 0 | 0% |
| **Total** | **32** | **0** | **0%** |
