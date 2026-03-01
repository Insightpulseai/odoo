# Plan: Slack Pulser Integration

> Implementation plan for the Slack `pulser` app using Supabase-first architecture.
> Constitution: `spec/slack-pulser-integration/constitution.md`
> PRD: `spec/slack-pulser-integration/prd.md`

---

## Architecture Decision: Supabase-First

All Slack integration logic runs as Supabase Edge Functions. No standalone Node.js server or Docker container. This aligns with the platform's Supabase-first approach and avoids infrastructure sprawl.

**Trade-offs accepted**:
- Edge Functions have a 400s wall clock limit -- long-running Socket Mode connections require a keep-alive strategy or external process
- 256 MB memory limit -- sufficient for event routing, not for heavy computation
- Socket Mode requires a persistent WebSocket -- may need a lightweight external process (DO droplet systemd service) if Edge Functions cannot maintain persistent connections

**Fallback**: If Edge Functions cannot maintain persistent WebSocket connections (Deno Deploy limitation), the Socket Mode handler runs as a lightweight systemd service on the DO droplet, calling Edge Functions for business logic.

---

## Phases

### Phase 1: Foundation (SSOT + Migration + Contracts)

**Status**: In progress

1. Create `ssot/integrations/slack/pulser.yaml` -- app metadata
2. Register secrets in `ssot/secrets/registry.yaml`
3. Create `ops.slack_envelopes` migration
4. Write platform contract C-20
5. Create spec bundle

**Deliverables**: All SSOT artifacts committed, migration ready to apply.

### Phase 2: Edge Functions

1. Create `supabase/functions/ops-slack-bridge/` -- HTTP fallback endpoint
   - Signing secret verification
   - URL verification challenge handler
   - Event routing
   - Envelope deduplication via `ops.slack_envelopes`

2. Create `supabase/functions/ops-slack-socket/` -- Socket Mode handler
   - WebSocket connection management
   - Envelope acknowledgement (< 3s)
   - Event/interaction/command routing
   - Reconnection with exponential backoff

3. Shared utilities in `supabase/functions/_shared/slack/`:
   - `verify.ts` -- signing secret verification
   - `api.ts` -- Slack Web API client (chat.postMessage, etc.)
   - `blocks.ts` -- Block Kit message builders
   - `envelope.ts` -- envelope deduplication logic

**Deliverables**: Edge Functions deployed, health checks passing.

### Phase 3: Notification Routing

1. Define channel routing rules (event type -> channel mapping)
2. Implement Block Kit message templates for each notification type:
   - CI result (pass/fail with details)
   - Deployment status (started/completed/failed)
   - Error alert (with acknowledge button)
   - Task completion summary
3. Wire `ops.platform_events` inserts to Slack notifications via pg_cron + pg_net

**Deliverables**: Platform events automatically posted to correct Slack channels.

### Phase 4: Interactive Actions & Slash Commands

1. Implement action handler for message buttons (acknowledge, investigate, rollback)
2. Implement slash command handlers (`/pulser status`, `/pulser deploy`, `/pulser health`)
3. Add modal views for confirmation flows (e.g., deploy confirmation)
4. Wire action results back to original messages (update, not new message)

**Deliverables**: Full interactive Slack experience operational.

### Phase 5: Observability & Hardening

1. Add metrics: envelope processing latency, deduplication hit rate, reconnection count
2. Add stale envelope cleanup (pg_cron job, archive envelopes older than 30 days)
3. Add health check endpoint (`?action=health`) for both Edge Functions
4. Load test with synthetic envelopes

**Deliverables**: Production-ready with monitoring.

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Edge Functions cannot maintain persistent WSS | High | High | Fallback to DO droplet systemd service |
| Slack rate limits on high-volume events | Medium | Medium | Queue and batch notifications |
| Envelope table growth | Low | Low | pg_cron cleanup job (Phase 5) |
| Token rotation breaks connection | Low | Medium | Monitor refresh token expiry, alert |

---

## Dependencies (External)

| Dependency | Owner | Status |
|------------|-------|--------|
| Slack App `pulser` created | DevOps | Done (App ID: A0ABQ9BGYA3) |
| Slack App installed to workspace | DevOps | Pending |
| Supabase Vault secrets populated | DevOps | Pending |
| `ops.slack_envelopes` migration applied | DBA | Migration ready |
| `ops.platform_events` table exists | DBA | Active |
