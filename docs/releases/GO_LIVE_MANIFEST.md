# Go-Live Manifest

> **Release:** prod-20260106-1741
> **Environment:** Production (erp.insightpulseai.com)
> **Generated:** 2026-01-06T18:07:00Z

---

## Deployment Identifiers

| Identifier | Value |
|------------|-------|
| **Release Tag** | `prod-20260106-1741` |
| **Commit SHA** | `782fea9a7a4656d6ba225fcbea132908978d1522` |
| **Deploy Workflow** | Deploy to Production #166 |
| **Deploy Time** | 2026-01-06T17:40:17Z |
| **Environment URL** | https://erp.insightpulseai.com |
| **Docker Image** | `ghcr.io/jgtolentino/odoo-ce:edge-standard` |
| **Previous Tag** | `prod-20260106-1643` |
| **Previous SHA** | `a42fc69f418ecb5744607749c5d544f88aae8a9d` |

---

## Pre-Deployment Gates

### Workflow Gates

| Gate | Status | Run |
|------|--------|-----|
| Pre-flight Checks | PASSED | Deploy #166, Job 1 |
| Image Verification | PASSED | Deploy #166, Step 4 |

### Quality Gates (from prior CI)

| Gate | Status | Notes |
|------|--------|-------|
| Module Production Gating | PASSED | Run #15 (782fea9) |
| All-Green Gates | ASSUMED | Triggered Deploy #166 |

---

## Deployment Checklist

### Code Deployment

- [x] Git pull on production server
- [x] Submodule update
- [x] Docker compose pull
- [x] Container recreate
- [x] Health check wait (30s)
- [x] Health endpoint verification

### Module Install/Upgrade

| Check | Status | Notes |
|-------|--------|-------|
| IPAI modules upgraded | **UNVERIFIED** | Deploy workflow doesn't run upgrade |
| OCA modules upgraded | **UNVERIFIED** | Deploy workflow doesn't run upgrade |
| Base module updated | **UNVERIFIED** | Deploy workflow doesn't run upgrade |

> **Note:** The "Deploy to Production" workflow performs git pull and docker recreate but does NOT execute Odoo module install/upgrade commands (`-u` or `-i` flags). Module state changes require the "Deploy Odoo Prod (upgrade module)" workflow, which **FAILED** (runs #24, #25).

### Database Migrations

| Check | Status |
|-------|--------|
| SQL migrations applied | N/A - No migrations in commit range |
| Data migrations applied | N/A - No migrations in commit range |

---

## Smoke Tests

| Test | Status | Notes |
|------|--------|-------|
| Service stability wait | PASSED | 60s delay |
| Health check | PASSED | Job completed |
| Production accessibility | PASSED | Workflow completed |

---

## Known Changes

### Shipped in This Release

| Category | Item | Status |
|----------|------|--------|
| **Spec** | `spec/ipai-ai-platform/` | NEW |
| **Tests** | `addons/ipai/ipai_ai_core/tests/` | NEW |
| **Docs** | IPAI AI Platform DBML, ERD, ORD | NEW |
| **Workflow** | `.github/workflows/diagrams.yml` | NEW |
| **Tool** | `tools/diagramflow/` | NEW |
| **API** | OpenAPI Workspace endpoints | UPDATED |
| **CI** | ipai-ai-platform-ci.yml | UPDATED |

### Known NOT Changed

| Category | Item | Reason |
|----------|------|--------|
| **Odoo Modules** | No manifest changes | Files unchanged |
| **OCA Dependencies** | No changes | manifest.yaml unchanged |
| **Database Schema** | No migrations | No SQL in commit range |
| **Seed Data** | No changes | db/seeds unchanged |
| **Environment Config** | No changes | .env.example unchanged |

---

## UNVERIFIED Section

The following items could not be verified from available evidence:

| Item | Evidence Gap | Mitigation |
|------|--------------|------------|
| Odoo module state | No upgrade logs | Check `/web/database/selector` or Odoo Apps |
| Docker container running | SSH output not captured | Check `docker ps` on server |
| Health endpoint response | Response body not captured | Manual curl to `/web/health` |
| Database connection | Not in workflow logs | Check Odoo logs on server |

---

## Rollback Plan

### Quick Rollback

```bash
# SSH to production server
ssh deploy@erp.insightpulseai.com

# Rollback to previous tag
cd /opt/odoo-ce
git fetch --tags
git checkout prod-20260106-1643

# Restart containers
docker compose pull
docker compose up -d --force-recreate

# Verify health
curl -sf http://localhost:8069/web/health
```

### Full Rollback (with database)

If data corruption suspected:

1. Stop Odoo container
2. Restore PostgreSQL from backup (if available)
3. Checkout previous tag
4. Restart containers
5. Verify data integrity

### Rollback Contacts

| Role | Contact |
|------|---------|
| DevOps Lead | @jgtolentino |
| Database Admin | TBD |
| Incident Response | TBD |

---

## Post-Deployment Verification

### Manual Checks Required

- [ ] Verify Odoo login works at https://erp.insightpulseai.com/web/login
- [ ] Check installed modules list matches expected
- [ ] Verify AI Platform features accessible (if any UI changes)
- [ ] Run manual smoke test on key workflows

### Automated Monitoring

| Monitor | URL/Command | Expected |
|---------|-------------|----------|
| Health endpoint | `GET /web/health` | 200 OK |
| Login page | `GET /web/login` | 200 OK |
| Container status | `docker ps` | Running |

---

## Release Notes

### PR #165: Upgrade React Fluent UI design system

**Summary:**
Production-ready React Fluent UI AI workspace with provider registry, thread persistence, workspace model for Notion-style organization, and RAG integration.

**Changes:**
- New spec kit bundle for IPAI AI Platform
- DBML schema and Mermaid ERD for data model visualization
- Object Relationship Document (ORD) with attribute definitions
- Enhanced OpenAPI spec with Workspaces endpoints
- Comprehensive unit tests for ipai_ai_core
- New DiagramFlow tool for diagram conversion

**Impact:** LOW - Primarily documentation, tests, and tooling. No Odoo module changes.

---

## Sign-Off

| Role | Name | Date | Status |
|------|------|------|--------|
| Deploy Author | GitHub Actions (automated) | 2026-01-06 | DEPLOYED |
| Release Verification | ReleaseBot | 2026-01-06 | VERIFIED |
| Manual QA | TBD | TBD | PENDING |
| Product Owner | TBD | TBD | PENDING |

---

## Links

| Resource | URL |
|----------|-----|
| Deploy Workflow | https://github.com/jgtolentino/odoo-ce/actions/runs/20756736863 |
| Release Tag | https://github.com/jgtolentino/odoo-ce/releases/tag/prod-20260106-1741 |
| PR #165 | https://github.com/jgtolentino/odoo-ce/pull/165 |
| Full Changelog | https://github.com/jgtolentino/odoo-ce/compare/prod-20260106-1643...prod-20260106-1741 |
| What Shipped (detailed) | [WHAT_SHIPPED.md](./WHAT_SHIPPED.md) |
| What Shipped (JSON) | [WHAT_SHIPPED.json](./WHAT_SHIPPED.json) |

---

*Generated by ReleaseBot for jgtolentino/odoo-ce*
