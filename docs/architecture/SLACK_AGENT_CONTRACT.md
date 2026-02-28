# SLACK_AGENT_CONTRACT.md
# Cross-boundary contract: Slack ↔ SSOT taskbus (ops.runs)
#
# Governs: apps/slack-agent/ ↔ supabase/functions/ ↔ Odoo (SoR) ↔ work.* (SoW)
# Created: 2026-03-01
# Branch:  feat/taskbus-agent-orchestration
# SSOT:    ssot/integrations/slack_agent.yaml

## 1. Boundary Diagram

```
Slack Platform
  │
  │  POST /api/slack/events        (Slack Events API)
  │  POST /api/slack/interactive   (Slack Interactivity)
  │  POST /api/slack/commands      (Slack Slash Commands)
  │
  ▼
apps/slack-agent  (Nitro, Vercel runtime)
  │
  │  1. Verify X-Slack-Signature (HMAC-SHA256, 5-min replay window)
  │  2. ACK HTTP 200 immediately (Slack timeout = 3s)
  │  3. Enqueue ops.run (fire-and-forget, idempotency key = slack:*:{id})
  │
  ▼
Supabase ops.runs  (SSOT — single append-only queue)
  │
  │  pg_cron / realtime → worker picks up run
  │
  ▼
Worker / Agent  (SoW boundary — all business logic here)
  │
  ├─→  Odoo / PostgreSQL  (SoR — writes only via approved run)
  ├─→  work.*             (SoW — task state only via approved run)
  └─→  Slack response_url / chat.postMessage  (async result delivery)
```

## 2. Request Verification

All three endpoints share the same verification contract.

**Algorithm**: HMAC-SHA256
**Key**: `SLACK_SIGNING_SECRET` (env var, never hardcoded)
**Message**: `v0:<x-slack-request-timestamp>:<raw_body_bytes>`
**Expected header**: `X-Slack-Signature: v0=<hex_digest>`

**Rejection conditions** (returns HTTP 401):
- Missing `X-Slack-Request-Timestamp` header
- Missing `X-Slack-Signature` header
- Timestamp older than 300 seconds (anti-replay)
- HMAC digest mismatch

**Implementation**: `apps/slack-agent/server/lib/verify.ts`
**Tests**: `apps/slack-agent/__tests__/verify.test.ts` (7 tests)

## 3. ACK-First Protocol

Slack will retry delivery if it does not receive HTTP 2xx within **3 seconds**.

```
Request received
  │
  ├─ Verify signature (sync, <1ms)
  ├─ Parse body (sync)
  ├─ Send HTTP 200 ACK  ←── Slack receives this; clock stops
  │
  └─ enqueueSlackRun()  ←── async, fire-and-forget; Slack does not wait
       │
       └─ .catch(console.error)  ←── errors logged, never re-thrown to Slack
```

This means **enqueue failures are non-fatal to Slack** but ARE logged. A separate
alerting mechanism should monitor `ops.run_events` for `status=error` rows.

## 4. Idempotency Contract

Slack retries on non-2xx or slow responses. The same Slack event can arrive multiple
times. Idempotency prevents duplicate taskbus runs.

| Source | Key format | Seed field |
|--------|------------|------------|
| Events API | `slack:event:{event_id}` | `body.event_id` (fallback: `event_ts`) |
| Interactivity | `slack:interaction:{trigger_id}` | `payload.trigger_id` |
| Slash Commands | `slack:command:{command}:{trigger_id}` | `trigger_id` + `command` |

The `ops.runs.idempotency_key` column has a `UNIQUE` constraint. Duplicate
`enqueue()` calls are silently rejected by the taskbus (INSERT ... ON CONFLICT DO NOTHING).

**Implementation**: `apps/slack-agent/server/lib/idempotency.ts`
**Tests**: `apps/slack-agent/__tests__/idempotency.test.ts`

## 5. SSOT Boundary Rules

| Rule | Rationale |
|------|-----------|
| Slack handlers NEVER write to Odoo directly | Preserves SoR write isolation |
| Slack handlers NEVER write to `work.*` tables | SoW boundary — only workers write |
| All state flows through `ops.runs` | Single audit trail, dedup, replay |
| `response_url` forwarded in run input | Worker posts async result, not handler |
| Signing secret ONLY in runtime env | Never in source, never in git |

## 6. Secrets

| Secret name | Purpose | Store |
|-------------|---------|-------|
| `slack_signing_secret` | Endpoint signature verification | Supabase Vault + Vercel env |
| `slack_bot_token` | `chat.postMessage` / `response_url` post | Supabase Vault + Vercel env |

See: `ssot/secrets/registry.yaml` entries `slack_signing_secret`, `slack_bot_token`

**Nitro config mapping** (`apps/slack-agent/nitro.config.ts`):

