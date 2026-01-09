# What's Deployed: prod-20260109-2219

**Release Tag:** `prod-20260109-2219`
**Release Commit:** `6bbe81e9413c8036e1a826b80e3864d63c616c73`
**Previous Tag:** `prod-20260109-2217`
**Previous Commit:** `52c69e170875e896e30ff0a96b4bac93b461ac2b`
**Compare Range:** [`prod-20260109-2217..prod-20260109-2219`](https://github.com/jgtolentino/odoo-ce/compare/prod-20260109-2217...prod-20260109-2219)
**Report Generated:** 2026-01-09T22:19:00Z

---

## Executive Summary

| Component | Deployed? | Evidence |
|-----------|-----------|----------|
| Odoo (addons, modules) | NO | No changes in `addons/` - git diff shows 0 files |
| Supabase (migrations, functions) | NO | No changes in `supabase/` - git diff shows 0 files |
| Infra/Deploy (docker, services) | NO | No changes in `deploy/`, `docker/`, `services/` |
| CI/Workflows | NO | No changes in `.github/workflows/` |
| Docs/Scripts | YES | 5 files changed: verification tooling + docs |
| Docker Image | UNVERIFIED | Expected `ghcr.io/jgtolentino/odoo-ce:edge-standard` per workflow |
| Workflow Run | UNVERIFIED | GitHub API not accessible - cannot confirm run ID |

**Deployment Type:** Documentation and tooling only - no runtime changes.

---

## Changes Included

### Commits in Range (2 commits)

| Hash | Subject | Author | Date | PR |
|------|---------|--------|------|---|
| `6bbe81e9` | chore(ops): verify supabase deploy (migrations, hooks, edge functions) | jgtolentino | 2026-01-10T06:17:10+08:00 | [#191](https://github.com/jgtolentino/odoo-ce/pull/191) |
| `d8bbeb13` | docs: auto-update SITEMAP.md and TREE.md [skip ci] | github-actions[bot] | 2026-01-09T22:15:57Z | - |

### Files Changed (5 files, +1306/-6)

| Status | File | Category |
|--------|------|----------|
| M | `SITEMAP.md` | Docs-only |
| M | `TREE.md` | Docs-only |
| A | `artifacts/supabase_verify/report.json` | Other (verification tooling) |
| A | `docs/ops/SUPABASE_DEPLOYMENT_VERIFICATION.md` | Docs-only |
| A | `scripts/verify_supabase_deploy.sh` | Other (verification script) |

### Change Categorization

| Category | Files Changed | Lines |
|----------|---------------|-------|
| Odoo (addons/, odoo/, config/, patches/) | 0 | 0 |
| Supabase (supabase/migrations, supabase/functions) | 0 | 0 |
| Infra/Deploy (deploy/, services/, docker/) | 0 | 0 |
| CI/Workflows (.github/workflows) | 0 | 0 |
| Docs-only (docs/, *.md) | 4 | +225/-6 |
| Other (scripts, artifacts) | 1 | +1087/0 |

---

## Commits NOT Included (3 commits to main after this release)

These commits exist on `main` but are **NOT** part of this release:

| Hash | Subject | Author | Status |
|------|---------|--------|--------|
| `5b4a06b6` | docs: auto-update SITEMAP.md and TREE.md [skip ci] | github-actions[bot] | EXCLUDED |
| `32ce14e3` | chore(oca): add OCA-style chore scope conventions (#192) | - | EXCLUDED |
| `98165acf` | docs: auto-update SITEMAP.md and TREE.md [skip ci] | github-actions[bot] | EXCLUDED |

---

## Runtime Evidence

### Docker Image

| Field | Value | Status |
|-------|-------|--------|
| Registry | `ghcr.io` | Expected per workflow |
| Image | `jgtolentino/odoo-ce` | Expected per workflow |
| Tag | `edge-standard` | Expected per workflow |
| Digest (sha256) | - | UNVERIFIED - cannot access registry |

### Workflow Run

| Field | Value | Status |
|-------|-------|--------|
| Workflow Name | `Deploy to Production` | Per `.github/workflows/deploy-production.yml` |
| Run URL | - | UNVERIFIED - GitHub API not accessible |
| Run ID | - | UNVERIFIED |
| Environment | `production` | Per workflow |
| Target URL | `https://erp.insightpulseai.net` | Per workflow |
| Conclusion | - | UNVERIFIED |

### Deployment Steps (Expected per Workflow)

1. Pre-flight checks (verify image exists)
2. SSH to production server
3. `git fetch origin main && git checkout main && git pull origin main`
4. `git submodule update --init --recursive`
5. `docker compose pull`
6. `docker compose up -d --force-recreate`
7. Health check: `curl -sf http://localhost:8069/web/health`
8. Create release tag

---

## Supabase Status

**Supabase: NO CHANGES DEPLOYED**

**Proof:** `git diff --name-only prod-20260109-2217..prod-20260109-2219 -- supabase/` returns empty.

- No migrations added or modified
- No Edge Functions added or modified
- No config.toml changes

The commit `6bbe81e9` adds **verification tooling** (`scripts/verify_supabase_deploy.sh`) to audit existing Supabase deployments, but does NOT deploy any Supabase artifacts.

The `artifacts/supabase_verify/report.json` shows `"overall_status": "PENDING"` - it's a template awaiting actual verification runs.

---

## Odoo Status

**Odoo Modules: NO CHANGES DEPLOYED**

**Proof:** `git diff --name-only prod-20260109-2217..prod-20260109-2219 -- addons/` returns empty.

- No module code changes
- No manifest changes
- No migration scripts

**Runtime Restart:** UNVERIFIED

The deployment workflow runs `docker compose up -d --force-recreate` which restarts Odoo containers, but does NOT explicitly run:
- `-u all` (module upgrade)
- `--stop-after-init` (verification)

---

## Risks / Unknowns

| Item | Status | Missing Evidence |
|------|--------|------------------|
| Workflow run URL | UNVERIFIED | GitHub API not accessible to retrieve run ID |
| Docker image digest | UNVERIFIED | Cannot access container registry to verify sha256 |
| Production health check | UNVERIFIED | Cannot access `erp.insightpulseai.net/web/health` |
| Odoo service restart | UNVERIFIED | No logs from production deployment |
| Supabase verification results | PENDING | `verify_supabase_deploy.sh` has not been executed |

**Mitigation:** This release contains only documentation and verification tooling. No runtime artifacts were changed in the codebase. Any production runtime changes are limited to container restarts (same image).

---

## Evidence Files

- [GO_LIVE_MANIFEST_prod-20260109-2219.md](./GO_LIVE_MANIFEST_prod-20260109-2219.md)
- [WHAT_DEPLOYED_prod-20260109-2219.json](./WHAT_DEPLOYED_prod-20260109-2219.json)
- [DEPLOYMENT_PROOFS/prod-20260109-2219/README.md](./DEPLOYMENT_PROOFS/prod-20260109-2219/README.md)

---

*Report generated deterministically from git artifacts. UNVERIFIED items require GitHub API access or production server access to confirm.*
