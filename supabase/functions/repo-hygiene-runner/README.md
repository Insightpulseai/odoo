# repo-hygiene-runner

Nightly repo hygiene Edge Function. Runs at 01:10 Asia/Manila (17:10 UTC)
via `ops_repo_hygiene_nightly` pg_cron job.

**Contract**: `docs/contracts/SUPABASE_CRON_REPO_HYGIENE.md`
**SSOT job config**: `automations/repo_hygiene/jobs/nightly.yml`

---

## Actions

| Action | Auth | Method | Description |
|--------|------|--------|-------------|
| `health` | None | GET | Liveness check |
| `run_nightly` | `x-bridge-secret` | POST | Execute nightly check suite |

## Required Env Vars

| Var | Description |
|-----|-------------|
| `REPO_HYGIENE_SECRET` | Shared secret for `x-bridge-secret` auth |
| `SUPABASE_URL` | Injected automatically by Supabase runtime |
| `SUPABASE_SERVICE_ROLE_KEY` | Injected automatically by Supabase runtime |

## Vault Secrets (pg_cron invocation)

| Vault key | Purpose |
|-----------|---------|
| `ops.cron.repo_hygiene_url` | Edge Function URL for cron |
| `ops.cron.repo_hygiene_secret` | `x-bridge-secret` value |

Set via:
```sql
SELECT vault.create_secret('<url>', 'ops.cron.repo_hygiene_url', 'repo-hygiene-runner Edge Function URL');
SELECT vault.create_secret('<secret>', 'ops.cron.repo_hygiene_secret', 'x-bridge-secret for repo-hygiene-runner');
```

## Health Check

```bash
curl https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/repo-hygiene-runner?action=health
# Expected: {"ok":true,"service":"repo-hygiene-runner","request_id":"..."}
```

## Output Tables

- `ops.repo_hygiene_runs` — one row per execution
- `ops.repo_hygiene_findings` — per-check results
- `ops.repo_hygiene_artifacts` — report artifacts

## Check Suite

| Check ID | Priority | What it verifies |
|---------|----------|-----------------|
| `p0_root_allowlist` | P0 | Root paths match allowlist in nightly.yml |
| `p0_secret_scan` | P0 | Secret scanning delegated to GitHub Advanced Security |
| `p0_structure_invariants` | P0 | No `ssot_violation` events in last 24h |
| `p1_evidence_retention` | P1 | Evidence bundles older than 90 days (informational) |
| `p2_contract_index_sync` | P2 | Contract index drift check was recent |
