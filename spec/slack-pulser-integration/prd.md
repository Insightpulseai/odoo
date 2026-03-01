# PRD: Slack Pulser Integration

> Product requirements for the Slack `pulser` app — IPAI ops notifications and interactive actions.
> Contract: C-20 (`docs/contracts/SLACK_PULSER_CONTRACT.md`)

---

## Problem Statement

IPAI platform operations (deployments, CI results, monitoring alerts, task completions) require a real-time notification channel with interactive capabilities. Slack is the team's primary communication tool and the approved replacement for the deprecated Mattermost integration.

---

## Goals

1. **Real-time ops notifications** -- Deliver platform events (CI pass/fail, deployment status, error alerts) to designated Slack channels within seconds.
2. **Interactive actions** -- Allow team members to acknowledge alerts, trigger rollbacks, or approve deployments directly from Slack message buttons.
3. **Slash commands** -- Provide `/pulser status`, `/pulser deploy`, and `/pulser health` commands for quick ops queries.
4. **Idempotent event processing** -- Guarantee exactly-once processing of Slack events using the envelope ledger.

---

## Non-Goals

- Slack app distribution to external workspaces (single-workspace only)
- File upload/download through Slack
- Slack Connect (cross-organization channels)
- Custom Slack workflows (Workflow Builder)
- Direct Odoo record manipulation from Slack (out of scope for v1)

---

## Requirements

### R1: Socket Mode Transport

- The app connects to Slack via Socket Mode (WebSocket)
- No public HTTP endpoint required for event delivery
- App-level token (`xapp-*`) used for WebSocket authentication
- Automatic reconnection with exponential backoff on connection drops

### R2: Ops Notifications

- **Channel routing**: Events are posted to channels based on event type (e.g., `#ops-alerts` for errors, `#ops-deploy` for deployments)
- **Message format**: Rich Block Kit messages with structured metadata (timestamp, service, severity)
- **Notification types** (v1):
  - CI pipeline pass/fail
  - Deployment started/completed/failed
  - Error rate threshold exceeded
  - Scheduled task completion
  - Manual trigger acknowledgements

### R3: Interactive Actions

- Message buttons for: Acknowledge, Investigate, Rollback, Approve
- Action payloads routed through Socket Mode envelope handling
- Actions audited to `ops.platform_events`
- Response messages update the original notification (replace, not new message)

### R4: Slash Commands

| Command | Description | Response |
|---------|-------------|----------|
| `/pulser status` | Show current platform health | Ephemeral message with service statuses |
| `/pulser deploy <service>` | Trigger deployment | Confirmation modal, then channel notification |
| `/pulser health` | Edge Function health checks | Ephemeral message with function statuses |

### R5: Idempotency

- All envelopes persisted to `ops.slack_envelopes` before processing
- Deduplication on `(team_id, envelope_id)` unique constraint
- Failed envelopes marked with `status = 'failed'` and `last_error` for debugging
- Retry logic respects the idempotency ledger

### R6: Security

- Signing secret verification for any HTTP fallback endpoints
- All secrets in Supabase Vault (see `ssot/secrets/registry.yaml`)
- No secret values in Edge Function source code or logs
- Bot token scopes limited to minimum required

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Event delivery latency (platform event to Slack message) | < 5 seconds |
| Envelope deduplication rate | 100% (no duplicate processing) |
| Socket Mode uptime | > 99.5% (reconnection within 30s) |
| Slash command response time | < 3 seconds |

---

## Architecture

```
Platform Events (CI, Deploy, Monitoring)
  |
  v
ops.platform_events (Supabase)
  |
  v
pg_cron / pg_net trigger
  |
  v
ops-slack-socket (Edge Function)
  |-- Socket Mode WSS connection
  |-- Outbound: Post to Slack channels via xoxb-* token
  |-- Inbound: Receive interactions and commands
  |-- Deduplicate via ops.slack_envelopes
  |
  v
Slack Workspace (#ops-alerts, #ops-deploy, etc.)
```

---

## Dependencies

- Supabase Edge Functions (runtime)
- Supabase Vault (secrets)
- `ops.slack_envelopes` migration (`20260301000002`)
- `ops.platform_events` table (existing)
- Slack App `pulser` (App ID: `A0ABQ9BGYA3`)
