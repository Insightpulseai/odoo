# FIGMA_INTEGRATION_SURFACE.md

> **SSOT**: `ssot/integrations/figma.yaml`
> **Status**: planned
> **Last reviewed**: 2026-03-01

Defines the surfaces adopted for Figma integration, boundary rules, auth approach,
and component ownership. This doc is the authoritative narrative companion to the
machine-readable SSOT at `ssot/integrations/figma.yaml`.

---

## 1. Integration Surface

We adopt the following Figma developer platform surfaces:

| Surface | Adoption | Purpose |
|---------|----------|---------|
| REST API v1 | Yes | Read files, components, variables, annotations |
| Webhooks V2 | Yes | React to library publish, file update, version update |
| Variables sync (CI) | Yes | Bidirectional tokens sync via GitHub Actions |
| MCP server | Yes | Claude Code agents access Figma context |
| Code Connect | Yes | Wire `packages/ui` components to Figma Dev Mode |
| Plugin API | No | Not adopted (browser-only; incompatible with CI/agent doctrine) |
| Widget API | No | Not adopted (canvas-only; out of scope) |

All surfaces are operated **API-first / no-UI**. No Figma-side configuration
is performed via the browser UI that cannot be reproduced from code.

---

## 2. Boundary Diagram

```
                       ┌──────────────────────────────────────────┐
                       │              Figma Platform               │
                       │  (Source of Record: design assets)        │
                       │                                           │
                       │  REST API v1      Webhooks V2             │
                       │  Variables API    MCP server              │
                       └───────────┬──────────────┬───────────────┘
                                   │              │
                    (OAuth2/PAT)   │              │  (webhook POST + HMAC verify)
                                   ▼              ▼
                       ┌───────────────────────────────────────────┐
                       │          supabase/functions/              │
                       │   figma-api/         figma-webhook/       │
                       │   (REST client)      (ingest + verify)    │
                       └───────────┬──────────────┬───────────────┘
                                   │              │
                    (enqueue)      │              │  (enqueue)
                                   ▼              ▼
                       ┌───────────────────────────────────────────┐
                       │              ops.runs (taskbus)            │
                       │         ops.run_events (audit log)         │
                       └───────────────────┬───────────────────────┘
                                           │
                              (workers pick up run items)
                                           ▼
                       ┌───────────────────────────────────────────┐
                       │               Workers / CI                 │
                       │   packages/design-tokens/tokens.json       │
                       │   packages/ui/ (Code Connect publish)      │
                       │   Claude Code agents (MCP bridge)          │
                       └───────────────────────────────────────────┘
```

**Key rules**:
- Figma is read surface in agent context (MCP bridge is read-only)
- Repo is canonical SoT for tokens after CI sync
- All agent activity is logged to `ops.run_events`

---

## 3. OAuth 2.0 + PAT Approach

### OAuth 2.0 (preferred for user-scoped access)

Use OAuth 2.0 when the integration acts on behalf of a specific Figma user
(e.g., Design team CI tasks, workspace-level variable reads).

- **Client ID / Secret**: stored in Supabase Vault (`figma_oauth_client_id`, `figma_oauth_client_secret`)
- **Token exchange**: server-side only (never in browser); token stored in Vault post-exchange
- **Scopes**: `file_read`, `file_variables:read`, `file_variables:write` (not `files:read`)
- **Scope policy**: `files:read` is prohibited (grants access to all org files); prefer `file_read` scoped to explicit file IDs

### Personal Access Token (internal automation only)

Use PAT for CI workflows, MCP server authentication, and agent tooling where
user-identity is not required.

- **Storage**: Supabase Vault (`figma_personal_access_token`) + os_keychain
- **Prohibited**: never in GitHub Actions env vars directly; inject via Vault read
- **Rotation**: on team member offboarding or suspected exposure

---

## 4. Webhooks V2

Figma Webhooks V2 are **API-managed only** — there is no UI for webhook CRUD.
This aligns with our no-UI SSOT doctrine.

### Creating a webhook

```
POST https://api.figma.com/v2/webhooks
Authorization: Bearer ${FIGMA_PERSONAL_ACCESS_TOKEN}
Content-Type: application/json

{
  "event_type": "LIBRARY_PUBLISH",
  "team_id": "<FIGMA_TEAM_ID>",
  "endpoint": "https://<project-ref>.supabase.co/functions/v1/figma-webhook",
  "passcode": "<figma_webhook_secret>",
  "status": "ACTIVE",
  "description": "Token sync trigger on library publish"
}
```

### Deleting a webhook

```
DELETE https://api.figma.com/v2/webhooks/{webhook_id}
Authorization: Bearer ${FIGMA_PERSONAL_ACCESS_TOKEN}
```

### Event types adopted

