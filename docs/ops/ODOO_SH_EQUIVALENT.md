# Odoo.sh-Equivalent Platform (OdooOps)

This document defines the architecture, workflows, and operational procedures for the **OdooOps** platform, providing a custom alternative to Odoo.sh for the **Insightpulseai** stack.

## Architecture SSOT

- **Repository**: `github.com/Insightpulseai/odoo` (The single source of truth for code and infra).
- **Control Plane**: GitHub Actions (Orchestration) + Ops Console (Visibility).
- **Data Plane**: DigitalOcean Droplets (Odoo Runtime) + Managed Postgres (Data).

## Workflow Matrix

| Event                 | Target Environment | Strategy                                            |
| :-------------------- | :----------------- | :-------------------------------------------------- |
| **Pull Request**      | Preflight Gate     | Lint, Tests, Allowlist & Risk-Tier checks.          |
| **Merge to main**     | Staging            | Auto-deploy latest `main` tag to staging droplet.   |
| **Release Tag (v\*)** | Production         | Approval-gated deployment with automated migration. |

## Environment Mapping (Vercel / Ops Console)

The `apps/ops-console/` Vercel deployment follows the same 3-tier promotion model as
Odoo.sh (dev → stage → prod), wired to GitHub events:

| Git event | GitHub Environment | Vercel tier | Supabase bucket prefix |
|-----------|-------------------|-------------|------------------------|
| Pull request | `preview` | Preview (ephemeral URL) | any (no constraint) |
| Push to `main` | `staging` | Staging | must start with `staging-` |
| Tag `v*` / `workflow_dispatch` | `production` | Production (`--prod`) | must start with `prod-` |

**Bucket prefix guard** — `scripts/ci/check_supabase_bucket_env.py` runs before every
non-preview deploy and blocks cross-env writes.  Exit codes: `0` OK · `1` prefix
mismatch (blocked) · `2` env var missing.

**Vercel function timeouts** (declared in `apps/ops-console/vercel.json`):

| Route | `maxDuration` | Rationale |
|-------|--------------|-----------|
| `app/api/ai/sql/route.ts` | 60 s | LLM inference |
| `app/api/secrets/sync/route.ts` | 300 s | Vault → Vercel env sync |
| `app/api/supabase-proxy/[...path]/route.ts` | 30 s | Supabase passthrough |

**Region:** `syd1` (Sydney).  Odoo stack is in SGP1 (DigitalOcean Singapore); consider
migrating to `sin1` if latency becomes a concern.

**Deployment workflow:** `.github/workflows/deploy-odooops-console.yml`

---

## Operational Procedures

### 1. Adding an OCA Addon (The Golden Path)

1. Add the OCA repository as a submodule in `addons/oca/repos/`.
2. Symlink the desired module into `addons/oca/selected/`.
3. Update the `allowlist.yaml` with the new module name.
4. Open a PR; verify the **Preflight Gate** passes.

### 2. Promoting Stage to Prod

1. Verify stability in the **Ops Console** (Health: Green).
2. Create a new GitHub Release/Tag (`v1.x.x`).
3. Approve the deployment in the GitHub Environments UI.
4. Monitor the **Production Healthcheck** output.

### 3. Triggering a Rollback

1. Open the **Rollback** workflow in GitHub Actions.
2. Select the target environment (`stage` or `prod`).
3. Enter the `previous_tag` (e.g., `v1.4.1`).
4. Execute; verify health in the Ops Console.
