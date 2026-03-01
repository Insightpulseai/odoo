# Plane App Connector — Architecture Reference

> **Status**: Planned
> **SSOT**: `ssot/integrations/plane_webhooks.yaml`, `ssot/integrations/plane_mcp.yaml`
> **Secrets**: `ssot/secrets/registry.yaml` — `plane_api_key`, `plane_oauth_client_id`, `plane_oauth_client_secret`
> **Last updated**: 2026-03-01

---

## 1. Integration Model

Plane.so is treated as an **external System of Work (SoW)**. The integration follows the same boundary doctrine as all SoW connectors:

- Plane is a **read-only source of truth** by default.
- All Plane data is **mirrored** into a `work_plane.*` schema in Supabase (safe default — no direct writes back to Plane unless an explicit writeback policy is activated per workspace).
- Internal `work.*` tables remain the canonical SoW for all IPAI agents; `work_plane.*` is a mirror layer, not a primary source.
- No Plane credentials are ever stored in Odoo, in Vercel environment variables, or in browser-side code.

---

## 2. Boundary Diagram

```
External (Plane.so)                    Internal (Supabase / IPAI)
─────────────────────────────          ─────────────────────────────────────────
                                       supabase/functions/
Plane REST API ──────────────────────► plane-sync/          ──► work_plane.*
                    (backfill +        (API worker)              (mirror schema)
                     incremental)

Plane Webhooks ──────────────────────► plane-webhook/       ──► ops.event_queue ──► worker ──► work_plane.*
                    (real-time)        (ingest + validate)

Plane MCP Server ────────────────────► Agent (ops.run_events log)
  (developers.plane.so)               (direct MCP calls; every
                                       action logged)

                                       [Writeback — DISABLED by default]
work_plane.* ────────────────────────► writeback-worker ──► Plane REST API
                    (only when          (policy gate required per workspace)
                     policy = enabled)
```

---

## 3. OAuth2 Flow

Plane supports OAuth2 Authorization Code flow for user-scoped access. The connector implements:

1. **Authorization redirect**: IPAI redirects the user to Plane's OAuth2 authorization endpoint with `client_id`, `redirect_uri`, `scope`, and `state` (CSRF token).
2. **Code exchange**: Plane redirects back to `supabase/functions/plane-oauth-callback/` with an authorization code.
3. **Token exchange**: The callback handler POSTs to Plane's token endpoint using `client_id` + `client_secret` (read from Supabase Vault) to obtain `access_token` and `refresh_token`.
4. **Token storage**: Tokens are stored as a **reference** in Supabase Vault, keyed by `workspace_slug + user_id`. The raw token value never leaves Vault.
5. **Token refresh**: The sync worker refreshes tokens proactively before expiry using the stored `refresh_token` ref.

**Credential locations**:

| Credential | Store | Key |
|---|---|---|
| `plane_oauth_client_id` | Supabase Vault | `plane_oauth_client_id` |
| `plane_oauth_client_secret` | Supabase Vault | `plane_oauth_client_secret` |
| Per-user `access_token` ref | Supabase Vault | `plane_token:{workspace_slug}:{user_id}` |
| Per-user `refresh_token` ref | Supabase Vault | `plane_refresh:{workspace_slug}:{user_id}` |

---

## 4. Webhook Ingestion

### 4.1 Endpoint

`supabase/functions/plane-webhook/` handles all inbound Plane webhook payloads.

### 4.2 Shared Secret Validation

Plane may not sign webhooks cryptographically (verify against current Plane docs at integration time). Until native signing is confirmed:

- Embed a shared secret in the webhook URL path or a custom header (`X-Plane-Webhook-Secret`).
- Validate the secret on every request **before** touching the payload body.
- Return HTTP 401 on mismatch; do not log the payload on failure.
- Rotate the shared secret on team member offboarding.

### 4.3 Idempotency

Plane sends a unique event ID with each webhook. The ingest handler:

1. Extracts the Plane event ID from the payload.
2. Checks `ops.event_queue` for a row with `idempotency_key = 'plane:event:{event_id}'`.
3. If found: returns HTTP 200 without re-enqueuing (silent dedup).
4. If not found: inserts a new `ops.event_queue` row and returns HTTP 200.

The `ops.event_queue.idempotency_key` column has a `UNIQUE` constraint — duplicate inserts raise a constraint error that is caught and silently ignored.

### 4.4 Processing

The worker consumes `ops.event_queue` rows and upserts into the appropriate `work_plane.*` table based on the event type (`issue.created`, `cycle.updated`, `page.deleted`, etc.).

---

## 5. Mirror Schema Plan

The `work_plane` schema mirrors the key Plane object types needed for agent workflows:

