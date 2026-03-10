# Plane Marketplace Integrations — Architecture Contract

> **Status**: planned (2026-03-01)
> **Owner**: ipai platform team
> **SSOT registry**: `ssot/integrations/plane.yaml`
> **Boundary doctrine**: `docs/architecture/SSOT_BOUNDARIES.md`

---

## Summary

Plane.so is the **Statement of Work (SoW)** surface for InsightPulse AI.
Marketplace integrations (MCP, GitHub, Slack, Sentry) are **SSOT-governed plugins**,
not ad-hoc SaaS toggles. Each integration has:

- A YAML file in `ssot/integrations/plane_*.yaml`
- An entry in `ssot/integrations/_index.yaml`
- A secrets entry in `ssot/secrets/registry.yaml`
- An audit trail via `ops.run_events`

---

## Integration Map

| Integration | Tier | Direction | Status | SSOT File | Edge Fn / MCP |
|---|---|---|---|---|---|
| Plane core (webhooks + API sync) | — | inbound | planned | `plane_webhooks.yaml` | `plane-webhook/`, `plane-sync/` |
| **Plane MCP (Claude / VS Code)** | T0 | bidirectional | planned | `plane_mcp.yaml` | `mcp/servers/plane/` |
| **GitHub ↔ Plane sync** | T1 | inbound primary | planned | `plane_github_sync.yaml` | `plane-github-sync/` |
| **Slack → Plane intake** | T1 | inbound | planned | `plane_slack_intake.yaml` | `apps/slack-agent/` |
| **Sentry → Plane issues** | T1 | inbound | planned | `plane_sentry_sync.yaml` | `sentry-plane-sync/` |

---

## Data Flow Overview

```
Slack threads ──────────────────────┐
                                    │ (intake)
GitHub PRs / issues ────────────────┤──▶ Plane Issues / Cycles / Modules
                                    │              │
Sentry errors ──────────────────────┘              │
                                                   │ webhook
                                       work_plane.* (mirror schema)
                                                   │
                                         ops.run_events (audit)
                                                   │
                                          Advisor SoW posture scan
```

```
Agents (Claude / VS Code)
    │
    │ MCP tool call
    ▼
mcp/servers/plane/index.ts
    │
    ├──▶ Plane REST API (read/write via tool_allowlist)
    │
    └──▶ ops.run_events (audit — required for every call)
```

---

## §MCP — Plane MCP Server

**Path**: `mcp/servers/plane/index.ts`
**SSOT**: `ssot/integrations/plane_mcp.yaml`

### Tool Allowlist

| Tool | Direction | Audit Required | Idempotency Required |
|---|---|---|---|
| `create_issue` | write | yes | yes |
| `update_issue` | write | yes | yes |
| `get_issue` | read | yes | no |
| `list_issues` | read | yes | no |
| `list_projects` | read | yes | no |
| `list_cycles` | read | yes | no |
| `list_modules` | read | yes | no |
| `search_pages` | read | yes | no |

### Required Environment Variables

| Variable | Source |
|---|---|
| `PLANE_API_KEY` | Supabase Vault → `plane_api_key` |
| `PLANE_WORKSPACE_ID` | Supabase Vault → `plane_workspace_id` |
| `SUPABASE_URL` | auto-injected |
| `SUPABASE_SERVICE_ROLE_KEY` | auto-injected |

### Claude Code registration

Add to `~/.claude/mcp-servers.json` (or project-local `.mcp.json`):

```json
{
  "plane": {
    "command": "node",
    "args": ["mcp/servers/plane/dist/index.js"],
    "env": {
      "PLANE_API_KEY": "<from Supabase Vault>",
      "PLANE_WORKSPACE_ID": "<workspace-slug>",
      "SUPABASE_URL": "<from env>",
      "SUPABASE_SERVICE_ROLE_KEY": "<from env>"
    }
  }
}
```

### Audit sink

Every tool call writes to `ops.run_events`:

```sql
-- verify audit coverage
SELECT tool_name, count(*), max(timestamp)
FROM ops.run_events
WHERE telemetry_source = 'plane_mcp'
GROUP BY tool_name
ORDER BY max(timestamp) DESC;
```

---

## §GitHub — GitHub ↔ Plane Sync

**Edge Function**: `supabase/functions/plane-github-sync/`
**SSOT**: `ssot/integrations/plane_github_sync.yaml`
**Mapping**: `ssot/mappings/plane_github.yaml`

### Data Flow

```
GitHub webhook (PR merged / issue closed)
  → X-GitHub-Delivery (idempotency key)
  → validate event type
  → extract Plane issue ID from branch / PR body
  → PATCH Plane issue state via API
  → write ops.runs + ops.run_events
```

### Linking convention

PRs must include one of:
- Branch name: `plane/{issue-uuid}` or `feat/plane/{issue-uuid}`
- PR body line: `plane-issue: {issue-uuid}`

### Setup

1. Fill `ssot/mappings/plane_github.yaml` with `plane_project_id` for each repo.
2. Create GitHub App / webhook pointing to:
   `https://<supabase-project>.supabase.co/functions/v1/plane-github-sync`
3. Set webhook events: `pull_request`, `issues`.
4. Inject `PLANE_GITHUB_MAPPING_JSON` as Supabase env var (serialized from mapping YAML).

---

## §Slack — Slack → Plane Intake

