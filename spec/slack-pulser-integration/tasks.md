# Tasks: Slack Pulser Integration

> Task breakdown for the Slack `pulser` app integration.
> Plan: `spec/slack-pulser-integration/plan.md`

---

## Phase 1: Foundation (SSOT + Migration + Contracts)

- [x] T1.1: Create `ssot/integrations/slack/pulser.yaml`
- [x] T1.2: Register Slack secrets in `ssot/secrets/registry.yaml`
- [x] T1.3: Create `supabase/migrations/20260301000002_slack_envelopes.sql`
- [x] T1.4: Write platform contract C-20 (`docs/contracts/SLACK_PULSER_CONTRACT.md`)
- [x] T1.5: Add C-20 to `docs/contracts/PLATFORM_CONTRACTS_INDEX.md`
- [x] T1.6: Create spec bundle (`spec/slack-pulser-integration/`)

---

## Phase 2: Edge Functions

- [ ] T2.1: Create `supabase/functions/ops-slack-bridge/index.ts` (HTTP fallback)
  - [ ] T2.1a: Implement signing secret verification
  - [ ] T2.1b: Implement URL verification challenge handler
  - [ ] T2.1c: Implement event routing dispatcher
  - [ ] T2.1d: Implement envelope deduplication via `ops.slack_envelopes`
  - [ ] T2.1e: Add `README.md` per Edge Function contract

- [ ] T2.2: Create `supabase/functions/ops-slack-socket/index.ts` (Socket Mode)
  - [ ] T2.2a: Implement WebSocket connection to Slack
  - [ ] T2.2b: Implement envelope acknowledgement (< 3s)
  - [ ] T2.2c: Implement event/interaction/command routing
  - [ ] T2.2d: Implement reconnection with exponential backoff
  - [ ] T2.2e: Add `README.md` per Edge Function contract

- [ ] T2.3: Create shared utilities `supabase/functions/_shared/slack/`
  - [ ] T2.3a: `verify.ts` -- signing secret verification
  - [ ] T2.3b: `api.ts` -- Slack Web API client wrapper
  - [ ] T2.3c: `blocks.ts` -- Block Kit message builder helpers
  - [ ] T2.3d: `envelope.ts` -- envelope dedup logic (insert-or-skip)

- [ ] T2.4: Deploy Edge Functions and verify health checks

---

## Phase 3: Notification Routing

- [ ] T3.1: Define channel routing configuration (event type -> channel ID mapping)
- [ ] T3.2: Implement Block Kit templates:
  - [ ] T3.2a: CI result template (pass/fail)
  - [ ] T3.2b: Deployment status template (started/completed/failed)
  - [ ] T3.2c: Error alert template (with acknowledge button)
  - [ ] T3.2d: Task completion template
- [ ] T3.3: Create pg_cron + pg_net trigger for `ops.platform_events` -> Slack
- [ ] T3.4: Test end-to-end: insert event -> Slack message appears

---

## Phase 4: Interactive Actions & Slash Commands

- [ ] T4.1: Implement action handler for interactive buttons
  - [ ] T4.1a: Acknowledge action
  - [ ] T4.1b: Investigate action (link to relevant dashboard/logs)
  - [ ] T4.1c: Rollback action (trigger deployment rollback)
- [ ] T4.2: Implement slash command handlers
  - [ ] T4.2a: `/pulser status` -- platform health summary
  - [ ] T4.2b: `/pulser deploy <service>` -- deployment trigger with confirmation
  - [ ] T4.2c: `/pulser health` -- Edge Function health check summary
- [ ] T4.3: Implement modal views for confirmation flows
- [ ] T4.4: Wire action results to update original messages

---

## Phase 5: Observability & Hardening

- [ ] T5.1: Add processing latency tracking to envelope handler
- [ ] T5.2: Create pg_cron job to archive stale envelopes (> 30 days)
- [ ] T5.3: Add health check endpoint (`?action=health`) to both Edge Functions
- [ ] T5.4: Load test with synthetic envelopes (verify dedup under concurrency)
- [ ] T5.5: Document runbook for Socket Mode reconnection failures

---

## Acceptance Criteria

| Criterion | Verification |
|-----------|-------------|
| SSOT artifacts committed | `ssot/integrations/slack/pulser.yaml` exists |
| Secrets registered | All 5 Slack secrets in `ssot/secrets/registry.yaml` |
| Migration ready | `20260301000002_slack_envelopes.sql` applies cleanly |
| Contract documented | C-20 in `PLATFORM_CONTRACTS_INDEX.md` |
| Edge Functions deployed | `?action=health` returns `{ ok: true }` |
| Envelope deduplication works | Duplicate envelope_id produces no side effects |
| Notifications delivered | Platform event -> Slack message in < 5s |
| Slash commands respond | `/pulser health` returns within 3s |
