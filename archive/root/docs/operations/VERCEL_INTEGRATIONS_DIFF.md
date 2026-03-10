# Vercel Integrations Diff Engine

Automated daily drift detector for Vercel team integrations.
Compares the two most recent integration snapshots and reports changes
via GitHub Issues and Slack.

---

## What It Checks

The diff engine compares `ops.integrations_snapshots` rows for each configured team
and detects:

| Change type | Description |
|-------------|-------------|
| **Added** | A new integration appeared since the last snapshot |
| **Removed** | An integration was deleted or uninstalled |
| **Changed** | An existing integration's fields changed (`name`, `slug`, `status`, `scopes`) |

---

## How It Works

```
Daily cron (08:00 UTC)
  → Fetch 2 latest snapshots per team (Supabase REST)
  → Compute diff (diff.ts)
  → Drift found?
      Yes → Open/update GitHub Issue + post Slack message
      No  → Close GitHub Issue (if open) + silent
```

### Snapshot capture
Snapshots are written to `ops.integrations_snapshots` by a separate Vercel webhook
or cron job that calls the Vercel API. The diff engine only reads; it does not
capture snapshots itself.

If `ops.integrations_snapshots` doesn't exist yet, apply:
`supabase/supabase/migrations/20260222000001_ops_integrations.sql`

---

## GitHub Issues

Each Vercel team gets one issue per repo. The issue is identified by a stable
HTML comment marker embedded in the body:

```
<!-- vercel-integrations-drift::TEAM_ID -->
```

- **Opened**: first time drift is detected for a team
- **Updated**: subsequent drift runs (body refreshed with latest diff)
- **Closed**: automatically when integrations return to expected state

Issues are created with labels: `ops`, `vercel`, `drift`.

---

## Suppressing False Positives

If an integration change is expected (e.g., a planned upgrade), resolve the
GitHub Issue manually with a comment explaining the change. The diff engine
will re-open it on the next run only if new drift is detected.

To permanently silence a specific rule, add the integration `slug` to
`IGNORED_INTEGRATION_SLUGS` in `platform/vercel-integrations/run.ts`.

---

## Configuration

| Env var | Required | Description |
|---------|----------|-------------|
| `VERCEL_API_TOKEN` | Yes | Vercel API token (team-scoped) |
| `SUPABASE_URL` | Yes | Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | Yes | Service role key (reads snapshots table) |
| `GH_TOKEN` | Yes | GitHub token with `issues:write` scope |
| `GH_REPO` | Yes | `owner/repo` format |
| `SLACK_WEBHOOK_URL` | No | Incoming webhook URL; skip for no Slack |
| `VERCEL_TEAM_IDS` | Yes | Comma-separated Vercel team IDs to monitor |

Set in GitHub Actions secrets for the scheduled CI workflow.

---

## Manual Run

```bash
# From repo root — requires env vars set locally
VERCEL_TEAM_IDS=team_abc123 \
SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co \
SUPABASE_SERVICE_ROLE_KEY=$SUPABASE_SERVICE_ROLE_KEY \
GH_TOKEN=$GH_TOKEN GH_REPO=Insightpulseai/odoo \
tsx platform/vercel-integrations/run.ts
```

---

## Source Files

| File | Purpose |
|------|---------|
| `platform/vercel-integrations/diff.ts` | Core diff logic (fetch + compare) |
| `platform/vercel-integrations/github_issues.ts` | Idempotent GitHub Issue manager |
| `platform/vercel-integrations/slack_notify.ts` | Slack webhook notification |
| `platform/vercel-integrations/run.ts` | Entry point (orchestrates the above) |
| `.github/workflows/vercel-integrations-diff.yml` | Daily cron CI workflow |

---

## Related Docs

| Doc | Purpose |
|-----|---------|
| `docs/ops/VERCEL_DOCS_SSOT.md` | Canonical Vercel docs URLs |
| `docs/ops/VERCEL_MONOREPO.md` | Vercel project setup and env vars |
| `docs/ops/OPS_ADVISOR.md` | Ops Advisor — broader platform health checks |
