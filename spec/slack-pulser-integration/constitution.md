# Constitution: Slack Pulser Integration

> Non-negotiable rules and constraints for the Slack `pulser` app integration.
> Contract: C-20 (`docs/contracts/SLACK_PULSER_CONTRACT.md`)

---

## Hard Constraints

1. **Socket Mode is the primary transport.** The integration uses Slack Socket Mode (WebSocket) as the default transport. HTTP endpoints are optional fallback only. Socket Mode avoids the need for a publicly routable URL.

2. **Signing secret verification is mandatory for HTTP mode.** Every HTTP request from Slack must be verified using HMAC-SHA256 with the signing secret. Requests with timestamps older than 5 minutes must be rejected (replay protection).

3. **Envelope idempotency is non-negotiable.** Every event envelope must be deduplicated using the `(team_id, envelope_id)` composite key in `ops.slack_envelopes` before any side effects execute. Insert-before-process, not process-then-record.

4. **Vault-only secrets.** All tokens and secrets (bot token, app-level token, signing secret, client secret, refresh token) are stored exclusively in Supabase Vault. Never in code, never in environment files committed to git, never logged.

5. **Acknowledge within 3 seconds.** Socket Mode envelopes must be acknowledged within 3 seconds of receipt. If the handler is slow, acknowledge first and process asynchronously.

6. **No Verification Token.** The legacy Verification Token is deprecated by Slack. Never use it for request verification. Use signing secret only.

7. **Supabase-first architecture.** All backend logic runs as Supabase Edge Functions. No standalone servers, no Docker containers for Slack handling. The Edge Function runtime constraints (256 MB memory, 400s wall clock) apply.

8. **Audit everything.** All processed events must be audited to `ops.platform_events`. All state changes must be traceable to a specific `envelope_id`.

9. **Least-privilege scopes.** Request only the minimum bot token scopes needed. Start with `chat:write`, `channels:read`, `commands`, `app_mentions:read`. Expand only when a specific feature requires it.

10. **No direct database writes from Slack handlers.** Slack event handlers may write to `ops.slack_envelopes` and `ops.platform_events` only. Any business logic that modifies Odoo data must go through the Odoo API or a dedicated bridge Edge Function.

---

## Boundaries

- **In scope**: Socket Mode connection, event routing, slash commands, interactive actions, ops notifications, idempotency ledger.
- **Out of scope**: Slack app distribution (single-workspace install only), Slack Enterprise Grid features, file uploads, Slack Connect (cross-org channels).

---

## Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| Supabase Edge Functions | Runtime | Active |
| Supabase Vault | Secret storage | Active |
| `ops.slack_envelopes` table | Idempotency | Migration ready |
| `ops.platform_events` table | Audit trail | Active |
| Slack API (api.slack.com) | External | Available |
