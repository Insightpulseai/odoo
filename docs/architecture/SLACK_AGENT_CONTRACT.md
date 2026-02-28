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

## 9. Local Development

```bash
# Start Nitro dev server (port 3300)
cd apps/slack-agent && pnpm dev

# Expose via ngrok or similar
ngrok http 3300

# Set Slack App → Event Subscriptions URL:
# https://<ngrok-id>.ngrok.io/api/slack/events

# Required env vars
SLACK_SIGNING_SECRET=<from Slack App > Basic Information > App Credentials>
SLACK_BOT_TOKEN=<from Slack App > OAuth & Permissions>
SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<from Supabase project settings>
```

## 10. Tests

```bash
# From apps/slack-agent/
pnpm test

# Covers:
#   verify.test.ts     — 7 tests: valid sig, tampered body, wrong secret,
#                        missing headers, replay attack, Uint8Array body
#   idempotency.test.ts — determinism, different IDs → different keys,
#                         slash normalization in commands
```

## 11. Deployment

The app deploys via Vercel (preset: `vercel` in `NITRO_PRESET`).

**Vercel env vars required** (all consumed via `useRuntimeConfig`):
- `SLACK_SIGNING_SECRET`
- `SLACK_BOT_TOKEN`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

**Slack App configuration**:
- Event Subscriptions → Request URL: `https://<vercel-url>/api/slack/events`
- Interactivity → Request URL: `https://<vercel-url>/api/slack/interactive`
- Slash Commands → Request URL: `https://<vercel-url>/api/slack/commands`

## 12. Contract Enforcement

This contract is validated by `ssot/integrations/slack_agent.yaml`.
Cross-boundary rules are enforced by `docs/architecture/SSOT_BOUNDARIES.md`.

Any change to the ACK pattern, idempotency key format, or boundary rules requires
updating both this document and the SSOT registration.
