# Deployment Proofs: prod-20260109-2219

**Release Tag:** `prod-20260109-2219`
**Generated:** 2026-01-09T22:19:00Z

---

## Git State

| Field | Value |
|-------|-------|
| Branch | `main` |
| HEAD SHA | `6bbe81e9413c8036e1a826b80e3864d63c616c73` |
| Previous Tag | `prod-20260109-2217` |
| Previous SHA | `52c69e170875e896e30ff0a96b4bac93b461ac2b` |

### Diffstat

```
 SITEMAP.md                                   |   5 +-
 TREE.md                                      |  20 +-
 artifacts/supabase_verify/report.json        | 117 ++++
 docs/ops/SUPABASE_DEPLOYMENT_VERIFICATION.md | 200 ++++++
 scripts/verify_supabase_deploy.sh            | 970 +++++++++++++++++++++++++++
 5 files changed, 1306 insertions(+), 6 deletions(-)
```

---

## Links

| Resource | URL |
|----------|-----|
| GitHub Release | https://github.com/jgtolentino/odoo-ce/releases/tag/prod-20260109-2219 |
| Compare View | https://github.com/jgtolentino/odoo-ce/compare/prod-20260109-2217...prod-20260109-2219 |
| PR #191 | https://github.com/jgtolentino/odoo-ce/pull/191 |
| Commit 6bbe81e9 | https://github.com/jgtolentino/odoo-ce/commit/6bbe81e9413c8036e1a826b80e3864d63c616c73 |
| Commit d8bbeb13 | https://github.com/jgtolentino/odoo-ce/commit/d8bbeb1356b11a4fe805157da2164d404dee86fe |

---

## CI Proof

| Field | Status |
|-------|--------|
| Workflow Name | `Deploy to Production` |
| Workflow File | `.github/workflows/deploy-production.yml` |
| Run URL | UNVERIFIED - GitHub API not accessible |
| Run ID | UNVERIFIED |
| Status | UNVERIFIED |
| Artifacts | UNVERIFIED |

**Note:** GitHub API was not accessible during report generation. Workflow run details cannot be confirmed.

---

## Runtime Proof

### Docker Image

| Field | Value | Status |
|-------|-------|--------|
| Registry | `ghcr.io` | Expected per workflow |
| Image | `jgtolentino/odoo-ce` | Expected per workflow |
| Tag | `edge-standard` | Expected per workflow |
| Digest | - | UNVERIFIED |

### Service Health

| Endpoint | Status |
|----------|--------|
| `https://erp.insightpulseai.com/web/health` | UNVERIFIED |
| `http://localhost:8069/web/health` (internal) | UNVERIFIED |

---

## Container Proof

| Field | Status |
|-------|--------|
| Container Name | UNVERIFIED |
| Image Digest | UNVERIFIED |
| Container Status | UNVERIFIED |
| Last Logs | UNVERIFIED |

---

## Database Proof

| Field | Status | Notes |
|-------|--------|-------|
| Odoo DB Connectivity | UNVERIFIED | No DB changes in this release |
| Migration Status | N/A | No Odoo migrations |
| Supabase Migrations | N/A | No Supabase migrations in commit range |

---

## App Proof

| Check | Status |
|-------|--------|
| `/web/login` returns 200 | UNVERIFIED |
| `/web/health` returns 200 | UNVERIFIED |
| Version banner | UNVERIFIED |

---

## Verification Commands

To verify this deployment manually:

```bash
# 1. Check release exists
gh release view prod-20260109-2219

# 2. Compare commits
git log --oneline prod-20260109-2217..prod-20260109-2219

# 3. Check workflow runs
gh run list --workflow=deploy-production.yml --limit=5

# 4. Check production health (requires access)
curl -sf https://erp.insightpulseai.com/web/health

# 5. Check container status (requires SSH access)
ssh user@erp.insightpulseai.com 'docker compose ps'
```

---

## Evidence Files in This Directory

| File | Description | Status |
|------|-------------|--------|
| `README.md` | This file | Generated |
| `workflow_run.json` | Workflow run details | NOT AVAILABLE |
| `health_check.txt` | Health endpoint response | NOT AVAILABLE |
| `container_logs.txt` | Container startup logs | NOT AVAILABLE |
| `image_digest.txt` | Docker image digest | NOT AVAILABLE |

---

## Summary

This release (`prod-20260109-2219`) contains **documentation and tooling changes only**:

1. Added Supabase verification script and documentation
2. Auto-generated SITEMAP.md and TREE.md updates

**No runtime code changes** were deployed. The deployment workflow restarts containers with the same image (`edge-standard`), but no Odoo modules or Supabase artifacts changed.

---

*Proofs generated from git artifacts. Items marked UNVERIFIED require GitHub API or production server access.*
