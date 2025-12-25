# WorkOS Production Deployment - Pre-Flight Checklist

**Target**: erp.insightpulseai.net
**Module**: WorkOS (Notion Clone for Odoo)
**Branch**: claude/notion-clone-odoo-module-LSFan (PR #89)

---

## Before Deployment

### Infrastructure Readiness

- [ ] SSH access to production server verified (`ssh deploy@erp.insightpulseai.net`)
- [ ] Sufficient disk space (>10% free on /opt/odoo-ce)
- [ ] Database backup directory exists (`/var/backups/odoo`)
- [ ] Log directory exists (`/var/log/odoo-deployment`)
- [ ] Docker containers running (`docker ps | grep odoo`)

### Code Readiness

- [ ] PR #89 reviewed and approved
- [ ] All tests passing in CI/CD
- [ ] Branch `claude/notion-clone-odoo-module-LSFan` merged from main (if required)
- [ ] No uncommitted local changes on production server
- [ ] Deployment scripts executable and tested

### Database Readiness

- [ ] PostgreSQL container healthy (`docker exec odoo-postgres psql -U odoo -c "SELECT 1"`)
- [ ] Database connection working (`docker exec odoo-accounting odoo -d odoo_accounting --test-enable`)
- [ ] Recent backup exists (< 24 hours old)
- [ ] Backup restoration tested successfully

### Network & Services

- [ ] Odoo web interface accessible (`https://erp.insightpulseai.net/web/login`)
- [ ] No active user sessions (or maintenance window scheduled)
- [ ] Reverse proxy / load balancer configured correctly
- [ ] SSL certificates valid (check expiry date)

### Rollback Preparation

- [ ] Rollback script tested (`scripts/prod/deploy_workos.sh --rollback`)
- [ ] Database backup retention policy confirmed
- [ ] Git branch protection rules understood
- [ ] Incident response team notified

---

## During Deployment

### Execution Checklist

- [ ] Deployment initiated by authorized user
- [ ] Deployment log location noted (`/var/log/odoo-deployment/workos_deploy_*.log`)
- [ ] Each phase completes without errors:
  - [ ] Phase 1: Pre-flight checks pass
  - [ ] Phase 2: Database backup created
  - [ ] Phase 3: Git sync completes
  - [ ] Phase 4: Module deployment succeeds
  - [ ] Phase 5: Verification passes
  - [ ] Phase 6: Artifacts committed
  - [ ] Phase 7: Manifest generated

### Real-Time Monitoring

- [ ] Monitor deployment logs: `tail -f /var/log/odoo-deployment/workos_deploy_*.log`
- [ ] Watch Odoo container logs: `docker logs -f odoo-accounting`
- [ ] Monitor PostgreSQL logs: `docker logs -f odoo-postgres`
- [ ] Check system resources: `htop` / `docker stats`

---

## After Deployment

### Verification Matrix

#### Module Installation

- [ ] Module `workos` visible in Apps list
- [ ] Module state = "installed" in database
- [ ] All module dependencies resolved
- [ ] No errors in Odoo server logs

#### Database Verification

- [ ] All database tables created (`SELECT * FROM information_schema.tables WHERE table_name LIKE 'workos%'`)
- [ ] All database triggers exist
- [ ] Row-level security (RLS) policies applied
- [ ] Database migrations completed successfully

#### HTTP Endpoints

- [ ] `/web/login` returns HTTP 200
- [ ] `/web` dashboard accessible
- [ ] `/workos` routes functional (if applicable)
- [ ] No 404 errors in access logs

#### Runtime Artifacts

- [ ] `docs/repo/REPO_SNAPSHOT.prod.json` generated
- [ ] `docs/runtime/0000_MENU_SITEMAP.json` created
- [ ] `docs/runtime/PROD_SNAPSHOT_MANIFEST.md` exists
- [ ] Artifacts committed to git

#### User Acceptance

- [ ] Admin can access WorkOS features
- [ ] Standard user permissions work correctly
- [ ] No JavaScript console errors
- [ ] Mobile responsive design intact

---

## Rollback Decision Matrix

| Condition | Severity | Action |
|-----------|----------|--------|
| Module install fails | High | Immediate rollback |
| Database migration errors | Critical | Immediate rollback + manual recovery |
| HTTP 500 errors on /web | Critical | Immediate rollback |
| Feature broken but Odoo stable | Medium | Document bug, deploy hotfix later |
| Performance degradation >20% | High | Rollback if affecting users |
| Visual/UX issues only | Low | Deploy hotfix in next cycle |

---

## Sign-Off

### Deployment Team

- [ ] **Initiated by**: ________________________ (Name)
- [ ] **Reviewed by**: ________________________ (Name)
- [ ] **Approved by**: ________________________ (Name)

### Deployment Outcome

- [ ] **Deployment Status**: ⬜ Success ⬜ Partial ⬜ Failed ⬜ Rolled Back
- [ ] **Start Time**: ________________________
- [ ] **End Time**: ________________________
- [ ] **Total Duration**: ________________________

### Post-Deployment Notes

```
[Record any issues, observations, or deviations from plan]




```

---

**Next Steps**: After successful deployment, update this checklist in git:

```bash
git add docs/deployment/PRE_FLIGHT_CHECKLIST.md
git commit -m "docs(deployment): mark pre-flight checklist complete"
git push origin claude/notion-clone-odoo-module-LSFan
```
