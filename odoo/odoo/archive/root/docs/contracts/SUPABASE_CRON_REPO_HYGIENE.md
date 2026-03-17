# Supabase Cron — Nightly Repo Hygiene Contract

> **Scope**: Scheduled nightly repo health automation.
> Jobs run at **01:10 Asia/Manila** (17:10 UTC) via pg_cron → pg_net → Edge Function.
>
> Last updated: 2026-02-21

---

## 1. Purpose

This contract defines the nightly automated repository hygiene system:

- **What**: A scheduled suite of repo health checks covering P0 (fail-fast), P1 (drift), and P2 (governance) categories.
- **Why**: Catch repo structure violations, secret leaks, and SSOT drift before they reach production.
- **When**: Every night at 01:10 Asia/Manila (17:10 UTC), scheduled via pg_cron.
- **Where**: Results persist to `ops.repo_hygiene_*` tables in Supabase.

---

## 2. Architecture

```
pg_cron (ops_repo_hygiene_nightly)
  └── pg_net HTTP POST
        └── repo-hygiene-runner Edge Function
              ├── P0: root allowlist, secret scan, structure invariants
              ├── P1: evidence retention, OCA submodule pins, generated file drift
              ├── P2: workflow YAML lint, contract index sync
              └── INSERT → ops.repo_hygiene_runs / findings / artifacts
```

---

## 3. SSOT Sources

| Artifact | Path | Role |
|---------|------|------|
| Job definition | `automations/repo_hygiene/jobs/nightly.yml` | Check config, schedule, allowlists |
| Edge Function | `supabase/functions/repo-hygiene-runner/` | Execution logic |
| Schema migration | `supabase/migrations/20260221000003_ops_repo_hygiene.sql` | Tables + RLS |
| Schedule migration | `supabase/migrations/20260221000004_schedule_repo_hygiene_nightly.sql` | pg_cron registration |
| This contract | `docs/contracts/SUPABASE_CRON_REPO_HYGIENE.md` | Specification |

Dashboard-only cron edits are drift unless backported to migrations.

---

## 4. Schedule

| Field | Value |
|-------|-------|
| UTC cron expression | `10 17 * * *` |
| Manila time | 01:10 Asia/Manila |
| pg_cron job name | `ops_repo_hygiene_nightly` |
| Job name prefix | `ops_` (platform automation) |

---

## 5. Edge Function Contract

**Function**: `repo-hygiene-runner`
**URL**: `https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/repo-hygiene-runner`

**Actions**:

| Action | Auth | Method | Response |
|--------|------|--------|----------|
| `health` | None | GET | `{ ok: true, service, request_id }` |
| `run_nightly` | `x-bridge-secret` | POST | `{ ok, run_id, p0_passed, p1_warnings, p2_infos, total_checks, duration_ms }` |

**Error codes**: `UNAUTHORIZED | BAD_REQUEST | METHOD_NOT_ALLOWED | NOT_FOUND | SERVICE_ERROR | NOT_CONFIGURED`

---

## 6. Check Suite

### P0 — Critical (fail-fast, stop on any failure)

| Check ID | What | Authoritative Gate |
|---------|------|-------------------|
| `p0_root_allowlist` | Only approved top-level paths exist | `ssot-surface-guard.yml` CI |
| `p0_secret_scan` | No raw secrets in committed code | GitHub Advanced Security + pre-commit |
| `p0_structure_invariants` | No `ssot_violation` events in `ops.platform_events` last 24h | Supabase DB query |

### P1 — Warnings (report; escalate on threshold)

| Check ID | What | Threshold |
|---------|------|-----------|
| `p1_stale_branches` | Branches with last commit > 30 days, no open PR | — |
| `p1_evidence_retention` | Evidence bundles older than 90 days | Report only |
| `p1_oca_submodule_pins` | OCA submodules pinned (not floating HEAD) | — |
| `p1_generated_file_drift` | SSOT generators produce same output as committed files | `--dry-run` comparison |

### P2 — Governance (informational)

| Check ID | What |
|---------|------|
| `p2_workflow_yaml_lint` | All `.github/workflows/*.yml` are valid YAML |
| `p2_contract_index_sync` | Every `docs/contracts/` file in `PLATFORM_CONTRACTS_INDEX.md` |

---

## 7. Required Vault Secrets

