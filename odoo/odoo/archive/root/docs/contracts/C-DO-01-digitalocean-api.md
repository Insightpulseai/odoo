# C-DO-01 — DigitalOcean API Provider Contract

> **Contract ID**: C-DO-01 (Platform Contracts Index: C-18)
> **Status**: Active
> **Owner**: Platform Engineering
> **Last Updated**: 2026-03-01

---

## 1. Scope

This contract governs all automated interactions with the DigitalOcean v2 REST API from
within the InsightPulse AI platform. It covers:

- Inventory ingestion (droplets, managed databases, firewalls, VPC, networking)
- Action dispatch (future: restart, resize, firewall rule patch)
- Audit logging of every API interaction
- Error, retry, and rate-limit handling

Manual `doctl` CLI usage by operators is **not** regulated by this contract but should
follow the same authentication and audit principles.

---

## 2. Authentication

| Item | Value |
|------|-------|
| Auth method | HTTP Bearer token |
| Header | `Authorization: Bearer <DO_API_TOKEN>` |
| Token SSOT | `ssot/secrets/registry.yaml → digitalocean_api_token` |
| Runtime store | Supabase Vault (`vault.secrets` key: `digitalocean_api_token`) |
| Local dev store | macOS Keychain (`ipai/do_api_token`) |
| CI store | GitHub Actions secret `DO_API_TOKEN` |
| **Forbidden** | Hardcoding token in any file tracked by git |

Token scopes required (minimum):

| Scope | Why |
|-------|-----|
| `droplet:read` | List and describe Droplets |
| `database:read` | List Managed Database clusters |
| `firewall:read` | List Firewall rules |
| `vpc:read` | VPC / private network topology |
| `load_balancer:read` | Load balancer inventory |
| `domain:read` | DNS / domain record verification |
| `monitoring:read` | Alert policies and metrics |
| `project:read` | Project / tag grouping |

Write scopes (for future action dispatch — not required by MVP ingest):

| Scope | Why |
|-------|-----|
| `droplet:create`, `droplet:delete` | Lifecycle automation (post-MVP) |
| `firewall:write` | Policy enforcement (post-MVP) |

---

## 3. Base URL and Versioning

```
https://api.digitalocean.com/v2
```

- All endpoints use HTTPS.
- API version is path-embedded (`/v2/`); no header versioning.
- Breaking changes are announced via DO changelog and will require a contract revision.

---

## 4. Pagination

DigitalOcean v2 uses **offset pagination** via query parameters:

| Parameter | Description | Default | Max |
|-----------|-------------|---------|-----|
| `page` | Page number (1-indexed) | 1 | — |
| `per_page` | Items per page | 20 | 200 |

Response envelope:

```json
{
  "resource_type": [...],
  "links": {
    "pages": {
      "next": "https://api.digitalocean.com/v2/droplets?page=2&per_page=200",
      "last": "..."
    }
  },
  "meta": { "total": 42 }
}
```

**Ingestion rule**: Always paginate until `links.pages.next` is absent. Use `per_page=200`
to minimize round-trips.

---

## 5. Rate Limits

| Limit | Value |
|-------|-------|
| Default rate limit | 5,000 requests / hour |
| Header: remaining | `RateLimit-Remaining` |
| Header: reset at | `RateLimit-Reset` (Unix timestamp) |
| HTTP status on limit | `429 Too Many Requests` |

**Retry policy** (mandatory for all ingest workers):

1. On `429`: read `Retry-After` header (seconds); if absent, wait 60 seconds.
2. On `5xx` (500, 502, 503, 504): exponential backoff — 2ˢ seconds, s = attempt number (1..5).
3. Max retries: **5** per resource type per ingest run.
4. After 5 failures: mark ingest run as `partial`, record `last_error`, continue to next resource.
5. Never retry `4xx` except `429`.

---

## 6. Resources in Scope (MVP)

| Resource | Endpoint | `ops` table |
|----------|----------|-------------|
| Droplets | `GET /v2/droplets` | `ops.do_droplets` |
| Managed Databases | `GET /v2/databases` | `ops.do_databases` |
| Firewalls | `GET /v2/firewalls` | `ops.do_firewalls` |
| Actions (audit) | per-resource action log | `ops.do_actions` |

Post-MVP (tracked in `ssot/providers/digitalocean/provider.yaml`):

- Load Balancers, VPC networks, Snapshots/Backups, Spaces (object storage), Projects/Tags

---

## 7. Idempotency and Audit Logging

Every ingest run **MUST**:

1. Insert a row in `ops.do_ingest_runs` at start (`status='running'`).
2. Upsert each resource into its `ops.do_*` table using `ON CONFLICT (do_id) DO UPDATE`.
3. Write a row to `ops.run_events` for each resource type processed (count, errors).
4. Update `ops.do_ingest_runs` at end with `status='success'|'partial'|'error'`, `counts`, `finished_at`.

Action dispatch (post-MVP) **MUST**:

1. Insert pre-action row to `ops.do_actions` with `status='pending'`.
2. Call DO API.
3. Update `ops.do_actions` with `status='success'|'error'` and DO-returned `action_id`.

---

## 8. Client Module Requirements

The DO client (`supabase/functions/ops-do-ingest/client.ts` or equivalent) MUST implement:

- `baseUrl`: configurable, defaults to `https://api.digitalocean.com/v2`
- `auth(token: string)`: bearer token injection
- `paginate<T>(path: string): AsyncGenerator<T>`: full pagination traversal
- `withRetry(fn: () => Promise<Response>): Promise<Response>`: retry + backoff
- `typed error envelope`: `{ status, message, id }` from DO error body

---

## 9. CI Enforcement

| Guard | Workflow |
|-------|---------|
| Secret name used (not value) | `ssot-surface-guard.yml` |
| `digitalocean_api_token` in registry | `ssot-surface-guard.yml` |
| Migration covers all `ops.do_*` tables | `spec-validate.sh` |

---

## 10. Contract Change Process

Changes to this contract require:

1. PR updating this file and `docs/contracts/PLATFORM_CONTRACTS_INDEX.md`.
2. Corresponding SSOT and migration updates in the same PR.
3. At least one reviewer from Platform Engineering.

---

*Reference: [DigitalOcean API v2 Documentation](https://docs.digitalocean.com/reference/api/api-reference/)*