| Table | Source | Notes |
|---|---|---|
| `work_plane.installations` | OAuth install record | One row per workspace installation |
| `work_plane.tokens_ref` | Vault key references | Maps workspace+user to Vault key names; never stores raw tokens |
| `work_plane.projects` | Plane projects | Mirrors `GET /workspaces/{slug}/projects/` |
| `work_plane.items` | Plane issues / cycles / modules | Unified item table; `item_type` discriminator column |
| `work_plane.pages` | Plane pages (wiki) | Mirrors Plane page content for agent RAG |
| `work_plane.events_cursor` | Sync state | Tracks last synced page/cursor per workspace for incremental sync |

All tables include:
- `plane_id` (text, unique within workspace) — Plane's own ID
- `workspace_slug` (text) — tenant identifier
- `synced_at` (timestamptz) — last mirror update
- `raw` (jsonb) — full Plane API response for forward compatibility

---

## 6. Writeback Policy

Writeback to Plane is **disabled by default**. It must be explicitly enabled per workspace:

```sql
UPDATE work_plane.installations
SET writeback_policy = 'enabled'
WHERE workspace_slug = '<slug>';
```

When enabled:
- The writeback worker reads pending `work_plane.*` changes flagged with `needs_sync = true`.
- It uses optimistic locking: Plane's `updated_at` timestamp is used as an ETag.
- On conflict (stale write), the worker logs the conflict in `ops.run_events` and skips the write.
- Conflict resolution policy must be documented per workspace before enabling writeback.

**Never enable writeback in a workspace without a documented conflict resolution policy.**

---

## 7. MCP Server

Plane exposes an MCP server at `developers.plane.so`. IPAI agents can call Plane operations directly via the MCP protocol without going through the REST API.

Rules for MCP agent calls:

- Every agent action against Plane via MCP **must** be logged in `ops.run_events` with:
  - `source: 'plane_mcp'`
  - `workspace_slug`
  - `action` (e.g., `issue.create`, `cycle.update`)
  - `plane_response_status`
- MCP calls that modify Plane state are subject to the same writeback policy gate as the REST writeback worker.
- MCP credentials (API key or OAuth token ref) are read from Supabase Vault at call time; never cached in agent memory.

---

## 8. Secrets Map

| Secret name | Purpose | Store | Rotation trigger |
|---|---|---|---|
| `plane_api_key` | X-API-Key for sync worker | Supabase Vault | Team member offboarding or Plane workspace credential reset |
| `plane_oauth_client_id` | OAuth2 app client ID | Supabase Vault | Plane app re-registration |
| `plane_oauth_client_secret` | OAuth2 app client secret | Supabase Vault | Plane app re-registration or exposure |
| `plane_token:{slug}:{user_id}` | Per-user access token ref | Supabase Vault | Token expiry or user revocation |
| `plane_refresh:{slug}:{user_id}` | Per-user refresh token ref | Supabase Vault | Token expiry or user revocation |

All secrets follow the `ssot/secrets/registry.yaml` policy:
- Never in GitHub Actions secrets
- Never in Vercel environment variables
- Never in browser-side code or logs

---

## 9. Tenant Mapping

Plane workspaces map to IPAI internal spaces as follows:

| Plane concept | IPAI mapping |
|---|---|
| `workspace_slug` | `work_plane.installations.workspace_slug` (canonical tenant key) |
| Plane workspace | `work.space_id` (internal space identifier) |
| Plane project | `work_plane.projects.id` → linked to `work.space_id` |
| Plane issue | `work_plane.items` (item_type = 'issue') |

The mapping is stored in `work_plane.installations`:

```sql
-- Example row
SELECT workspace_slug, space_id, writeback_policy
FROM work_plane.installations
WHERE workspace_slug = 'insightpulseai';
-- workspace_slug | space_id (UUID) | writeback_policy
-- insightpulseai | <uuid>           | disabled
```

---

## 10. Future Work

Once the mirror schema is stable and validated:

1. **work.templates parity**: Evaluate whether Plane's templates, recurring issues, and automation rules can be expressed in `work.templates` for cross-platform portability.
2. **Bidirectional sync**: Define conflict resolution policy per workspace, then enable writeback selectively.
3. **Agent integration**: Surface `work_plane.items` and `work_plane.pages` in the SoW RAG index (`work.search_index`) so agents can answer questions about Plane content.
4. **Analytics bridge**: Expose `work_plane.*` tables via the Superset analytics bridge for PM reporting.

---

## References

- `ssot/integrations/plane_webhooks.yaml` — integration SSOT
- `ssot/integrations/plane_mcp.yaml` — MCP agent SSOT (planned)
- `ssot/secrets/registry.yaml` — secret identifiers and storage policy
- `docs/architecture/SOW_BOUNDARY.md` — SoW boundary doctrine
- Plane REST API: `https://api.plane.so/api/v1/`
- Plane MCP Server: `https://developers.plane.so` (MCP endpoint)
