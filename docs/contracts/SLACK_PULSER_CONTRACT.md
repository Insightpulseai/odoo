# Slack Pulser Contract (C-20)

> **Scope**: Defines the integration boundary between the Slack `pulser` app
> and IPAI Supabase Edge Functions for ops notifications and interactive actions.
>
> SSOT: `ssot/integrations/slack/pulser.yaml`
> Last updated: 2026-03-01

---

## 1. Parties

| Role | Component | Location |
|------|-----------|----------|
| **Source** | Slack API (Events, Interactions, Commands) | External (`wss://wss-primary.slack.com`, `api.slack.com`) |
| **Consumer** | `ops-slack-bridge` (Supabase Edge Function) | `supabase/functions/ops-slack-bridge/` |
| **Consumer** | `ops-slack-socket` (Supabase Edge Function) | `supabase/functions/ops-slack-socket/` |
| **SSOT metadata** | Slack App SSOT | `ssot/integrations/slack/pulser.yaml` |
| **Secret registry** | Supabase Vault | `ssot/secrets/registry.yaml` (names only) |
| **Idempotency ledger** | Postgres | `ops.slack_envelopes` |

---

## 2. Transport

### 2.1 Socket Mode (Primary)

Socket Mode is the primary transport. The Edge Function `ops-slack-socket` maintains
a WebSocket connection to Slack and receives events, interactions, and slash commands
without exposing a public HTTP endpoint.

```
Connection:
  wss://wss-primary.slack.com/link
  Headers:
    Authorization: Bearer xapp-... (app-level token)

Envelope format (inbound):
  {
    "envelope_id": "<uuid>",
    "type": "events_api" | "interactive" | "slash_commands",
    "payload": { ... },
    "accepts_response_payload": true | false,
    "retry_attempt": 0,
    "retry_reason": ""
  }

Acknowledgement (must send within 3 seconds):
  { "envelope_id": "<uuid>" }

Acknowledgement with response payload:
  { "envelope_id": "<uuid>", "payload": { ... } }
```

### 2.2 HTTP Endpoints (Optional / Fallback)

If Socket Mode is unavailable, the `ops-slack-bridge` Edge Function can receive
events via HTTP POST. HTTP mode requires signing secret verification.

```
POST <SUPABASE_EDGE_URL>/ops-slack-bridge?action=event
Headers:
  X-Slack-Signature: v0=<hmac_sha256>
  X-Slack-Request-Timestamp: <epoch_seconds>
  Content-Type: application/json
Body:
  { type: "event_callback", event: {...}, team_id, event_id, ... }
Response (200 OK):
  (empty body or challenge response)
```

---

## 3. Auth & Verification

### 3.1 Socket Mode Authentication

- App-level token (`xapp-*`) authenticates the WebSocket connection
- Bot token (`xoxb-*`) authenticates outbound API calls
- Both tokens stored in Supabase Vault

### 3.2 HTTP Signing Secret Verification (for HTTP mode)

```typescript
const timestamp = req.headers.get("X-Slack-Request-Timestamp");
const signature = req.headers.get("X-Slack-Signature");
const body = await req.text();

// Reject if timestamp older than 5 minutes (replay protection)
if (Math.abs(Date.now() / 1000 - Number(timestamp)) > 300) {
  return jsonErr("UNAUTHORIZED", "Stale timestamp", 401);
}

const basestring = `v0:${timestamp}:${body}`;
const expected = "v0=" + hmac("sha256", SLACK_SIGNING_SECRET, basestring);
if (!timingSafeEqual(signature, expected)) {
  return jsonErr("UNAUTHORIZED", "Invalid signature", 401);
}
```

### 3.3 URL Verification Challenge

The HTTP endpoint must handle Slack's URL verification challenge:

```typescript
if (body.type === "url_verification") {
  return new Response(JSON.stringify({ challenge: body.challenge }), {
    headers: { "Content-Type": "application/json" },
  });
}
```

---

## 4. Idempotency

### 4.1 Envelope Deduplication

Slack may retry event delivery. All envelopes MUST be deduplicated before processing.

**Deduplication key**: `(team_id, envelope_id)`

**Ledger table**: `ops.slack_envelopes` (see migration `20260301000002_slack_envelopes.sql`)

```typescript
// Before processing:
const { data, error } = await supabase
  .from("slack_envelopes")
  .insert({
    envelope_id,
    team_id,
    event_type,
    payload,
    status: "processing",
  })
  .select()
  .single();

if (error?.code === "23505") {
  // Unique constraint violation — already processed
  return ack(envelope_id);
}

// After processing:
await supabase
  .from("slack_envelopes")
  .update({ status: "completed", processed_at: new Date().toISOString() })
  .match({ team_id, envelope_id });
```

### 4.2 Envelope Lifecycle