```
SLACK_SIGNING_SECRET  →  runtimeConfig.slackSigningSecret
SLACK_BOT_TOKEN       →  runtimeConfig.slackBotToken
SUPABASE_URL          →  runtimeConfig.supabaseUrl
SUPABASE_SERVICE_ROLE_KEY  →  runtimeConfig.supabaseServiceRoleKey
```

## 7. Registered Routes and Job Types

### Events API (`/api/slack/events`)

| Slack event type | Job type | Agent |
|-----------------|----------|-------|
| `app_mention` | `slack.event.app_mention` | `slack-copilot-agent` |
| `message` | `slack.event.message` | `slack-copilot-agent` |

Add new event types in `apps/slack-agent/server/lib/taskbus.ts` →
`resolveSlackAction()`. Unregistered event types are acknowledged but not enqueued.

### Slash Commands (`/api/slack/commands`)

| Command | Job type | Agent |
|---------|----------|-------|
| `/run` | `slack.command.run` | `slack-copilot-agent` |
| `/ask` | `slack.command.ask` | `slack-copilot-agent` |

Add new commands in `resolveSlackCommand()`. Unknown commands receive an ephemeral
"Unknown command" message and are not enqueued.

### Interactivity (`/api/slack/interactive`)

All interaction types are enqueued as `slack.interactive.{type}` with agent
`slack-copilot-agent`. The `callback_id` (from view or first action) is included
in the run input for worker-side routing.

## 8. URL Verification (Slack App Setup)

When configuring the Slack App's Event Subscriptions, Slack sends a one-time
`url_verification` challenge. The events endpoint handles this transparently:

```
POST /api/slack/events
Body: { "type": "url_verification", "challenge": "abc123" }
Response: { "challenge": "abc123" }
```

No signature is present on challenge requests; they bypass verification.

## 9. Install State SSOT

Slack App configuration is declared in `ssot/integrations/slack_agent.install.yaml`
(the authoritative mapping — not tribal knowledge, not this doc).

That file specifies:
- Required endpoint paths (`/api/slack/events`, `/api/slack/interactive`, `/api/slack/commands`)
- Required bot OAuth scopes (`chat:write`, `commands`)
- ACK contract: ack_within_ms=2500, pattern=ACK then enqueue
- Idempotency key formats and dedup behaviour
- Secrets consumers (server-only, no browser/CI access)
- Enterprise Grid readiness notes (planned: org/workspace routing tables)

**During initial setup**, follow the install YAML, not this document, for URL and scope values.

**For Enterprise Grid**: The install YAML contains a `enterprise_grid_readiness` block.
Before enabling org-wide install, add the three ops tables listed there and a separate
admin token entry to the secrets registry.

## 10. Local Development

```bash
# Start Nitro dev server (port 3300)
cd apps/slack-agent && pnpm dev

# Expose via ngrok or similar, then set Request URLs in Slack App settings
# following ssot/integrations/slack_agent.install.yaml endpoints.

# Required env vars (server-side only — never expose to browser)
SLACK_SIGNING_SECRET=<Slack App → Basic Information → Signing Secret>
SLACK_BOT_TOKEN=<Slack App → OAuth & Permissions → Bot Token>
SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<Supabase project → API settings>
```

## 11. Tests

```bash
# From apps/slack-agent/
pnpm test

# Covers:
#   verify.test.ts     — 7 tests: valid sig, tampered body, wrong secret,
#                        missing headers, replay attack, Uint8Array body
#   idempotency.test.ts — determinism, different IDs → different keys,
#                         slash normalization in commands
```

## 12. Deployment

The app deploys via Vercel (preset: `vercel` in `NITRO_PRESET`).

Env vars must be set in Vercel Dashboard (not committed to git) and in Supabase Vault.
See `ssot/secrets/registry.yaml` entries `slack_signing_secret`, `slack_bot_token` for
approved stores and explicit consumer list.

## 13. Contract Enforcement

**SSOT files** (these are the authoritative sources — update them, not this doc):
- `ssot/integrations/slack_agent.yaml` — components, boundary rules, risk flags
- `ssot/integrations/slack_agent.install.yaml` — endpoints, scopes, ACK/idempotency contract
- `ssot/integrations/_index.yaml` — integration registration

**CI gate**: `.github/workflows/slack-agent-ssot-gate.yml` runs
`scripts/ci/check_slack_agent_contract.py` on every change to `apps/slack-agent/**`
or `ssot/integrations/slack_agent*.yaml`. CI fails if:
- Any route removes signature verification
- ACK is sent after enqueue (ACK-fast violation)
- Idempotency key builder is missing from a route
- Install YAML is missing required fields

Cross-boundary rules are enforced by `docs/architecture/SSOT_BOUNDARIES.md`.
