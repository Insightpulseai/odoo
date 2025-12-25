# WorkOS Deployment Verification Matrix

**Purpose**: Comprehensive validation checklist for production deployment
**Target**: erp.insightpulseai.net
**Module**: WorkOS (Notion Clone for Odoo)

---

## Verification Levels

| Level | Description | Required For |
|-------|-------------|--------------|
| **L1** | Basic deployment success | All deployments |
| **L2** | Functional verification | Production deployments |
| **L3** | Performance & security | Production deployments |
| **L4** | User acceptance | Major releases |

---

## L1: Basic Deployment Success

### Git Verification

| Check | Command | Expected Result | Status |
|-------|---------|-----------------|--------|
| Branch deployed | `git branch --show-current` | `claude/notion-clone-odoo-module-LSFan` | ⬜ |
| Commit hash | `git rev-parse HEAD` | Matches deployment plan | ⬜ |
| No uncommitted changes | `git status` | Working tree clean | ⬜ |
| Remote synced | `git fetch && git status` | Up to date with origin | ⬜ |

### Database Verification

| Check | Command | Expected Result | Status |
|-------|---------|-----------------|--------|
| Backup created | `ls -lh /var/backups/odoo/odoo_accounting_*.sql.gz \| head -1` | Recent backup exists | ⬜ |
| Backup size valid | `stat -c%s <backup_file>` | > 1MB | ⬜ |
| Database accessible | `docker exec odoo-postgres psql -U odoo -c "SELECT 1"` | Returns 1 | ⬜ |
| No active locks | `SELECT * FROM pg_locks WHERE granted = false;` | 0 rows | ⬜ |

### Container Verification

| Check | Command | Expected Result | Status |
|-------|---------|-----------------|--------|
| Odoo container running | `docker ps \| grep odoo-accounting` | Status: Up | ⬜ |
| PostgreSQL container running | `docker ps \| grep odoo-postgres` | Status: Up | ⬜ |
| Container health | `docker inspect --format='{{.State.Health.Status}}' odoo-accounting` | healthy | ⬜ |
| No restart loops | `docker inspect --format='{{.RestartCount}}' odoo-accounting` | 0 | ⬜ |

### HTTP Endpoint Verification

| Endpoint | Expected HTTP Code | Expected Content | Status |
|----------|-------------------|------------------|--------|
| `/web/login` | 200 | Login form visible | ⬜ |
| `/web` | 200 or 303 | Dashboard or redirect | ⬜ |
| `/web/database/manager` | 200 | DB manager (if enabled) | ⬜ |

---

## L2: Functional Verification

### Module Installation

| Check | SQL Query | Expected Result | Status |
|-------|-----------|-----------------|--------|
| Module exists | `SELECT name, state FROM ir_module_module WHERE name = 'workos';` | state = 'installed' | ⬜ |
| Dependencies resolved | `SELECT d.name FROM ir_module_module_dependency d JOIN ir_module_module m ON d.module_id = m.id WHERE m.name = 'workos';` | All dependencies installed | ⬜ |
| No broken dependencies | `SELECT * FROM ir_module_module WHERE state = 'to install' OR state = 'to upgrade';` | 0 rows (or expected modules only) | ⬜ |

### Database Schema Verification

| Check | SQL Query | Expected Result | Status |
|-------|-----------|-----------------|--------|
| WorkOS tables exist | `SELECT COUNT(*) FROM information_schema.tables WHERE table_name LIKE 'workos%';` | > 0 | ⬜ |
| Indexes created | `SELECT COUNT(*) FROM pg_indexes WHERE tablename LIKE 'workos%';` | > 0 | ⬜ |
| Constraints exist | `SELECT COUNT(*) FROM information_schema.table_constraints WHERE table_name LIKE 'workos%';` | > 0 | ⬜ |
| Views created (if any) | `SELECT COUNT(*) FROM information_schema.views WHERE table_name LIKE 'workos%';` | Expected count | ⬜ |

### Menu & View Verification

| Check | SQL Query | Expected Result | Status |
|-------|-----------|-----------------|--------|
| Menus created | `SELECT name FROM ir_ui_menu WHERE name LIKE '%WorkOS%' OR name LIKE '%Notion%';` | WorkOS menu items exist | ⬜ |
| Views registered | `SELECT name, type FROM ir_ui_view WHERE name LIKE '%workos%';` | List, form, kanban views exist | ⬜ |
| Actions defined | `SELECT name FROM ir_actions_act_window WHERE res_model LIKE 'workos%';` | WorkOS actions registered | ⬜ |

### Security & Access Rights

| Check | SQL Query | Expected Result | Status |
|-------|-----------|-----------------|--------|
| Access rules exist | `SELECT name FROM ir_model_access WHERE model_id IN (SELECT id FROM ir_model WHERE model LIKE 'workos%');` | Access rules defined | ⬜ |
| Record rules exist | `SELECT name FROM ir_rule WHERE model_id IN (SELECT id FROM ir_model WHERE model LIKE 'workos%');` | RLS policies exist | ⬜ |
| Groups configured | `SELECT name FROM res_groups WHERE name LIKE '%WorkOS%';` | User groups created | ⬜ |

---

## L3: Performance & Security

### Performance Metrics

| Metric | Measurement | Threshold | Status |
|--------|-------------|-----------|--------|
| Login page load time | `curl -w "%{time_total}" https://erp.insightpulseai.net/web/login` | < 2 seconds | ⬜ |
| Dashboard load time | Manual browser test | < 3 seconds | ⬜ |
| Database query time | `EXPLAIN ANALYZE SELECT * FROM workos_* LIMIT 100;` | < 100ms | ⬜ |
| Memory usage | `docker stats odoo-accounting --no-stream` | < 80% | ⬜ |

