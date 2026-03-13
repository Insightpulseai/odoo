# ipai_agent — Odoo-Native IPAI Agent Runtime

**Date:** 2026-02-27
**Status:** Active — `addons/ipai/ipai_agent`
**Branch:** `feat/ipai-module-audit-odoo19`

---

## Decision

`addons/ipai/ipai_agent` is the **single, canonical surface** for triggering and auditing
IPAI agent runs from within Odoo. No other addon should re-implement the agent lifecycle
or the HMAC webhook endpoint.

---

## Architecture

```
Odoo UI
 └─ ipai.agent.run (queued)
      │
      ├── cron (every 2min): ipai.agent.run.cron_dispatch_queued()
      │       │
      │       ├── policy gate:  waiting_approval? → wait
      │       └── dispatch:     POST <edge_fn_endpoint> (HMAC/JWT/service_role)
      │
      └── Supabase Edge Function
               │
               └── POST /ipai/agent/callback   (HMAC-verified)
                        │
                        └── ipai.agent.run  state → succeeded/failed
```

---

## Models

| Model | Purpose |
|---|---|
| `ipai.agent.run` | Single execution record (state machine + I/O payloads) |
| `ipai.agent.tool` | Registry of permitted tools + auth mode |
| `ipai.agent.policy` | Governance defaults per (target_model, company_id) |

### State machine

```
queued → running → succeeded
queued → waiting_approval → (approve) → queued → running → succeeded
                           → (reject)  → cancelled
queued / waiting_approval  → cancelled
failed / cancelled          → queued  (retry)
```

### Idempotency

Default key: `<target_model>/<target_res_id>/<tool_technical_name>`

`find_or_create()` reuses active runs within a 300-second window.
Completed (succeeded/failed/cancelled) runs are never reused.

---

## Security

### Auth modes (configured per tool, in `ipai.agent.tool.auth_mode`)

| Mode | How it works |
|---|---|
| `none` | No auth (internal/dev only) |
| `api_key` | Secret read from `ir.config_parameter` at dispatch |
| `jwt` | User's Supabase JWT forwarded in `Authorization: Bearer` |
| `service_role` | `SUPABASE_SERVICE_ROLE_KEY` from `ir.config_parameter` |
| `hmac` | HMAC-SHA256(body + timestamp, secret) — callbacks use this |

### Webhook (POST `/ipai/agent/callback`)

- `x-signature`: HMAC-SHA256(body + timestamp_bytes, HMAC_SECRET)
- `x-timestamp`: Unix epoch string (seconds)
- Window: ±300 seconds (replay protection)
- Secret: `ir.config_parameter` key `ipai.agent.hmac_secret`

### Supabase Edge Function side (`supabase/functions/_shared/auth_guard.ts`)

- `requireAuth(req)` — verifies JWT or service_role key
- `requireHmac(req)` — verifies x-signature + x-timestamp
- All secrets via `Deno.env` (Supabase Vault), never in code

---

## Access Groups

| Group | XML ID | Can |
|---|---|---|
| Agent User | `group_ipai_agent_user` | Trigger runs, view own runs |
| Agent Approver | `group_ipai_agent_approver` | Approve/reject, cancel |
| Agent Admin | `group_ipai_agent_admin` | Full CRUD, tool/policy config |

---

## ir.config_parameter keys

| Key | Purpose |
|---|---|
| `ipai.agent.hmac_secret` | HMAC secret for webhook callback verification |
| `ipai.agent.tool.<technical_name>.endpoint` | Tool endpoint URL (set per tool via `endpoint_param`) |
| `ipai.agent.tool.<technical_name>.secret` | Tool API key / secret (set per tool via `secret_param`) |

**Never hardcode values** — all lookups go through `tool.get_endpoint()` / `tool.get_secret()`.

---

## Integration with ipai_hr_expense_liquidation

A "Run IPAI Agent" button is available on `hr.expense.liquidation` form view
(submitted + approved states, requires `group_ipai_agent_user`).

The button calls `action_trigger_agent_run()` which:
1. Looks up the active tool with `technical_name = "liquidation_process"`
2. Calls `ipai.agent.run.find_or_create()` with liquidation context
3. Opens the resulting run record in a modal

---

## Extension rules (for future addons)

```
✅ Do:   Add new ipai.agent.tool records pointing to new Edge Functions
✅ Do:   Add new ipai.agent.policy records for new target models
✅ Do:   _inherit = "ipai.agent.run" to add custom fields
❌ Don't: Create a second webhook controller at a different path
❌ Don't: Re-implement the state machine or idempotency logic
❌ Don't: Hardcode endpoint URLs or secrets in Python / TypeScript code
```

---

## Related commits

| Commit | Description |
|---|---|
| *(this session)* | Add `ipai_agent` addon: models, controller, views, cron, tests |
| *(this session)* | Add `supabase/functions/_shared/auth_guard.ts` |
| *(this session)* | Add "Run IPAI Agent" button on hr.expense.liquidation |
