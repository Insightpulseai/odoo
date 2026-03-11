# C-SLACK-PLANE-01 — Two-App Slack Model (Plane + Pulser)

**Status**: Active
**Last updated**: 2026-03-01
**SSOT**: `ssot/integrations/slack/apps.yaml`
**Related**: `docs/contracts/C-PULSER-ODOO-01.md`

---

## Purpose

This contract defines the boundary between two separate Slack apps used by
InsightPulse AI: **Plane Slack** (product/project management UX) and **Pulser
Slack** (operations control plane). They must never be merged into a single
Slack app.

---

## Two-App Model

| Property | Plane Slack App | Pulser Slack App |
|----------|----------------|------------------|
| **Command** | `/plane` | `/pulser` |
| **Purpose** | Issues from Slack, unfurls, thread sync | Intent enqueue, status/gates/mail, fix workflows |
| **Base URL** | `https://plane.insightpulseai.com` | Socket Mode (no public URL required) |
| **Transport** | HTTP endpoints (webhooks) | Socket Mode (long-lived runner) |
| **OAuth** | Team + User OAuth (workspace installs) | Optional (bot token only) |
| **Owner** | Plane self-hosted platform | InsightPulse AI platform team |

---

## Plane Slack Endpoints

All endpoints are owned by Plane's self-hosted Slack integration:

| Endpoint | URL |
|----------|-----|
| Slash command | `https://plane.insightpulseai.com/silo/api/slack/command/` |
| Team OAuth callback | `https://plane.insightpulseai.com/silo/api/slack/team/auth/callback/` |
| User OAuth callback | `https://plane.insightpulseai.com/silo/api/slack/user/auth/callback/` |
| Events | `https://plane.insightpulseai.com/silo/api/slack/events` |
| Action (interactivity) | `https://plane.insightpulseai.com/silo/api/slack/action/` |
| Options (menus) | `https://plane.insightpulseai.com/silo/api/slack/options/` |

---

## Pulser Slack Surface

Pulser uses Socket Mode — no public HTTP endpoints for Slack events:

- **Slash command**: `/pulser` (parsed by `supabase/functions/pulser-slack-handler/`)
- **Intent queue**: `ops.taskbus_intents`
- **Response**: Ephemeral ACK within 3 seconds, async result via `response_url`
- **Contract**: `docs/contracts/C-PULSER-ODOO-01.md`

---

## Non-Overlap Rules

1. **Pulser MUST NOT handle `/plane`** — all `/plane` traffic routes to Plane's endpoints.
2. **Plane MUST NOT handle `/pulser`** — all `/pulser` traffic routes to Pulser's handler.
3. **No shared Slack app token** — each app has its own bot token and signing secret.
4. **No shared OAuth flow** — Plane manages its own OAuth; Pulser uses bot token only.

---

## Required Secrets

### Plane Slack App

| Secret | Store | Purpose |
|--------|-------|---------|
| `PLANE_SLACK_CLIENT_ID` | Plane self-hosted env | Slack OAuth client ID |
| `PLANE_SLACK_CLIENT_SECRET` | Plane self-hosted env | Slack OAuth client secret |

### Pulser Slack App

| Secret | Store | Purpose |
|--------|-------|---------|
| `SLACK_SIGNING_SECRET` | Supabase Vault / Vercel env | HMAC signature verification |
| `SLACK_BOT_TOKEN` | Supabase Vault / Vercel env | Bot API calls (chat.postMessage) |

---

## Integration Layer

The two apps connect at the **data plane**, not the Slack layer:

```
Plane Slack → /plane create → Plane creates issue
                                    ↓
                              Plane webhooks
                                    ↓
                         ops.work_items (upsert)
                                    ↑
                         Pulser reads work items
                                    ↑
Pulser Slack → /pulser plane status → query ops.work_items
```

### Why not merge?

1. **Incompatible endpoint surfaces**: Plane expects `/silo/api/slack/*`; Pulser
   uses Socket Mode. Mounting one inside the other creates brittle coupling.

2. **Different OAuth models**: Plane needs Team+User OAuth for workspace installs.
   Pulser is a runner — it should not manage user OAuth tokens.

3. **Scope creep**: Combined app needs `links:read`, `links:write`,
   `message.channels`, plus all Pulser scopes. Classic "God token" problem.

4. **Separate failure domains**: If Plane's Slack integration is down, `/pulser
   status` and `/pulser gates` must still work. Fusing them couples incident
   response to the system under incident.

5. **Independent upgrade paths**: Plane is an external product that gets upgraded.
   Pulser is internal platform. Shared app means every Plane upgrade risks
   breaking ops workflows.

---

## Future: Unified Slack Experience

To make it *feel* like one experience without merging apps:

- `/pulser plane status` queries Plane API / `ops.work_items`
- Cross-linking: Pulser replies include Plane issue URLs and vice versa
- Unified unfurl handling via shared domain allowlist (separate apps)
- `/pulser` can invoke Plane REST API for read operations

---

## Verification Checklist

- [ ] Plane Slack endpoints listed with `plane.insightpulseai.com` domain
- [ ] Plane Slack secrets registered in `ssot/secrets/registry.yaml` (values in Vault/env)
- [ ] Contract explicitly separates `/plane` vs `/pulser`
- [ ] `ssot/integrations/slack/apps.yaml` declares both apps
- [ ] Ops Console plan references the two-app model
