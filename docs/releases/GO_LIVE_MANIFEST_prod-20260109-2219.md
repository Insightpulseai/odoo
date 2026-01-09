# Go-Live Manifest: prod-20260109-2219

**Release:** `prod-20260109-2219`
**Deployment Type:** Documentation / Tooling Only
**Production Impact:** Minimal (container restart only, no code changes)

---

## Pre-Deployment Checklist

| Check | Status | Notes |
|-------|--------|-------|
| Code freeze confirmed | N/A | Docs-only release |
| All CI gates passed | ASSUMED | Release tag created by workflow |
| Database backup taken | N/A | No DB changes |
| Rollback plan documented | N/A | No runtime changes to rollback |

---

## Deployment Verification

### Component Verification Matrix

| Component | Expected State | Actual State | Pass/Fail |
|-----------|---------------|--------------|-----------|
| Odoo Modules | No changes | No changes | PASS |
| Supabase Migrations | No changes | No changes | PASS |
| Supabase Functions | No changes | No changes | PASS |
| Docker Image | `edge-standard` | UNVERIFIED | UNVERIFIED |
| Workflow Completion | Success | UNVERIFIED | UNVERIFIED |

### Health Endpoints

| Endpoint | Expected | Actual | Status |
|----------|----------|--------|--------|
| `https://erp.insightpulseai.net/web/health` | 200 OK | - | UNVERIFIED |
| `https://erp.insightpulseai.net/web/login` | 200 OK | - | UNVERIFIED |

---

## What Shipped

### Code Changes

1. **PR #191: chore(ops): verify supabase deploy**
   - Added `scripts/verify_supabase_deploy.sh` - comprehensive Supabase verification script
   - Added `docs/ops/SUPABASE_DEPLOYMENT_VERIFICATION.md` - verification documentation
   - Added `artifacts/supabase_verify/report.json` - verification report template
   - **Impact:** Tooling only, no runtime changes

2. **Auto-generated docs update**
   - Updated `SITEMAP.md` and `TREE.md`
   - **Impact:** Documentation only

### Runtime Changes

| Change | Applied? | Evidence |
|--------|----------|----------|
| Docker containers restarted | UNVERIFIED | Per workflow: `docker compose up -d --force-recreate` |
| Odoo modules upgraded | NO | No `-u` flag in deployment script |
| Database migrations | NO | No Supabase migrations in commit range |

---

## Rollback Procedure

**Risk Level:** LOW - No runtime code changes deployed.

**If rollback needed:**
```bash
# This release contains only docs/tooling - no rollback needed
# If container issues occur, redeploy previous tag:
git checkout prod-20260109-2217
docker compose up -d --force-recreate
```

---

## Sign-Off

| Role | Name | Date | Status |
|------|------|------|--------|
| Release Manager | - | - | PENDING |
| QA | - | - | N/A (docs-only) |
| Ops | - | - | PENDING |

---

## Evidence Links

- **GitHub Release:** [prod-20260109-2219](https://github.com/jgtolentino/odoo-ce/releases/tag/prod-20260109-2219)
- **Compare View:** [prod-20260109-2217...prod-20260109-2219](https://github.com/jgtolentino/odoo-ce/compare/prod-20260109-2217...prod-20260109-2219)
- **PR #191:** [chore(ops): verify supabase deploy](https://github.com/jgtolentino/odoo-ce/pull/191)
- **Deployment Proofs:** [DEPLOYMENT_PROOFS/prod-20260109-2219/](./DEPLOYMENT_PROOFS/prod-20260109-2219/)

---

## Post-Deployment Tasks

- [ ] Run `./scripts/verify_supabase_deploy.sh` to populate verification results (requires Supabase credentials)
- [ ] Verify production health at `https://erp.insightpulseai.net/web/health`
- [ ] Update status in this manifest after verification

---

*Manifest generated: 2026-01-09T22:19:00Z*
