# Supabase ↔ n8n Integration (Ops Automations)

## Purpose

Use n8n workflows as the approval and automation plane for Odoo + Supabase ops
events. Supabase pushes events outward via **Database Webhooks**; n8n receives
them on a **Webhook Trigger node** and drives the downstream actions (Slack
approvals, GitHub workflow dispatches, Odoo API calls, etc.).

## Supported patterns

### Pattern A — push (DB Webhook → n8n)

Best for: real-time events (approval requests, deploy triggers, anomaly alerts)

```
Supabase: INSERT/UPDATE/DELETE on ops.*
  └─ Database Webhook (post-commit) fires HTTP POST
       └─ n8n Webhook Trigger (prod URL)
            └─ Slack approval → await
                 └─ n8n Supabase node: UPDATE approval row
                      └─ GitHub Workflow Dispatch (optional)
```

Supabase Database Webhooks fire **after commit** on `INSERT`, `UPDATE`, or
`DELETE` and deliver a JSON payload to an external HTTP endpoint.

### Pattern B — pull (n8n schedule → Supabase)

Best for: periodic polling, reporting, reconciliation

```
n8n Schedule Trigger (cron)
  └─ n8n Supabase node: SELECT / query
       └─ transform + notify / write back
```

The n8n Supabase node supports `create`, `get`, `getAll`, `delete` row
operations and can act as an AI tool in agentic workflows.

### Pattern C — Ops Console initiated

Best for: manual deploys, environment promotions from the UI

```
Ops Console Action (Next.js API route)
  └─ GitHub Workflow Dispatch API
       └─ (optional) n8n webhook as a side-channel notification
```

## Security model

- Use `SUPABASE_SERVICE_ROLE_KEY` **only server-side** — stored in n8n's
  credential vault (not in browser code, not in `.env.local` for client routes).
- Never store the service role key in any `NEXT_PUBLIC_*` variable.
- Prefer a **dedicated least-privilege Postgres role** + RLS for webhook sources
  where possible; reserve service role for n8n only.
- n8n credentials: store Supabase API key in n8n's built-in credential store,
  not as a plain environment variable.

## Canonical event contract

All triggers (Supabase DB Webhooks, Ops Console, GitHub Actions, manual n8n
runs) should emit / accept the same JSON shape:

```json
{
  "event_type": "deploy.requested",
  "env": "prod",
  "actor": "jgtolentino",
  "correlation_id": "uuid-v4",
  "payload": {}
}
```

Full schema: `docs/ops/contracts/n8n_event.schema.json`

## n8n Webhook node — test vs prod URLs

- **Test URL**: used when executing workflows manually in the n8n editor. Does
  **not** persist between editor sessions. Use for development only.
- **Prod URL**: stable URL active only when the workflow is **activated**
  (toggled on). Use this URL in Supabase Database Webhook targets.

Always configure Supabase webhooks with the **prod URL**; update them whenever
you recreate the workflow.

## Practical blueprints

### Approval workflow (replaces manual gate)

1. Odoo or Ops Console writes a row to `ops.approval_requests`.
2. Supabase Database Webhook on `INSERT` → n8n webhook trigger.
3. n8n posts Slack message with approve/reject buttons; workflow pauses.
4. On approval:
   - n8n Supabase node: UPDATE `ops.approval_requests` → `approved`.
   - n8n triggers GitHub Workflow Dispatch for the deploy.
5. On rejection:
   - n8n Supabase node: UPDATE → `rejected`.
   - Slack notification to requestor.

### Ops notifications

Any `INSERT` into `ops.run_events`:
- n8n fans out to: Slack `#ops-alerts`, GitHub Issue (if severity ≥ high),
  evidence log write-back.

## Cross-references

- `docs/ops/SUPABASE_VERCEL.md` — env var wiring
- `docs/ops/VERCEL_MONOREPO.md` — monorepo build config
- `docs/ops/contracts/n8n_event.schema.json` — canonical event payload schema
- `apps/ops-console/app/api/` — server routes that dispatch to n8n / GitHub
- Live n8n: `https://n8n.insightpulseai.com` (admin: `devops@insightpulseai.com`)
