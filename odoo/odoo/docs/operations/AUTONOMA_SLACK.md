# Autonoma Slack Integration Runbook
#
# SSOT:  ssot/qa/autonoma_slack.yaml
# Secrets: ssot/secrets/registry.yaml §autonoma_oauth_client_id
# Spec:  https://docs.autonoma.app/slack-integration
# Updated: 2026-03-02

## What the Autonoma Slack Bot Does

Autonoma's Slack bot provides real-time E2E test notifications:

| Notification Type | Content |
|-------------------|---------|
| Test result | Pass/fail status, execution time, affected components |
| Summary | Aggregate counts for scheduled runs, link to detailed report |
| Quick actions | Acknowledge / assign / dismiss failures inline in Slack |
| Commands | `/autonoma status`, `/autonoma run <suite>` from any channel |

**Security model**: OAuth 2.0 between Slack and Autonoma. Encrypted in transit and at rest. Granular permissions. Autonoma maintains audit logs.

---

## Channel Routing (per SSOT)

| Environment | Status | Channel | Format |
|-------------|--------|---------|--------|
| `production` | failed | `#ops-alerts` | Detailed (components + time + link) |
| `preview` | failed | `#dev-ci` | Compact (pass/fail + link) |
| any | scheduled daily | `#qa` | Summary aggregate |
| `production` | passed | `#ops-alerts` | Minimal ✅ line (disabled until first pass) |

Routing config: `ssot/qa/autonoma_slack.yaml §routing`

---

## Setup

### Prerequisites
- Autonoma account at `app.autonoma.app` with `insightpulseai/ops-console` project created
- Slack workspace admin access (to authorize OAuth app)

### Step 1: Install Autonoma Slack App

1. In Autonoma dashboard → Integrations → Slack → Connect
2. Authorize with your Slack workspace (`insightpulseai`)
3. Copy the OAuth client ID and client secret

### Step 2: Store secrets

```bash
# Store Autonoma OAuth credentials (not yet provisioned)
supabase secrets set AUTONOMA_OAUTH_CLIENT_ID=<client_id>
supabase secrets set AUTONOMA_OAUTH_CLIENT_SECRET=<client_secret>
```

These are tracked in `ssot/secrets/registry.yaml` with `status: not_provisioned`.

### Step 3: Configure channel routing

In Autonoma dashboard → Notifications → Slack:

- `production` failures → `#ops-alerts`
- `preview` failures → `#dev-ci`
- Daily scheduled → `#qa`
- Filter: E2E + smoke tests only

After configuring channels, update channel IDs in `ssot/qa/autonoma_slack.yaml §slack.channels`.

### Step 4: Test the integration

Send a test notification from Autonoma → Integrations → Slack → Send Test.

Check `#ops-alerts` for the test message.

---

## Troubleshooting

### Notifications not arriving

1. Verify Slack app is still authorized: Autonoma → Integrations → Slack → Status
2. Check channel IDs in SSOT match actual Slack channels
3. Check routing filter: `status: [failed]` — passes won't trigger unless `prod-pass` rule is enabled

### OAuth token expired

Re-authorize in Autonoma dashboard → Integrations → Slack → Reconnect.

---

## Convergence Integration (Future)

When `ssot/qa/autonoma_slack.yaml §convergence.enabled = true`:

- `ops-convergence-scan` checks that every Vercel production deployment has an Autonoma E2E result within 60 minutes
- Finding kind: `e2e_missing` → appears in ops-console `/overview` convergence card

To enable: update `convergence.enabled: true` and implement the convergence scan probe.

---

## Related

- `ssot/qa/autonoma_slack.yaml` — routing SSOT
- `ssot/secrets/registry.yaml` — Autonoma OAuth secrets
- `docs/runbooks/GITHUB_APP_PROVISIONING.md` — ops.webhook_events (convergence events)
- `ssot/errors/failure_modes.yaml` — failure mode codes