**Handler**: `apps/slack-agent/` (extension)
**SSOT**: `ssot/integrations/plane_slack_intake.yaml`

### Intake Triggers

| Trigger | Action |
|---|---|
| `:plane:` reaction on any message | Create Plane issue from thread context |
| `/plane create <title>` slash command | Interactive issue creation |

### Idempotency

Key: `{workspace_id}:{channel_id}:{thread_ts}`
Stored in: `work_plane.slack_intake_events`

### Bot reply format

```
✅ Created: [PLANE-42] Fix authentication timeout
→ https://app.plane.so/{workspace}/projects/{project}/issues/{id}/
```

### Setup

1. Add `:plane:` reaction emoji to Slack workspace.
2. Register `/plane` slash command in Slack App settings → `apps/slack-agent/`.
3. Add `PLANE_API_KEY` + `PLANE_WORKSPACE_ID` to Slack agent environment.
4. (Optional) Create `ssot/mappings/plane_slack_channels.yaml` to map channels → projects.

---

## §Sentry — Sentry → Plane Issues

**Edge Function**: `supabase/functions/sentry-plane-sync/`
**SSOT**: `ssot/integrations/plane_sentry_sync.yaml`
**Dedup table**: `work_plane.sentry_issues`

### Data Flow

```
Sentry alert webhook
  → validate HMAC-SHA256 (sentry-hook-signature)
  → check work_plane.sentry_issues for existing fingerprint
  → if new: POST to Plane API → upsert dedup row
  → if existing: update last_seen + occurrence_count (no Plane API call)
  → if resolved: PATCH Plane issue state to "Done"
  → write ops.run_events
```

### Priority mapping

| Sentry Level | Plane Priority |
|---|---|
| fatal | urgent |
| error | high |
| warning | medium |
| info | low |
| debug | none |

### Setup

1. Create `ssot/mappings/plane_sentry.yaml` mapping `sentry_project_slug → plane_project_id`.
2. Configure Sentry webhook in Sentry → Settings → Developer Settings → Webhooks:
   `https://<supabase-project>.supabase.co/functions/v1/sentry-plane-sync`
3. Set `SENTRY_WEBHOOK_SECRET` in Supabase Vault.
4. Inject `PLANE_SENTRY_MAPPING_JSON` as Supabase env var.

---

## Forbidden Patterns

| Pattern | Reason |
|---|---|
| UI-only integration toggle in Plane settings | Creates drift vs SSOT; integration not tracked in repo |
| Plane as System of Record (SoR) | Plane is SoW; canonical truth lives in `work.*/work_plane.*` |
| `plane_api_key` in Vercel env or browser | Server-only; `prohibited_consumers` in secrets registry |
| Edge Function hardcoding repo → project mappings | Mappings belong in `ssot/mappings/plane_github.yaml` |
| Sentry sync creating duplicate issues | `work_plane.sentry_issues` fingerprint dedup is mandatory |
| MCP tool calling Plane APIs outside tool_allowlist | Tool allowlist is the governance boundary |

---

## Writeback Policy

**Default**: all writeback disabled (Plane is consumed, not written to from internal systems).

To enable GitHub → Plane writeback (not currently needed):
1. Set `writeback_enabled: true` in `ssot/mappings/plane_github.yaml` for the target repo.
2. Document rationale in this file under a new §Writeback section.
3. Merge via PR with review.

---

## Advisor SoW Posture Scan

Once active, the Advisor scan (`ssot/integrations/plane.yaml §advisor_scan`) answers:

| Check | Query |
|---|---|
| MCP server healthy | `ops.run_events WHERE telemetry_source = 'plane_mcp'` |
| GitHub sync coverage | `ops.runs WHERE integration = 'plane_github_sync'` |
| Slack intake active | `ops.runs WHERE integration = 'plane_slack_intake'` |
| Sentry issue linkage | `work_plane.sentry_issues WHERE plane_issue_id IS NOT NULL` |

---

## Secrets Quick Reference

| Secret | Vault Key | Notes |
|---|---|---|
| `PLANE_API_KEY` | `plane_api_key` | X-API-Key header; server-only |
| `PLANE_WORKSPACE_ID` | `plane_workspace_id` | workspace slug for API paths |
| `PLANE_WEBHOOK_SECRET` | `plane_webhook_secret` | inbound webhook validation |
| `SENTRY_WEBHOOK_SECRET` | (to add) | Sentry HMAC signing secret |

Full registry: `ssot/secrets/registry.yaml §plane_*`

---

## Activation Checklist

- [ ] Plane workspace created and `plane_workspace_id` stored in Supabase Vault
- [ ] `plane_api_key` stored in Supabase Vault; `plane_webhook_secret` generated
- [ ] `ssot/mappings/plane_github.yaml` `plane_project_id` fields filled
- [ ] GitHub App webhook configured pointing to `plane-github-sync`
- [ ] MCP server built (`pnpm build` in `mcp/servers/plane/`) and registered in `.mcp.json`
- [ ] Slack bot invited to relevant channels; `:plane:` emoji registered
- [ ] Sentry webhook configured; `SENTRY_WEBHOOK_SECRET` in Vault
- [ ] `PLANE_GITHUB_MAPPING_JSON` + `PLANE_SENTRY_MAPPING_JSON` injected as Supabase env vars
- [ ] Advisor posture scan producing output (verify via `ops.run_events`)