### Security Validation

| Check | Method | Expected Result | Status |
|-------|--------|-----------------|--------|
| RLS enabled | `SELECT COUNT(*) FROM ir_rule WHERE model_id IN (SELECT id FROM ir_model WHERE model LIKE 'workos%');` | > 0 | ⬜ |
| SQL injection test | Attempt SQL injection in search fields | Request blocked | ⬜ |
| XSS test | Attempt XSS in text fields | Content escaped | ⬜ |
| CSRF protection | Check CSRF tokens in forms | Tokens present | ⬜ |
| HTTPS enforced | `curl -I http://erp.insightpulseai.net` | Redirect to HTTPS | ⬜ |

### Log Verification

| Log Type | Location | Check For | Status |
|----------|----------|-----------|--------|
| Odoo server logs | `docker logs odoo-accounting --tail=100` | No ERROR or CRITICAL | ⬜ |
| PostgreSQL logs | `docker logs odoo-postgres --tail=100` | No connection errors | ⬜ |
| Nginx logs | `/var/log/nginx/access.log` | No 500 errors | ⬜ |
| Deployment log | `/var/log/odoo-deployment/workos_deploy_*.log` | All phases completed | ⬜ |

---

## L4: User Acceptance Testing

### Admin User Tests

| Feature | Test Steps | Expected Result | Status |
|---------|-----------|-----------------|--------|
| Module visible | Login as admin → Apps → Search "WorkOS" | Module appears in list | ⬜ |
| Create workspace | Navigate to WorkOS → New Workspace | Workspace created | ⬜ |
| Create page | Open workspace → New Page | Page created | ⬜ |
| Edit page | Open page → Edit content → Save | Changes saved | ⬜ |
| Share workspace | Workspace → Share → Add user | User added | ⬜ |

### Standard User Tests

| Feature | Test Steps | Expected Result | Status |
|---------|-----------|-----------------|--------|
| View shared workspace | Login as user → WorkOS | Shared workspaces visible | ⬜ |
| Read-only permissions | Try to edit read-only page | Edit blocked | ⬜ |
| Edit allowed pages | Edit page with write permission | Changes saved | ⬜ |
| Search functionality | Search for content | Results returned | ⬜ |

### Mobile Responsiveness

| Device | Resolution | Test | Expected Result | Status |
|--------|-----------|------|-----------------|--------|
| Mobile (portrait) | 375×667 | Open WorkOS page | Layout responsive | ⬜ |
| Mobile (landscape) | 667×375 | Navigate workspace | No horizontal scroll | ⬜ |
| Tablet | 768×1024 | Create/edit page | Touch controls work | ⬜ |

### Browser Compatibility

| Browser | Version | Test | Expected Result | Status |
|---------|---------|------|-----------------|--------|
| Chrome | Latest | Full functionality | All features work | ⬜ |
| Firefox | Latest | Full functionality | All features work | ⬜ |
| Safari | Latest | Full functionality | All features work | ⬜ |
| Edge | Latest | Full functionality | All features work | ⬜ |

---

## Runtime Artifacts Verification

### Generated Files

| File | Location | Content Check | Status |
|------|----------|---------------|--------|
| Repository snapshot | `docs/repo/REPO_SNAPSHOT.prod.json` | Valid JSON, modules listed | ⬜ |
| Menu sitemap | `docs/runtime/0000_MENU_SITEMAP.json` | WorkOS menus present | ⬜ |
| HTTP sitemap | `docs/runtime/http_sitemap.json` | WorkOS routes mapped | ⬜ |
| Git state | `docs/repo/GIT_STATE.prod.txt` | Commit hash matches | ⬜ |
| Deployment manifest | `docs/runtime/PROD_SNAPSHOT_MANIFEST.md` | All sections completed | ⬜ |

### Git Commit Verification

| Check | Command | Expected Result | Status |
|-------|---------|-----------------|--------|
| Artifacts committed | `git log -1 --name-only` | Runtime artifacts in commit | ⬜ |
| Commit message | `git log -1 --oneline` | Contains timestamp & deployment info | ⬜ |
| Pushed to remote | `git log origin/claude/notion-clone-odoo-module-LSFan..HEAD` | No unpushed commits | ⬜ |

---

## Final Sign-Off

### Deployment Team

| Role | Name | Signature | Date/Time |
|------|------|-----------|-----------|
| **Deployed By** | | | |
| **Verified By** | | | |
| **Approved By** | | | |

### Overall Status

- [ ] **L1 - Basic Deployment**: ⬜ Pass ⬜ Fail
- [ ] **L2 - Functional**: ⬜ Pass ⬜ Fail
- [ ] **L3 - Performance & Security**: ⬜ Pass ⬜ Fail
- [ ] **L4 - User Acceptance**: ⬜ Pass ⬜ Fail

### Decision

- [ ] **APPROVED** - Deployment successful, no rollback needed
- [ ] **PARTIAL** - Minor issues, deploy hotfix in next cycle
- [ ] **ROLLBACK** - Critical issues, execute rollback procedure

### Notes

```
[Record any issues, observations, or deviations]




```

---

**Commands to Execute Verification**:

```bash
# Run full verification suite
cd /opt/odoo-ce
bash scripts/prod/verify_workos.sh

# Generate verification report
bash tools/audit/gen_verification_report.sh > docs/deployment/VERIFICATION_REPORT_$(date +%Y%m%d_%H%M%S).md

# Commit verification results
git add docs/deployment/VERIFICATION_REPORT_*.md
git commit -m "docs(deployment): verification results"
git push origin claude/notion-clone-odoo-module-LSFan
```