| Status | Meaning |
|--------|---------|
| `pending` | Received, not yet processing |
| `processing` | Handler executing |
| `completed` | Successfully processed |
| `failed` | Processing failed (see `last_error`) |

---

## 5. Invariants

1. **Acknowledge within 3 seconds.** Socket Mode envelopes must be acknowledged within 3 seconds. Perform the ack first, then process asynchronously if the handler is slow.

2. **Persist envelope_id before side effects.** Insert into `ops.slack_envelopes` before executing any side-effecting operation (posting messages, updating records, etc.).

3. **Deduplicate on (team_id, envelope_id).** Never process the same envelope twice. Use the unique constraint on `ops.slack_envelopes` for atomic deduplication.

4. **Vault-only secrets.** Bot token, app-level token, signing secret, client secret, and refresh token are stored exclusively in Supabase Vault. Never hardcode, never log.

5. **Signing secret verification for HTTP mode.** All HTTP requests must be verified using the signing secret. Reject requests with timestamps older than 5 minutes.

6. **Audit trail.** All processed events are audited to `ops.platform_events` with `actor: ops-slack-bridge` or `actor: ops-slack-socket`.

7. **No Verification Token.** The legacy Verification Token is deprecated by Slack. Use signing secret verification only.

---

## 6. Environment Variables (Supabase Vault)

| Secret name | Purpose | Vault key |
|-------------|---------|-----------|
| Bot token (`xoxb-*`) | Outbound API calls | `slack_bot_token` |
| App-level token (`xapp-*`) | Socket Mode connection | `slack_app_token` |
| Signing secret | HTTP request verification | `slack_signing_secret` |
| Client secret | OAuth flow | `slack_client_secret` |
| Refresh token | Token rotation (if enabled) | `slack_refresh_token` |

All names registered in `ssot/secrets/registry.yaml`.

---

## 7. Event Processing Flow

```
Slack Platform
  |
  |-- Socket Mode (primary)
  |     |
  |     v
  |   ops-slack-socket (Edge Function)
  |     |-- Maintain WSS connection with xapp-* token
  |     |-- Receive envelope
  |     |-- ACK within 3 seconds
  |     |-- Insert into ops.slack_envelopes (dedupe)
  |     |-- Route by envelope type:
  |     |     events_api   -> event handler
  |     |     interactive  -> interaction handler
  |     |     slash_commands -> command handler
  |     |-- Audit to ops.platform_events
  |
  |-- HTTP (fallback)
        |
        v
      ops-slack-bridge (Edge Function)
        |-- Verify X-Slack-Signature
        |-- Handle url_verification challenge
        |-- Insert into ops.slack_envelopes (dedupe)
        |-- Route by event type
        |-- Audit to ops.platform_events
```

---

## 8. Error Handling

| Scenario | Response | Action |
|----------|----------|--------|
| Invalid signing secret (HTTP) | 401 UNAUTHORIZED | Log attempt, reject |
| Stale timestamp (> 5 min) | 401 UNAUTHORIZED | Replay attack, reject |
| Duplicate envelope | 200 OK (idempotent) | Return cached ack |
| WSS connection dropped | Reconnect | Exponential backoff, max 5 retries |
| Handler failure | Update `ops.slack_envelopes.status = 'failed'` | Log `last_error`, alert ops |
| Slack API rate limit | Respect `Retry-After` | Queue and retry |

---

## 9. Scopes

### Bot Token Scopes (xoxb-*)

| Scope | Purpose |
|-------|---------|
| `chat:write` | Post messages to channels |
| `channels:read` | List public channels |
| `commands` | Slash commands |
| `app_mentions:read` | Respond to @pulser mentions |

### App-Level Token Scopes

| Scope | Purpose |
|-------|---------|
| `connections:write` | Establish Socket Mode connection |
| `authorizations:read` | Read authorization info |
| `app_configurations:write` | Manage app configuration |

---

## 10. CI Enforcement

- `ssot-surface-guard.yml` validates Edge Function README.md presence
- `platform-guardrails.yml` scans for hardcoded secrets
- Migration `20260301000002_slack_envelopes.sql` creates the idempotency ledger

---

## 11. Related Docs

- `ssot/integrations/slack/pulser.yaml` -- App metadata SSOT
- `ssot/secrets/registry.yaml` -- Secret name registry
- `supabase/migrations/20260301000002_slack_envelopes.sql` -- Envelope ledger migration
- `docs/contracts/SUPABASE_EDGE_FUNCTIONS_CONTRACT.md` -- Edge Function standards
- `docs/contracts/SUPABASE_VAULT_CONTRACT.md` -- Vault access patterns
- `docs/contracts/PLATFORM_CONTRACTS_INDEX.md` -- Contract index (C-20)
- `spec/slack-pulser-integration/` -- Spec bundle for implementation