Before applying `20260221000004_schedule_repo_hygiene_nightly.sql`:

| Vault key | Purpose |
|-----------|---------|
| `ops.cron.repo_hygiene_url` | Edge Function URL for cron invocations |
| `ops.cron.repo_hygiene_secret` | `x-bridge-secret` value |

Set via:
```sql
SELECT vault.create_secret(
  'https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/repo-hygiene-runner',
  'ops.cron.repo_hygiene_url',
  'repo-hygiene-runner Edge Function URL for cron invocations'
);
SELECT vault.create_secret(
  '<REPO_HYGIENE_SECRET_value>',
  'ops.cron.repo_hygiene_secret',
  'x-bridge-secret for repo-hygiene-runner cron invocations'
);
```

Also set Edge Function secret:
```bash
supabase secrets set --project-ref spdtwktxdalcfigzeqrz \
  REPO_HYGIENE_SECRET=<value>
```

---

## 8. Output Tables

| Table | Purpose |
|-------|---------|
| `ops.repo_hygiene_jobs` | Job registry (SSOT from nightly.yml) |
| `ops.repo_hygiene_runs` | One row per execution |
| `ops.repo_hygiene_findings` | Per-check results within a run |
| `ops.repo_hygiene_artifacts` | Report artifacts (optional) |

**RLS**: Authenticated users can SELECT; only `service_role` can INSERT/UPDATE/DELETE.

---

## 9. Monitoring Queries

```sql
-- Last 5 runs
SELECT run_at, completed_at, status, p0_passed, p1_warnings, duration_ms
FROM ops.repo_hygiene_runs
WHERE job_name = 'nightly'
ORDER BY run_at DESC
LIMIT 5;

-- Recent P0 failures
SELECT r.run_at, f.check_id, f.status, f.message
FROM ops.repo_hygiene_findings f
JOIN ops.repo_hygiene_runs r ON r.id = f.run_id
WHERE f.priority = 'p0' AND f.status = 'failed'
ORDER BY r.run_at DESC
LIMIT 20;

-- pg_cron history
SELECT jobname, start_time, end_time, status, return_message
FROM cron.job_run_details
WHERE jobname = 'ops_repo_hygiene_nightly'
ORDER BY start_time DESC
LIMIT 10;
```

---

## 10. Rollback

```sql
-- Disable without deleting
UPDATE cron.job SET active = false WHERE jobname = 'ops_repo_hygiene_nightly';

-- Remove permanently (requires backport migration to keep SSOT current)
SELECT cron.unschedule('ops_repo_hygiene_nightly');
```

---

## 11. Pre-Run Provisioning (migration-driven; no dashboard steps)

**Extensions**: `pg_cron` and `pg_net` are enabled by the schedule migration
(`CREATE EXTENSION IF NOT EXISTS`). If the Supabase plan does not permit these
extensions, the migration fails loudly — treat as a provisioning constraint,
not a manual step.

**Vault secrets** (names only; values are runtime provisioning — never committed):

```sql
-- Set via Supabase SQL editor or supabase-cli exec; values not stored in repo
SELECT vault.create_secret('<url>', 'ops.cron.repo_hygiene_url', 'repo-hygiene-runner URL');
SELECT vault.create_secret('<secret>', 'ops.cron.repo_hygiene_secret', 'x-bridge-secret');
```

**Edge Function secret** (names only; value is runtime provisioning):

```bash
supabase secrets set --project-ref spdtwktxdalcfigzeqrz REPO_HYGIENE_SECRET=<value>
```

**Apply migrations** (in order):
```bash
supabase db push  # or apply 000003 then 000004 via Supabase CLI
```

**Verify** (no dashboard required):
```bash
curl https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/repo-hygiene-runner?action=health
# Expected: {"ok":true,"service":"repo-hygiene-runner","request_id":"..."}
```

---

## 12. Related Docs

- `docs/contracts/SUPABASE_CRON_CONTRACT.md` — pg_cron SSOT rules
- `docs/contracts/SUPABASE_VAULT_CONTRACT.md` — Vault key naming convention
- `docs/contracts/SUPABASE_EDGE_FUNCTIONS_CONTRACT.md` — Edge Function limits
- `automations/repo_hygiene/jobs/nightly.yml` — SSOT check config
- `supabase/functions/repo-hygiene-runner/` — Implementation