| Event | Purpose |
|-------|---------|
| `FILE_UPDATE` | Design file saved — low-frequency audit |
| `FILE_VERSION_UPDATE` | Explicit version checkpoint |
| `LIBRARY_PUBLISH` | Triggers variables/tokens sync pull |
| `FILE_COMMENT` | Optional: Slack notification of design comments |

### Signature verification

Every ingest must verify `x-figma-signature` (HMAC-SHA256 of payload using `figma_webhook_secret`).
Requests without a valid signature are rejected with HTTP 401. The secret is read from
Supabase Vault at function cold-start; if absent, the function refuses to start.

---

## 5. Variables Sync

Figma Variables map to design tokens in `packages/design-tokens/tokens.json`.
The repo is the **canonical source**; Figma is the consumer after a CI push.

### Flow

```
1. Designer updates tokens in packages/design-tokens/tokens.json (PR)
2. CI: .github/workflows/figma-variables-sync.yml
   → reads tokens.json
   → calls Figma Variables API (file_variables:write scope)
   → pushes changes to Figma file
3. (Optional) LIBRARY_PUBLISH webhook fires → supabase/functions/figma-webhook
   → enqueues ops.run to pull back and audit-verify repo ↔ Figma alignment
```

### Reference

Pattern adapted from [figma/variables-github-action-example](https://github.com/figma/variables-github-action-example).

### Generated artifact

`packages/design-tokens/tokens.json` — **never hand-edit Figma variables directly**.
Edit the YAML/JSON source, run `scripts/design/export_tokens.sh`, commit all generated files.

---

## 6. Code Connect

Code Connect wires Figma component definitions (in Dev Mode) to the actual React
components in `packages/ui/`, showing real component code instead of Figma-generated stubs.

### Publish workflow

```bash
pnpm figma connect publish
```

This reads `.figma/components.json` (generated from `packages/ui/` component config)
and publishes mappings to Figma via the Code Connect API.

### CI workflow

`.github/workflows/figma-code-connect-publish.yml` runs `pnpm figma connect publish`
on merge to `main` when `packages/ui/**` or `.figma/**` changes.

### Reference

[figma/code-connect](https://github.com/figma/code-connect)

---

## 7. MCP Server

The Figma MCP server exposes Figma context (files, components, variables, annotations)
to Claude Code agents as first-class tools.

### Configuration

`agents/mcp/figma.json` — standard MCP JSON config:

```json
{
  "mcpServers": {
    "figma": {
      "url": "https://api.figma.com/v1/ai/mcp",
      "headers": {
        "Authorization": "Bearer ${FIGMA_PERSONAL_ACCESS_TOKEN}"
      }
    }
  }
}
```

### Rate limits

Per [figma/mcp-server-guide](https://github.com/figma/mcp-server-guide):
- Respect Figma REST API rate limits (no batch polling loops)
- MCP tool calls are blocking; do not fan out parallel calls to the same file

### Agent constraints

- Agents access Figma via MCP in **read-only** mode
- All tool calls must emit an entry to `ops.run_events`
- `FIGMA_PERSONAL_ACCESS_TOKEN` is sourced from Supabase Vault at runtime

---

## 8. Secrets

All secrets are tracked in `ssot/secrets/registry.yaml`. No values are stored here.

| Secret identifier | Purpose | Stores |
|-------------------|---------|--------|
| `figma_oauth_client_id` | Figma OAuth2 app client ID | Supabase Vault, os_keychain |
| `figma_oauth_client_secret` | Figma OAuth2 app client secret (token exchange) | Supabase Vault, os_keychain |
| `figma_personal_access_token` | PAT for internal automation (CI, MCP, agents) | Supabase Vault, os_keychain |
| `figma_webhook_secret` | Shared secret for webhook signature verification | Supabase Vault, os_keychain |

**Prohibited stores** for all Figma secrets:
- `github_actions` (inject via Vault read, not direct env injection)
- `vercel_env` (browser-facing; server-only secrets must not reach browser)

---

## 9. Contract Enforcement

### SSOT

Machine-readable integration definition: `ssot/integrations/figma.yaml`

Figma is registered in the integration index at: `ssot/integrations/_index.yaml`

### CI gate (future)

A dedicated CI workflow (`.github/workflows/ssot-surface-guard.yml`) will validate:
- `figma_webhook_secret` present in Vault before webhook registration
- OAuth scope list does not include `files:read`
- `agents/mcp/figma.json` references `ssot/integrations/figma.yaml` in `_comment`

Until the CI gate is live, the contract is enforced by code review.

### Cross-boundary contract

This integration crosses the Figma design surface boundary into the Supabase/CI
execution domain. The contract doc is this file. Registered in:
`docs/contracts/PLATFORM_CONTRACTS_INDEX.md` (add entry when that index exists).
